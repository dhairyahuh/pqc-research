#!/usr/bin/env python3
"""
test_validator.py — Phase 18J Gate B Test Suite Runner

Executes validate_ledger.py on all synthetic fixtures in fixtures/ and verifies:
  1. Exact exit codes (0, 1, 2)
  2. Exact verdict strings (COMPLETE, INVALID_LEDGER, PARTIAL_ABORTED)
  3. Diagnostic error reporting matches expected invariant failures
  4. Non-circular, deterministic validation

Generates:
  - research/phase18_gate_b/gate_b_validator_report.json
  - research/results/phase18_gates/gate_b_validator_report.json
"""

import os
import sys
import json
import subprocess
import time
import hashlib
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
VALIDATOR_SCRIPT = os.path.join(BASE_DIR, "validate_ledger.py")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "research", "results", "phase18_gates")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Test definitions: (fixture_name, expected_verdict, expected_exit_code, expected_error_substring)
TEST_SPECS = [
    {
        "test_id": "TEST_01_VALID_COMPLETE",
        "category": "Valid complete ledger",
        "fixture_name": "fixture_valid_complete.jsonl",
        "expected_verdict": "COMPLETE",
        "expected_exit_code": 0,
        "expected_error_substr": None,
        "description": "Full 1,680 trial campaign with valid quotas, lifecycles, and CAMPAIGN_SEAL."
    },
    {
        "test_id": "TEST_02_MISSING_CONDITION",
        "category": "Missing condition",
        "fixture_name": "fixture_missing_condition.jsonl",
        "expected_verdict": "PARTIAL_ABORTED",
        "expected_exit_code": 2,
        "expected_error_substr": "Scenario 45 is missing condition record 'C11'",
        "description": "Scenario 45 missing condition C11 without seal; correctly identified as incomplete/aborted run."
    },
    {
        "test_id": "TEST_03_DUPLICATE_KEY",
        "category": "Duplicate key",
        "fixture_name": "fixture_duplicate_start.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "Duplicate START record for trial (12, 'C11')",
        "description": "Duplicate START record for trial (12, C11); rejected as duplicate key."
    },
    {
        "test_id": "TEST_04_INVALID_LIFECYCLE",
        "category": "Invalid lifecycle",
        "fixture_name": "fixture_orphan_finalize.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "Orphan FINALIZE record for trial (1, 'C00') without preceding START",
        "description": "FINALIZE record emitted without preceding START; rejected as orphan finalize."
    },
    {
        "test_id": "TEST_05_QUOTA_VIOLATION",
        "category": "Quota violation",
        "fixture_name": "fixture_quota_violation.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "Quota 1 scenario count (299) != expected 300",
        "description": "Scenario 300 shifted from Quota 1 to Quota 2; rejected as quota allocation mismatch."
    },
    {
        "test_id": "TEST_06_SEAL_TAMPERING_HASH",
        "category": "Seal tampering",
        "fixture_name": "fixture_corrupted_seal.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "CAMPAIGN_SEAL SHA-256 hash mismatch",
        "description": "content_sha256 in CAMPAIGN_SEAL has 1 flipped character; rejected as seal mismatch."
    },
    {
        "test_id": "TEST_07_SEAL_TAMPERING_PAYLOAD",
        "category": "Seal tampering",
        "fixture_name": "fixture_tampered_payload.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "CAMPAIGN_SEAL SHA-256 hash mismatch",
        "description": "Covered payload byte modified while seal unchanged; rejected as seal mismatch."
    },
    {
        "test_id": "TEST_08_FALSE_SUCCESS_SEMANTICS",
        "category": "False-success semantics",
        "fixture_name": "fixture_false_success_semantics.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "False-success violation: Trial (10, 'C10') aborted with 'SIGNAL_TERMINATION' but claims restoration_status 'RESTORED_AND_VERIFIED'",
        "description": "Aborted trial falsely claiming clean table restoration; rejected by semantic orthogonality rule."
    },
    {
        "test_id": "TEST_09_MISSING_SEAL",
        "category": "Missing or malformed seal",
        "fixture_name": "fixture_missing_seal.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "All 1,680 trials finalized, but mandatory CAMPAIGN_SEAL is missing",
        "description": "Complete 1,680 trials but missing terminal CAMPAIGN_SEAL record; rejected."
    },
    {
        "test_id": "TEST_10_TRUNCATED_WRITE",
        "category": "Syntax & delimitation anomaly",
        "fixture_name": "fixture_truncated_write.jsonl",
        "expected_verdict": "INVALID_LEDGER",
        "expected_exit_code": 1,
        "expected_error_substr": "File does not terminate with a newline (\\n / 0x0A) — truncated write detected",
        "description": "File abruptly cut off mid-line without trailing newline; rejected as truncated write."
    },
    {
        "test_id": "TEST_11_DANGLING_START",
        "category": "Lifecycle crash anomaly",
        "fixture_name": "fixture_dangling_start.jsonl",
        "expected_verdict": "PARTIAL_ABORTED",
        "expected_exit_code": 2,
        "expected_error_substr": "Ledger ends with unfinalized trial (50, 'C00') (dangling start followed by EOF)",
        "description": "Trial started followed by immediate EOF; correctly classified as crashed/aborted run."
    }
]


