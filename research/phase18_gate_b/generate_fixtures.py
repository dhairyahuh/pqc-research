#!/usr/bin/env python3
"""
generate_fixtures.py — Generate synthetic test fixtures for Phase 18J Gate B.

Generates 11 deterministic fixtures into research/phase18_gate_b/fixtures/:
  1. fixture_valid_complete.jsonl
  2. fixture_missing_condition.jsonl
  3. fixture_duplicate_start.jsonl
  4. fixture_orphan_finalize.jsonl
  5. fixture_quota_violation.jsonl
  6. fixture_corrupted_seal.jsonl
  7. fixture_tampered_payload.jsonl
  8. fixture_false_success_semantics.jsonl
  9. fixture_missing_seal.jsonl
  10. fixture_truncated_write.jsonl
  11. fixture_dangling_start.jsonl
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Tuple

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
os.makedirs(FIXTURES_DIR, exist_ok=True)

TOTAL_MASTER_SCENARIOS = 420
CONDITIONS = ("C00", "C10", "C01", "C11")
DUMMY_SS_HEX = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def get_scenario_metadata(sid: int) -> Dict[str, Any]:
    """Returns ratified stratum metadata for scenario sid in [1, 420]."""
    if 1 <= sid <= 300:
        return {
            "quota_stratum": "QUOTA_1_ADMITTED_CORRUPTED",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_BIT", "C11": "CH_BIT"},
            "control_cell": None,
        }
    elif 301 <= sid <= 320:
        return {
            "quota_stratum": "QUOTA_2_ADMITTED_CLEAN",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_DUP", "C11": "CH_DUP"},
            "control_cell": None,
        }
    elif 321 <= sid <= 340:
        return {
            "quota_stratum": "QUOTA_2_ADMITTED_CLEAN",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_REORDER", "C11": "CH_REORDER"},
            "control_cell": None,
        }
    elif 341 <= sid <= 355:
        return {
            "quota_stratum": "QUOTA_3_DELIVERY_BLOCKING",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_TRUNC", "C11": "CH_TRUNC"},
            "control_cell": None,
        }
    elif 356 <= sid <= 370:
        return {
            "quota_stratum": "QUOTA_3_DELIVERY_BLOCKING",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_LOSS", "C11": "CH_LOSS"},
            "control_cell": None,
        }
    elif 371 <= sid <= 385:
        return {
            "quota_stratum": "QUOTA_3_DELIVERY_BLOCKING",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_DELAY", "C11": "CH_DELAY"},
            "control_cell": None,
        }
    elif 386 <= sid <= 400:
        return {
            "quota_stratum": "QUOTA_3_DELIVERY_BLOCKING",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_INTERRUPT", "C11": "CH_INTERRUPT"},
            "control_cell": None,
        }
    elif 401 <= sid <= 405:
        return {
            "quota_stratum": "QUOTA_4_NEGATIVE_CONTROL",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "NONE", "C11": "NONE"},
            "control_cell": "CONTROL_DORMANT_CLEAN",
        }
    elif 406 <= sid <= 410:
        return {
            "quota_stratum": "QUOTA_4_NEGATIVE_CONTROL",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_BIT", "C11": "CH_BIT"},
            "control_cell": "CONTROL_DORMANT_BIT",
        }
    elif 411 <= sid <= 415:
        return {
            "quota_stratum": "QUOTA_4_NEGATIVE_CONTROL",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "NONE", "C11": "NONE"},
            "control_cell": "CONTROL_SHAM_CLEAN",
        }
    elif 416 <= sid <= 420:
        return {
            "quota_stratum": "QUOTA_4_NEGATIVE_CONTROL",
            "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_BIT", "C11": "CH_BIT"},
            "control_cell": "CONTROL_SHAM_BIT",
        }
    else:
        raise ValueError(f"Scenario ID {sid} out of bounds [1, 420]")


def build_trial_records(sid: int, cond: str, meta: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Builds standard (START, FINALIZE) pair for a scenario condition."""
    ch_cls = meta["channel_class"][cond]
    stratum = meta["quota_stratum"]
    ctrl_cell = meta["control_cell"]

    start_rec = {
        "record_type": "START",
        "master_seed_id": sid,
        "condition": cond,
        "quota_stratum": stratum,
        "channel_class": ch_cls,
        "control_cell": ctrl_cell,
        "timestamp_utc": "2026-10-12T00:00:00Z",
    }

    # Outcomes
    # In Quota 3 C01/C11, channel fault blocks delivery
    is_q3_blocked = (stratum == "QUOTA_3_DELIVERY_BLOCKING" and cond in ("C01", "C11"))
    if is_q3_blocked:
        proto_outcome = "DELIVERY_FAILED"
        crypto_endpoint = "NOT_EVALUATED_DELIVERY_BLOCKED"
        ss_hex = None
    else:
        proto_outcome = "KEY_ESTABLISHED"
        crypto_endpoint = "MATCH"
        ss_hex = DUMMY_SS_HEX

    # Restoration status: C10 and C11 must verify table restoration
    if cond in ("C10", "C11"):
        restoration_status = "RESTORED_AND_VERIFIED"
    else:
        restoration_status = "NOT_APPLICABLE"

    finalize_rec = {
        "record_type": "FINALIZE",
        "master_seed_id": sid,
        "condition": cond,
        "quota_stratum": stratum,
        "channel_class": ch_cls,
        "control_cell": ctrl_cell,
        "execution_status": "ATTEMPTED_COMPLETED",
        "protocol_outcome": proto_outcome,
        "crypto_endpoint": crypto_endpoint,
        "restoration_status": restoration_status,
        "output_ss_hex": ss_hex,
        "timestamp_utc": "2026-10-12T00:00:01Z",
    }

    return start_rec, finalize_rec


