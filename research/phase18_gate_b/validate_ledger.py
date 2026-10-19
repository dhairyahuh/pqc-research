#!/usr/bin/env python3
"""
validate_ledger.py — Phase 18J Gate B: Semantic Ledger Validator

Validates experimental campaign ledgers (JSON Lines) against the ratified
multi-fault experimental specification:
  - PHASE18G_IMPLEMENTATION_GATE_PLAN.md (§3.2 Gate B)
  - PHASE18F_FINAL_SPECIFICATION_AUDIT.md (§2 Ledger Validation)
  - PHASE17H_OPERATOR_RATIFICATION.md (§1.2 Quotas and Stratification)
  - PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md (Finding A: Two-Phase Logging & Seal)

Validation Invariants:
  1. Syntax & Delimitation: Valid UTF-8 JSON objects, strictly newline-terminated.
  2. Unique Trial Keys: Unique (master_seed_id, condition) keys, master_seed_id in [1, 420].
  3. Legal State Transitions: UNSEEN -> STARTED -> FINALIZED; sequential execution.
  4. Complete Scenario Coverage: Exactly 420 master scenarios x 4 conditions = 1,680 trials.
  5. Quota Stratum Enforcement:
       Q1: 300 active twiddle + CH_BIT
       Q2: 40 active twiddle (20 CH_DUP, 20 CH_REORDER)
       Q3: 60 active twiddle (15 CH_TRUNC, 15 CH_LOSS, 15 CH_DELAY, 15 CH_INTERRUPT)
       Q4: 20 controls (5 dormant-clean, 5 dormant-bit, 5 sham-clean, 5 sham-bit)
  6. Semantic Outcome Orthogonality:
       - No false-success: crashes/aborts CANNOT claim RESTORED_AND_VERIFIED.
       - No false-SDC: delivery blocks / crashes CANNOT claim DIFFERENT_OUTPUT (SDC).
  7. Non-Self-Referential Integrity Seal:
       - CAMPAIGN_SEAL record must be the terminal line.
       - content_sha256 strictly covers bytes 0..M-1 preceding the seal line.

Exit Codes:
  0: COMPLETE (All invariants passed, valid CAMPAIGN_SEAL verified)
  1: INVALID_LEDGER (Syntax error, structural anomaly, quota violation, seal corruption, false-success)
  2: PARTIAL_ABORTED (Valid syntax/states, but incomplete run < 1680 trials or interrupted crash)
  3: OPERATIONAL_ERROR (File not found, CLI usage error)
"""

import sys
import os
import json
import hashlib
import argparse
from typing import Dict, Any, List, Tuple, Set, Optional

# Constants matching ratified specification
TOTAL_MASTER_SCENARIOS = 420
TOTAL_TRIALS = 1680  # 420 * 4
CONDITIONS = ("C00", "C10", "C01", "C11")

QUOTA_1_COUNT = 300
QUOTA_2_COUNT = 40
QUOTA_3_COUNT = 60
QUOTA_4_COUNT = 20

QUOTA_2_SUBCLASSES = {"CH_DUP": 20, "CH_REORDER": 20}
QUOTA_3_SUBCLASSES = {"CH_TRUNC": 15, "CH_LOSS": 15, "CH_DELAY": 15, "CH_INTERRUPT": 15}
QUOTA_4_CONTROL_CELLS = {
    "CONTROL_DORMANT_CLEAN": 5,
    "CONTROL_DORMANT_BIT": 5,
    "CONTROL_SHAM_CLEAN": 5,
    "CONTROL_SHAM_BIT": 5
}

VALID_EXECUTION_STATUSES = {
    "ATTEMPTED_STARTED",
    "ATTEMPTED_COMPLETED",
    "SIGNAL_TERMINATION",
    "CRASH_SIGNAL",
    "ABNORMAL_PROCESS_EXIT",
    "PROTECT_ERROR",
    "RESTORATION_ERROR",
    "UNVERIFIED_PROCESS_ABORTED"
}