def run_test(spec: Dict[str, Any]) -> Dict[str, Any]:
    fixture_path = os.path.join(FIXTURES_DIR, spec["fixture_name"])
    if not os.path.exists(fixture_path):
        return {
            "test_id": spec["test_id"],
            "fixture": spec["fixture_name"],
            "status": "FAILED",
            "reason": f"Fixture file not found: {fixture_path}"
        }

    # Compute fixture file SHA-256
    with open(fixture_path, "rb") as f:
        file_bytes = f.read()
    fixture_sha256 = hashlib.sha256(file_bytes).hexdigest()
    file_size = len(file_bytes)

    # Execute validator via subprocess with --json
    cmd = [sys.executable, VALIDATOR_SCRIPT, fixture_path, "--json"]
    t0 = time.perf_counter()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration_sec = time.perf_counter() - t0

    actual_exit_code = res.returncode
    stdout_text = res.stdout.strip()
    stderr_text = res.stderr.strip()

    try:
        summary_json = json.loads(stdout_text)
        actual_verdict = summary_json.get("verdict")
        actual_errors = summary_json.get("errors", [])
    except Exception as e:
        actual_verdict = "PARSING_ERROR"
        actual_errors = [f"Failed to parse validator JSON output: {str(e)}", stdout_text]

    # Evaluate assertions
    exit_code_ok = (actual_exit_code == spec["expected_exit_code"])
    verdict_ok = (actual_verdict == spec["expected_verdict"])
    error_substr_ok = True
    if spec["expected_error_substr"]:
        error_substr_ok = any(spec["expected_error_substr"] in err for err in actual_errors)

    passed = exit_code_ok and verdict_ok and error_substr_ok

    return {
        "test_id": spec["test_id"],
        "category": spec["category"],
        "fixture_name": spec["fixture_name"],
        "fixture_bytes": file_size,
        "fixture_sha256": fixture_sha256,
        "description": spec["description"],
        "expected_exit_code": spec["expected_exit_code"],
        "actual_exit_code": actual_exit_code,
        "expected_verdict": spec["expected_verdict"],
        "actual_verdict": actual_verdict,
        "expected_error_substr": spec["expected_error_substr"],
        "matched_error": error_substr_ok,
        "duration_sec": round(duration_sec, 4),
        "errors_reported": actual_errors,
        "test_passed": passed
    }


def main():
    print("=" * 70)
    print(" PHASE 18J GATE B: SEMANTIC LEDGER VALIDATOR TEST SUITE")
    print("=" * 70)
    print(f"Validator script: {VALIDATOR_SCRIPT}")
    print(f"Fixtures dir:     {FIXTURES_DIR}")
    print(f"Total test cases: {len(TEST_SPECS)}\n")

    results = []
    all_passed = True

    for spec in TEST_SPECS:
        print(f"[*] Running {spec['test_id']} ({spec['fixture_name']})...")
        t_res = run_test(spec)
        results.append(t_res)

        status_str = "PASS" if t_res["test_passed"] else "FAIL"
        if not t_res["test_passed"]:
            all_passed = False

        print(f"    Verdict: {t_res['actual_verdict']} (expected {t_res['expected_verdict']})")
        print(f"    Exit:    {t_res['actual_exit_code']} (expected {t_res['expected_exit_code']})")
        print(f"    Result:  [{status_str}] in {t_res['duration_sec']}s")
        if not t_res["test_passed"]:
            print(f"    ERRORS:  {t_res['errors_reported']}")
        print()

    # Compute overall statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["test_passed"])
    failed_tests = total_tests - passed_tests

    # Compute script hash
    with open(VALIDATOR_SCRIPT, "rb") as f:
        validator_sha256 = hashlib.sha256(f.read()).hexdigest()

    report = {
        "gate": "GATE_B",
        "phase": "PHASE_18J",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validator_script": "research/phase18_gate_b/validate_ledger.py",
        "validator_sha256": validator_sha256,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "overall_verdict": "PASS" if all_passed else "FAIL",
        "test_results": results
    }

    # Write report to local gate directory
    local_report_path = os.path.join(BASE_DIR, "gate_b_validator_report.json")
    with open(local_report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Local report written: {local_report_path}")

    # Write report to central research results directory
    central_report_path = os.path.join(RESULTS_DIR, "gate_b_validator_report.json")
    with open(central_report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Central report written: {central_report_path}")

    print("\n" + "=" * 70)
    print(f" FINAL SUMMARY: {passed_tests}/{total_tests} tests passed. Verdict: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 70)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