def write_ledger_with_seal(path: str, records: List[Dict[str, Any]], trial_count: int = 1680) -> None:
    """Serializes records to JSON Lines, computes SHA-256 seal over bytes 0..M-1, and appends CAMPAIGN_SEAL."""
    lines = [json.dumps(r, separators=(",", ":")) + "\n" for r in records]
    payload_bytes = "".join(lines).encode("utf-8")
    covered_bytes = len(payload_bytes)
    content_sha256 = hashlib.sha256(payload_bytes).hexdigest()

    seal_rec = {
        "record_type": "CAMPAIGN_SEAL",
        "status": "COMPLETE",
        "trial_count": trial_count,
        "covered_bytes": covered_bytes,
        "content_sha256": content_sha256,
    }
    seal_line = json.dumps(seal_rec, separators=(",", ":")) + "\n"

    with open(path, "wb") as f:
        f.write(payload_bytes)
        f.write(seal_line.encode("utf-8"))


def generate_all_fixtures():
    print("[+] Generating base complete campaign records...")
    base_records: List[Dict[str, Any]] = []
    for sid in range(1, TOTAL_MASTER_SCENARIOS + 1):
        meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            base_records.append(s_rec)
            base_records.append(f_rec)

    # 1. fixture_valid_complete.jsonl
    p1 = os.path.join(FIXTURES_DIR, "fixture_valid_complete.jsonl")
    write_ledger_with_seal(p1, base_records, trial_count=1680)
    print(f"  -> Generated {p1} ({os.path.getsize(p1)} bytes)")

    # 2. fixture_missing_condition.jsonl
    # Seed 45 has C00, C10, C01 (missing C11), no seal (runner interrupted)
    p2 = os.path.join(FIXTURES_DIR, "fixture_missing_condition.jsonl")
    records_missing_c11 = []
    for sid in range(1, TOTAL_MASTER_SCENARIOS + 1):
        meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            if sid == 45 and cond == "C11":
                continue
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            records_missing_c11.append(s_rec)
            records_missing_c11.append(f_rec)
    with open(p2, "wb") as f:
        for r in records_missing_c11:
            f.write((json.dumps(r, separators=(",", ":")) + "\n").encode("utf-8"))
    print(f"  -> Generated {p2} ({os.path.getsize(p2)} bytes)")

    # 3. fixture_duplicate_start.jsonl
    # Trial (12, C11) has duplicate START record
    p3 = os.path.join(FIXTURES_DIR, "fixture_duplicate_start.jsonl")
    records_dup = []
    for sid in range(1, 20):  # Partial run up to scenario 20 is sufficient to trigger error
        meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            records_dup.append(s_rec)
            if sid == 12 and cond == "C11":
                # Duplicate START record inserted immediately
                records_dup.append(dict(s_rec))
            records_dup.append(f_rec)
    with open(p3, "wb") as f:
        for r in records_dup:
            f.write((json.dumps(r, separators=(",", ":")) + "\n").encode("utf-8"))
    print(f"  -> Generated {p3} ({os.path.getsize(p3)} bytes)")

    # 4. fixture_orphan_finalize.jsonl
    # Trial (1, C00) starts directly with FINALIZE without START
    p4 = os.path.join(FIXTURES_DIR, "fixture_orphan_finalize.jsonl")
    meta1 = get_scenario_metadata(1)
    _, f_rec1 = build_trial_records(1, "C00", meta1)
    with open(p4, "wb") as f:
        f.write((json.dumps(f_rec1, separators=(",", ":")) + "\n").encode("utf-8"))
    print(f"  -> Generated {p4} ({os.path.getsize(p4)} bytes)")

    # 5. fixture_quota_violation.jsonl
    # Scenario 300 changed from Quota 1 to Quota 2 (Quota 1 = 299, Quota 2 = 41)
    p5 = os.path.join(FIXTURES_DIR, "fixture_quota_violation.jsonl")
    records_quota_bad = []
    for sid in range(1, TOTAL_MASTER_SCENARIOS + 1):
        if sid == 300:
            bad_meta = {
                "quota_stratum": "QUOTA_2_ADMITTED_CLEAN",
                "channel_class": {"C00": "NONE", "C10": "NONE", "C01": "CH_DUP", "C11": "CH_DUP"},
                "control_cell": None,
            }
            meta = bad_meta
        else:
            meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            records_quota_bad.append(s_rec)
            records_quota_bad.append(f_rec)
    write_ledger_with_seal(p5, records_quota_bad, trial_count=1680)
    print(f"  -> Generated {p5} ({os.path.getsize(p5)} bytes)")

    # 6. fixture_corrupted_seal.jsonl
    # content_sha256 in CAMPAIGN_SEAL has 1 flipped character
    p6 = os.path.join(FIXTURES_DIR, "fixture_corrupted_seal.jsonl")
    with open(p1, "rb") as f:
        valid_bytes = f.read()
    # Replace last character of content_sha256
    # In seal line: ..."content_sha256":"<64 hex>"}\n
    # Flip the character right before '"}'
    idx = valid_bytes.rfind(b'"}')
    corrupted_bytes = bytearray(valid_bytes)
    # Flip char at idx - 1
    corrupted_bytes[idx - 1] = ord("0") if chr(corrupted_bytes[idx - 1]) != "0" else ord("1")
    with open(p6, "wb") as f:
        f.write(corrupted_bytes)
    print(f"  -> Generated {p6} ({os.path.getsize(p6)} bytes)")

    # 7. fixture_tampered_payload.jsonl
    # Modify 1 byte in the covered payload (offset 500) while keeping seal untouched
    p7 = os.path.join(FIXTURES_DIR, "fixture_tampered_payload.jsonl")
    tampered_bytes = bytearray(valid_bytes)
    tampered_bytes[500] = ord("X") if tampered_bytes[500] != ord("X") else ord("Y")
    with open(p7, "wb") as f:
        f.write(tampered_bytes)
    print(f"  -> Generated {p7} ({os.path.getsize(p7)} bytes)")

    # 8. fixture_false_success_semantics.jsonl
    # Scenario 10 C10 has execution_status: SIGNAL_TERMINATION but restoration_status: RESTORED_AND_VERIFIED
    p8 = os.path.join(FIXTURES_DIR, "fixture_false_success_semantics.jsonl")
    records_false_success = []
    for sid in range(1, TOTAL_MASTER_SCENARIOS + 1):
        meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            if sid == 10 and cond == "C10":
                f_rec["execution_status"] = "SIGNAL_TERMINATION"
                f_rec["restoration_status"] = "RESTORED_AND_VERIFIED"  # False success!
                f_rec["protocol_outcome"] = "CRASH_TERMINATED"
                f_rec["crypto_endpoint"] = "NOT_EVALUATED_CRASH"
                f_rec["output_ss_hex"] = None
            records_false_success.append(s_rec)
            records_false_success.append(f_rec)
    write_ledger_with_seal(p8, records_false_success, trial_count=1680)
    print(f"  -> Generated {p8} ({os.path.getsize(p8)} bytes)")

    # 9. fixture_missing_seal.jsonl
    # All 1,680 trials complete, but CAMPAIGN_SEAL line omitted
    p9 = os.path.join(FIXTURES_DIR, "fixture_missing_seal.jsonl")
    with open(p1, "rb") as f:
        lines = f.readlines()
    # Drop seal line (last line)
    seal_dropped_bytes = b"".join(lines[:-1])
    with open(p9, "wb") as f:
        f.write(seal_dropped_bytes)
    print(f"  -> Generated {p9} ({os.path.getsize(p9)} bytes)")

    # 10. fixture_truncated_write.jsonl
    # Trailing line missing \n and cut mid-JSON
    p10 = os.path.join(FIXTURES_DIR, "fixture_truncated_write.jsonl")
    with open(p1, "rb") as f:
        full_content = f.read()
    # Truncate by 35 bytes (middle of seal record, no trailing \n)
    truncated_content = full_content[:-35]
    with open(p10, "wb") as f:
        f.write(truncated_content)
    print(f"  -> Generated {p10} ({os.path.getsize(p10)} bytes)")

    # 11. fixture_dangling_start.jsonl
    # Scenario 50 C00 emits START, then crash before FINALIZE, EOF reached without seal
    p11 = os.path.join(FIXTURES_DIR, "fixture_dangling_start.jsonl")
    records_dangling = []
    for sid in range(1, 51):
        meta = get_scenario_metadata(sid)
        for cond in CONDITIONS:
            if sid == 50 and cond == "C00":
                # Emit START only, then simulate process crash
                s_rec, _ = build_trial_records(sid, cond, meta)
                records_dangling.append(s_rec)
                break
            s_rec, f_rec = build_trial_records(sid, cond, meta)
            records_dangling.append(s_rec)
            records_dangling.append(f_rec)
    with open(p11, "wb") as f:
        for r in records_dangling:
            f.write((json.dumps(r, separators=(",", ":")) + "\n").encode("utf-8"))
    print(f"  -> Generated {p11} ({os.path.getsize(p11)} bytes)")

    print("[+] All 11 fixtures successfully generated.")


if __name__ == "__main__":
    generate_all_fixtures()