CRASH_ABORT_STATUSES = {
    "SIGNAL_TERMINATION",
    "CRASH_SIGNAL",
    "ABNORMAL_PROCESS_EXIT",
    "PROTECT_ERROR",
    "RESTORATION_ERROR",
    "UNVERIFIED_PROCESS_ABORTED"
}


class LedgerValidator:
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.verdict = "INVALID_LEDGER"
        self.exit_code = 1

        # State tracking
        self.raw_bytes = b""
        self.total_bytes = 0
        self.line_count = 0
        self.records: List[Dict[str, Any]] = []

        # Key state tracking: (master_seed_id, condition) -> "STARTED" | "FINALIZED"
        self.trial_states: Dict[Tuple[int, str], str] = {}
        self.start_records: Dict[Tuple[int, str], Dict[str, Any]] = {}
        self.finalize_records: Dict[Tuple[int, str], Dict[str, Any]] = {}

        # Scenario metadata: master_seed_id -> {quota_stratum, channel_class, control_cell, conditions_seen}
        self.scenario_meta: Dict[int, Dict[str, Any]] = {}

        # Seal tracking
        self.seal_record: Optional[Dict[str, Any]] = None
        self.seal_byte_offset: Optional[int] = None
        self.seal_covered_bytes_expected: Optional[int] = None

    def fail(self, msg: str):
        self.errors.append(msg)

    def validate(self) -> Tuple[str, int, Dict[str, Any]]:
        # 1. Read raw bytes from disk
        if not os.path.exists(self.ledger_path):
            self.fail(f"Ledger file not found: {self.ledger_path}")
            return "OPERATIONAL_ERROR", 3, self._summary()

        try:
            with open(self.ledger_path, "rb") as f:
                self.raw_bytes = f.read()
            self.total_bytes = len(self.raw_bytes)
        except Exception as e:
            self.fail(f"Failed to read ledger file: {str(e)}")
            return "OPERATIONAL_ERROR", 3, self._summary()

        if self.total_bytes == 0:
            self.fail("Ledger file is empty (0 bytes).")
            return "INVALID_LEDGER", 1, self._summary()

        # 2. Invariant 1: Syntax & Delimitation
        if not self.raw_bytes.endswith(b"\n"):
            self.fail("File does not terminate with a newline (\\n / 0x0A) — truncated write detected.")
            return "INVALID_LEDGER", 1, self._summary()

        # Split into raw lines keeping track of byte offsets
        raw_lines = self.raw_bytes.split(b"\n")
        # Remove trailing empty element caused by final \n
        if raw_lines and raw_lines[-1] == b"":
            raw_lines.pop()

        current_offset = 0
        currently_started_trial: Optional[Tuple[int, str]] = None
        has_seal = False
        is_partial_aborted_candidate = False

        for line_idx, line_bytes in enumerate(raw_lines):
            line_num = line_idx + 1
            line_len = len(line_bytes) + 1  # includes \n
            line_offset = current_offset
            current_offset += line_len

            # Decode UTF-8
            try:
                line_str = line_bytes.decode("utf-8")
            except UnicodeDecodeError as e:
                self.fail(f"Line {line_num}: UTF-8 decode error: {str(e)}")
                return "INVALID_LEDGER", 1, self._summary()

            # Parse JSON
            try:
                rec = json.loads(line_str)
            except json.JSONDecodeError as e:
                self.fail(f"Line {line_num}: Invalid JSON syntax: {str(e)}")
                return "INVALID_LEDGER", 1, self._summary()

            if not isinstance(rec, dict):
                self.fail(f"Line {line_num}: Record is not a JSON object.")
                return "INVALID_LEDGER", 1, self._summary()

            record_type = rec.get("record_type")
            if not record_type:
                self.fail(f"Line {line_num}: Missing required field 'record_type'.")
                return "INVALID_LEDGER", 1, self._summary()

            # Process by record_type
            if record_type == "CAMPAIGN_SEAL":
                if has_seal:
                    self.fail(f"Line {line_num}: Duplicate CAMPAIGN_SEAL detected.")
                    return "INVALID_LEDGER", 1, self._summary()
                if line_idx != len(raw_lines) - 1:
                    self.fail(f"Line {line_num}: CAMPAIGN_SEAL is not the terminal record (found at line {line_num} of {len(raw_lines)}).")
                    return "INVALID_LEDGER", 1, self._summary()

                has_seal = True
                self.seal_record = rec
                self.seal_byte_offset = line_offset
                continue

            if record_type not in ("START", "FINALIZE"):
                self.fail(f"Line {line_num}: Unknown record_type '{record_type}'.")
                return "INVALID_LEDGER", 1, self._summary()

            # Validate Trial Identifiers
            master_seed_id = rec.get("master_seed_id")
            condition = rec.get("condition")

            if not isinstance(master_seed_id, int) or master_seed_id < 1 or master_seed_id > TOTAL_MASTER_SCENARIOS:
                self.fail(f"Line {line_num}: Invalid master_seed_id '{master_seed_id}'. Must be int in [1, {TOTAL_MASTER_SCENARIOS}].")
                return "INVALID_LEDGER", 1, self._summary()

            if condition not in CONDITIONS:
                self.fail(f"Line {line_num}: Invalid condition '{condition}'. Must be one of {CONDITIONS}.")
                return "INVALID_LEDGER", 1, self._summary()

            trial_key = (master_seed_id, condition)

            # Invariant 3: State Progression & Transition
            if record_type == "START":
                # Check duplicate start
                if trial_key in self.trial_states:
                    prev_state = self.trial_states[trial_key]
                    self.fail(f"Line {line_num}: Duplicate START record for trial {trial_key} (previous state: {prev_state}).")
                    return "INVALID_LEDGER", 1, self._summary()

                # Check for dangling start from previous trial
                if currently_started_trial is not None:
                    self.fail(f"Line {line_num}: Trial {trial_key} started while previous trial {currently_started_trial} was not finalized (dangling start).")
                    is_partial_aborted_candidate = True
                    return "INVALID_LEDGER", 1, self._summary()

                self.trial_states[trial_key] = "STARTED"
                self.start_records[trial_key] = rec
                currently_started_trial = trial_key

                # Register scenario metadata
                self._record_scenario_meta(line_num, master_seed_id, condition, rec)

            elif record_type == "FINALIZE":
                # Check orphan finalize
                if trial_key not in self.trial_states or self.trial_states[trial_key] != "STARTED":
                    if trial_key not in self.trial_states:
                        self.fail(f"Line {line_num}: Orphan FINALIZE record for trial {trial_key} without preceding START.")
                    else:
                        self.fail(f"Line {line_num}: Duplicate FINALIZE record for trial {trial_key} (already FINALIZED).")
                    return "INVALID_LEDGER", 1, self._summary()

                # Check that finalized trial matches the currently started trial
                if currently_started_trial != trial_key:
                    self.fail(f"Line {line_num}: Finalize trial {trial_key} does not match currently open trial {currently_started_trial}.")
                    return "INVALID_LEDGER", 1, self._summary()

                self.trial_states[trial_key] = "FINALIZED"
                self.finalize_records[trial_key] = rec
                currently_started_trial = None

                # Invariant 6: Outcome Semantics & Non-False-Success Verification
                if not self._validate_outcome_semantics(line_num, trial_key, rec):
                    return "INVALID_LEDGER", 1, self._summary()

        # Check if the final record left an unclosed dangling start
        if currently_started_trial is not None:
            self.fail(f"Ledger ends with unfinalized trial {currently_started_trial} (dangling start followed by EOF).")
            # This is a classic crash anomaly without seal
            if not has_seal:
                self.verdict = "PARTIAL_ABORTED"
                self.exit_code = 2
                return self.verdict, self.exit_code, self._summary()
            else:
                return "INVALID_LEDGER", 1, self._summary()

        # 3. Invariant 4: Scenario and Condition Coverage
        finalized_count = len(self.finalize_records)
        scenarios_present = set(k[0] for k in self.finalize_records.keys())

        # Check for missing conditions within observed scenarios
        missing_conditions_found = False
        for sid in scenarios_present:
            for cond in CONDITIONS:
                if (sid, cond) not in self.finalize_records:
                    self.fail(f"Scenario {sid} is missing condition record '{cond}'.")
                    missing_conditions_found = True

        if missing_conditions_found:
            if not has_seal:
                self.verdict = "PARTIAL_ABORTED"
                self.exit_code = 2
                return self.verdict, self.exit_code, self._summary()
            else:
                return "INVALID_LEDGER", 1, self._summary()

        # 4. Check if trial count is less than 1,680
        if finalized_count < TOTAL_TRIALS:
            if not has_seal:
                self.verdict = "PARTIAL_ABORTED"
                self.exit_code = 2
                return self.verdict, self.exit_code, self._summary()
            else:
                self.fail(f"CAMPAIGN_SEAL present but finalized trial count ({finalized_count}) < {TOTAL_TRIALS}.")
                return "INVALID_LEDGER", 1, self._summary()

        if finalized_count > TOTAL_TRIALS:
            self.fail(f"Finalized trial count ({finalized_count}) exceeds expected {TOTAL_TRIALS}.")
            return "INVALID_LEDGER", 1, self._summary()

        # Check total scenario count == 420
        if len(scenarios_present) != TOTAL_MASTER_SCENARIOS:
            self.fail(f"Distinct scenario count ({len(scenarios_present)}) != {TOTAL_MASTER_SCENARIOS}.")
            return "INVALID_LEDGER", 1, self._summary()

        # 5. Invariant 5: Quota Stratum Enforcement
        if not self._validate_quotas():
            return "INVALID_LEDGER", 1, self._summary()

        # 6. Invariant 7: CAMPAIGN_SEAL Integrity Verification
        if not has_seal or self.seal_record is None:
            self.fail("All 1,680 trials finalized, but mandatory CAMPAIGN_SEAL is missing.")
            return "INVALID_LEDGER", 1, self._summary()

        if not self._validate_seal():
            return "INVALID_LEDGER", 1, self._summary()

        # All checks passed!
        self.verdict = "COMPLETE"
        self.exit_code = 0
        return self.verdict, self.exit_code, self._summary()

    def _record_scenario_meta(self, line_num: int, sid: int, cond: str, rec: Dict[str, Any]):
        quota_stratum = rec.get("quota_stratum")
        channel_class = rec.get("channel_class")
        control_cell = rec.get("control_cell")

        if sid not in self.scenario_meta:
            self.scenario_meta[sid] = {
                "quota_stratum": quota_stratum,
                "channel_classes": {},
                "control_cell": control_cell
            }

        meta = self.scenario_meta[sid]
        # Verify consistent quota_stratum across conditions
        if meta["quota_stratum"] != quota_stratum:
            self.fail(f"Line {line_num}: Scenario {sid} condition {cond} has quota_stratum '{quota_stratum}', diverging from prior '{meta['quota_stratum']}'.")

        meta["channel_classes"][cond] = channel_class
        if control_cell and meta["control_cell"] is None:
            meta["control_cell"] = control_cell

    def _validate_outcome_semantics(self, line_num: int, trial_key: Tuple[int, str], rec: Dict[str, Any]) -> bool:
        sid, cond = trial_key
        exec_status = rec.get("execution_status")
        proto_outcome = rec.get("protocol_outcome")
        crypto_endpoint = rec.get("crypto_endpoint")
        restoration_status = rec.get("restoration_status")
        output_ss_hex = rec.get("output_ss_hex")

        if exec_status not in VALID_EXECUTION_STATUSES:
            self.fail(f"Line {line_num}: Trial {trial_key} has invalid execution_status '{exec_status}'.")
            return False

        # Rule S1: No False Restoration on Abort/Crash
        if exec_status in CRASH_ABORT_STATUSES:
            if restoration_status == "RESTORED_AND_VERIFIED":
                self.fail(f"Line {line_num}: False-success violation: Trial {trial_key} aborted with '{exec_status}' but claims restoration_status 'RESTORED_AND_VERIFIED'.")
                return False

        # Rule S2: No False SDC on Crash/Abort
        if exec_status in CRASH_ABORT_STATUSES:
            if crypto_endpoint == "DIFFERENT_OUTPUT":
                self.fail(f"Line {line_num}: False-SDC violation: Trial {trial_key} aborted with '{exec_status}' but claims crypto_endpoint 'DIFFERENT_OUTPUT' (SDC).")
                return False

        # Rule S3: Successful protocol outcome requires output_ss_hex
        if proto_outcome in ("KEY_ESTABLISHED", "RECOVERED_ON_RETRY"):
            if not output_ss_hex or len(output_ss_hex) != 64:
                self.fail(f"Line {line_num}: Trial {trial_key} established key ('{proto_outcome}') but output_ss_hex is invalid or missing.")
                return False
            if crypto_endpoint and crypto_endpoint.startswith("NOT_EVALUATED"):
                self.fail(f"Line {line_num}: Trial {trial_key} established key but crypto_endpoint is '{crypto_endpoint}'.")
                return False

        # Rule S4: Normal completed trials on C10/C11 must verify restoration
        if cond in ("C10", "C11") and exec_status == "ATTEMPTED_COMPLETED":
            if restoration_status != "RESTORED_AND_VERIFIED":
                self.fail(f"Line {line_num}: Completed trial {trial_key} on mutated condition '{cond}' must have restoration_status 'RESTORED_AND_VERIFIED' (got '{restoration_status}').")
                return False

        return True

    def _validate_quotas(self) -> bool:
        q1_sids = []
        q2_sids = []
        q3_sids = []
        q4_sids = []

        q2_counts = {"CH_DUP": 0, "CH_REORDER": 0}
        q3_counts = {"CH_TRUNC": 0, "CH_LOSS": 0, "CH_DELAY": 0, "CH_INTERRUPT": 0}
        q4_counts = {cell: 0 for cell in QUOTA_4_CONTROL_CELLS}

        for sid, meta in self.scenario_meta.items():
            q = meta["quota_stratum"]
            ch_active = meta["channel_classes"].get("C01") or meta["channel_classes"].get("C11")

            if q == "QUOTA_1_ADMITTED_CORRUPTED":
                q1_sids.append(sid)
                if ch_active != "CH_BIT":
                    self.fail(f"Scenario {sid} in Quota 1 must have active channel CH_BIT (got '{ch_active}').")
                    return False

            elif q == "QUOTA_2_ADMITTED_CLEAN":
                q2_sids.append(sid)
                if ch_active not in QUOTA_2_SUBCLASSES:
                    self.fail(f"Scenario {sid} in Quota 2 has invalid channel class '{ch_active}'.")
                    return False
                q2_counts[ch_active] += 1

            elif q == "QUOTA_3_DELIVERY_BLOCKING":
                q3_sids.append(sid)
                if ch_active not in QUOTA_3_SUBCLASSES:
                    self.fail(f"Scenario {sid} in Quota 3 has invalid channel class '{ch_active}'.")
                    return False
                q3_counts[ch_active] += 1

            elif q == "QUOTA_4_NEGATIVE_CONTROL":
                q4_sids.append(sid)
                cell = meta.get("control_cell")
                if cell not in QUOTA_4_CONTROL_CELLS:
                    self.fail(f"Scenario {sid} in Quota 4 has unknown control_cell '{cell}'.")
                    return False
                q4_counts[cell] += 1

            else:
                self.fail(f"Scenario {sid} has unknown quota_stratum '{q}'.")
                return False

        # Validate total counts
        if len(q1_sids) != QUOTA_1_COUNT:
            self.fail(f"Quota 1 scenario count ({len(q1_sids)}) != expected {QUOTA_1_COUNT}.")
            return False

        if len(q2_sids) != QUOTA_2_COUNT:
            self.fail(f"Quota 2 scenario count ({len(q2_sids)}) != expected {QUOTA_2_COUNT}.")
            return False
        for ch, expected in QUOTA_2_SUBCLASSES.items():
            if q2_counts[ch] != expected:
                self.fail(f"Quota 2 subclass '{ch}' count ({q2_counts[ch]}) != expected {expected}.")
                return False

        if len(q3_sids) != QUOTA_3_COUNT:
            self.fail(f"Quota 3 scenario count ({len(q3_sids)}) != expected {QUOTA_3_COUNT}.")
            return False
        for ch, expected in QUOTA_3_SUBCLASSES.items():
            if q3_counts[ch] != expected:
                self.fail(f"Quota 3 subclass '{ch}' count ({q3_counts[ch]}) != expected {expected}.")
                return False

        if len(q4_sids) != QUOTA_4_COUNT:
            self.fail(f"Quota 4 scenario count ({len(q4_sids)}) != expected {QUOTA_4_COUNT}.")
            return False
        for cell, expected in QUOTA_4_CONTROL_CELLS.items():
            if q4_counts[cell] != expected:
                self.fail(f"Quota 4 control cell '{cell}' count ({q4_counts[cell]}) != expected {expected}.")
                return False

        return True

    def _validate_seal(self) -> bool:
        seal = self.seal_record
        if not seal:
            self.fail("CAMPAIGN_SEAL record is missing.")
            return False

        status = seal.get("status")
        trial_count = seal.get("trial_count")
        covered_bytes = seal.get("covered_bytes")
        content_sha256 = seal.get("content_sha256")

        if status != "COMPLETE":
            self.fail(f"CAMPAIGN_SEAL status is '{status}', expected 'COMPLETE'.")
            return False

        if trial_count != TOTAL_TRIALS:
            self.fail(f"CAMPAIGN_SEAL trial_count ({trial_count}) != expected {TOTAL_TRIALS}.")
            return False

        if covered_bytes != self.seal_byte_offset:
            self.fail(f"CAMPAIGN_SEAL covered_bytes ({covered_bytes}) does not match actual pre-seal offset ({self.seal_byte_offset}).")
            return False

        if not content_sha256 or len(content_sha256) != 64:
            self.fail(f"CAMPAIGN_SEAL content_sha256 is malformed (length {len(str(content_sha256))}).")
            return False

        # Non-Self-Referential Hash Verification over bytes 0..M-1
        pre_seal_bytes = self.raw_bytes[:covered_bytes]
        actual_hash = hashlib.sha256(pre_seal_bytes).hexdigest()

        if actual_hash.lower() != content_sha256.lower():
            self.fail(f"CAMPAIGN_SEAL SHA-256 hash mismatch! Seal claims '{content_sha256}', recomputed '{actual_hash}'.")
            return False

        return True

    def _summary(self) -> Dict[str, Any]:
        return {
            "ledger_path": self.ledger_path,
            "verdict": self.verdict,
            "exit_code": self.exit_code,
            "total_bytes": self.total_bytes,
            "finalized_trials": len(self.finalize_records),
            "total_master_scenarios": len(self.scenario_meta),
            "errors": self.errors,
            "warnings": self.warnings
        }


def main():
    parser = argparse.ArgumentParser(description="Phase 18J Gate B Semantic Ledger Validator")
    parser.add_argument("ledger_path", help="Path to campaign_ledger.jsonl")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON summary")
    args = parser.parse_args()

    validator = LedgerValidator(args.ledger_path)
    verdict, exit_code, summary = validator.validate()

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"=== Ledger Validation: {args.ledger_path} ===")
        print(f"Verdict:   {verdict} (Exit Code: {exit_code})")
        print(f"Trials:    {summary['finalized_trials']} / {TOTAL_TRIALS} finalized")
        print(f"Scenarios: {summary['total_master_scenarios']} / {TOTAL_MASTER_SCENARIOS} master scenarios")
        if summary["errors"]:
            print(f"\nErrors ({len(summary['errors'])}):")
            for err in summary["errors"]:
                print(f"  [!] {err}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
