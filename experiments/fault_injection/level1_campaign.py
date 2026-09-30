"""
Phase 4A: Level 1 (API & Input Buffer) Fault Injection Experimental Campaign.
Evaluates ML-KEM-768 and ML-DSA-65 under controlled software fault abstractions:
- SEU (Single-bit flips)
- Multi-bit flips
- Burst corruption
- Byte-level corruption
- Buffer truncation

Records structured metadata, computes Wilson score 95% confidence intervals,
and explicitly analyzes the ML-KEM implicit rejection vs. session desynchronization duality.
"""

import os
import sys
import time
import json
import math
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from algorithms.oqs_wrapper import MLKEM, MLDSA, get_liboqs_version
from fault_injection.fault_models.fault_definitions import (
    FaultClass, OutcomeClass, FaultDescriptor, FaultResult
)
from fault_injection.injector.engine import FaultInjectorEngine
from fault_injection.scheduler.scheduler import DeterministicScheduler


def calculate_wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Computes binomial proportion and Wilson score interval.
    Returns (proportion, lower_bound, upper_bound) in percent.
    """
    if n == 0:
        return 0.0, 0.0, 0.0

    p_hat = k / n
    z = 1.95996  # 95% two-sided normal quantile

    denominator = 1.0 + (z**2) / n
    center_adj = p_hat + (z**2) / (2 * n)
    spread = z * math.sqrt((p_hat * (1 - p_hat) / n) + ((z**2) / (4 * n**2)))

    lower = max(0.0, (center_adj - spread) / denominator) * 100.0
    upper = min(1.0, (center_adj + spread) / denominator) * 100.0
    return round(p_hat * 100.0, 2), round(lower, 2), round(upper, 2)


def run_kem_level1_experiment(
    iterations: int = 1000,
    master_seed: int = 421098
) -> Dict[str, Any]:
    """Runs Level 1 input fault campaigns on ML-KEM-768."""
    print("\n" + "=" * 75)
    print(" RUNNING PHASE 4A: ML-KEM-768 LEVEL 1 FAULT CAMPAIGN")
    print(f" Target: ML-KEM-768 | Iterations per test: {iterations} | Master Seed: {master_seed}")
    print("=" * 75)

    kem = MLKEM("ML-KEM-768")
    scheduler = DeterministicScheduler(master_seed, "MLKEM768-L1-CAMPAIGN")

    campaigns = [
        {"name": "SEU_Ciphertext", "target": "ciphertext", "type": "single_bit_flip", "class": FaultClass.SEU},
        {"name": "Burst_Ciphertext", "target": "ciphertext", "type": "burst_corruption", "class": FaultClass.BURST, "burst_len": 4},
        {"name": "SEU_PublicKey", "target": "public_key", "type": "single_bit_flip", "class": FaultClass.SEU},
        {"name": "SEU_SecretKey", "target": "secret_key", "type": "single_bit_flip", "class": FaultClass.SEU},
    ]

    campaign_results = {}

    for c in campaigns:
        print(f"\n[+] Executing {c['name']} ({c['target']})...")
        counts = {o.value: 0 for o in OutcomeClass}
        detailed_samples = []

        if c["class"] == FaultClass.SEU:
            target_len = kem.length_ciphertext if c["target"] == "ciphertext" else (
                kem.length_public_key if c["target"] == "public_key" else kem.length_secret_key
            )
            fault_gen = scheduler.schedule_seu_campaign(
                "ML-KEM", "ML-KEM-768", c["target"], target_len, "pre_operation", iterations
            )
        else:
            fault_gen = scheduler.schedule_burst_campaign(
                "ML-KEM", "ML-KEM-768", c["target"], kem.length_ciphertext, c["burst_len"], "pre_decaps", iterations
            )

        for fault in fault_gen:
            # 1. Baseline legitimate execution
            pk, sk = kem.keypair()
            ct, ss_enc = kem.encaps(pk)

            t0 = time.perf_counter_ns()
            outcome = OutcomeClass.CORRECT
            fault_detected = False
            recovered = False
            err_code = 0
            details = None

            try:
                if c["target"] == "ciphertext":
                    if c["class"] == FaultClass.SEU:
                        corrupted_ct = FaultInjectorEngine.inject_seu_bit_flip(ct, fault.target_index, fault.bit_index)
                    else:
                        corrupted_ct = FaultInjectorEngine.inject_burst_corruption(ct, fault.target_index, c["burst_len"], fault.seed)

                    ss_dec = kem.decaps(corrupted_ct, sk)

                    if ss_dec == ss_enc:
                        # Theoretically impossible for FIPS 203 under ciphertext corruption
                        outcome = OutcomeClass.CORRECT
                    else:
                        # FIPS 203 Section 7.3: Decapsulation returns pseudorandom key (implicit rejection)
                        # At KEM level: Expected rejection mechanism
                        # At System/Spacecraft level: Silent Data Corruption (SDC) / session desync
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                        fault_detected = False
                        details = "Implicit rejection triggered: FO transform produced alternate pseudorandom key without error"

                elif c["target"] == "public_key":
                    corrupted_pk = FaultInjectorEngine.inject_seu_bit_flip(pk, fault.target_index, fault.bit_index)
                    # Encapsulate under corrupted public key
                    ct_f, ss_enc_f = kem.encaps(corrupted_pk)
                    ss_dec_f = kem.decaps(ct_f, sk)

                    if ss_enc_f == ss_dec_f:
                        outcome = OutcomeClass.CORRECT
                    else:
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                        details = "Corrupted public key produced mismatched ciphertext/shared secret"

                elif c["target"] == "secret_key":
                    corrupted_sk = FaultInjectorEngine.inject_seu_bit_flip(sk, fault.target_index, fault.bit_index)
                    ss_dec = kem.decaps(ct, corrupted_sk)

                    if ss_dec == ss_enc:
                        outcome = OutcomeClass.CORRECT
                    else:
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                        details = "Corrupted secret key produced mismatched shared secret during decapsulation"

            except Exception as e:
                outcome = OutcomeClass.CRASH
                err_code = -1
                details = str(e)

            t1 = time.perf_counter_ns()
            runtime_us = (t1 - t0) / 1000.0

            res = FaultResult(
                fault=fault,
                baseline_result=ss_enc.hex()[:16] + "...",
                faulted_result=ss_dec.hex()[:16] + "..." if 'ss_dec' in locals() else "N/A",
                outcome_class=outcome,
                fault_detected=fault_detected,
                recovered=recovered,
                runtime_us=round(runtime_us, 2),
                memory_bytes=len(ct) + len(pk) + len(sk),
                error_code=err_code,
                details=details
            )

            counts[outcome.value] += 1
            if len(detailed_samples) < 5:
                detailed_samples.append(res.to_dict())

        # Statistical analysis with Wilson score interval
        sdc_rate, sdc_low, sdc_high = calculate_wilson_ci(counts[OutcomeClass.SILENT_DATA_CORRUPTION.value], iterations)
        crash_rate, _, _ = calculate_wilson_ci(counts[OutcomeClass.CRASH.value], iterations)

        campaign_results[c["name"]] = {
            "target": c["target"],
            "fault_type": c["type"],
            "iterations": iterations,
            "counts": counts,
            "rates_pct": {
                "silent_data_corruption": {"rate": sdc_rate, "ci_95": [sdc_low, sdc_high]},
                "crash": {"rate": crash_rate}
            },
            "sample_records": detailed_samples
        }

        print(f"  Outcome counts: {counts}")
        print(f"  Silent Data Corruption (SDC): {sdc_rate}% [95% CI: {sdc_low}% - {sdc_high}%]")

    return campaign_results


def run_dsa_level1_experiment(
    iterations: int = 1000,
    master_seed: int = 890123
) -> Dict[str, Any]:
    """Runs Level 1 input fault campaigns on ML-DSA-65."""
    print("\n" + "=" * 75)
    print(" RUNNING PHASE 4A: ML-DSA-65 LEVEL 1 FAULT CAMPAIGN")
    print(f" Target: ML-DSA-65 | Iterations per test: {iterations} | Master Seed: {master_seed}")
    print("=" * 75)

    sig = MLDSA("ML-DSA-65")
    scheduler = DeterministicScheduler(master_seed, "MLDSA65-L1-CAMPAIGN")
    base_msg = b"Spacecraft Navigation Telemetry Block seq=1024 epoch=2026-10-01"

    campaigns = [
        {"name": "SEU_Signature", "target": "signature", "type": "single_bit_flip", "class": FaultClass.SEU},
        {"name": "Burst_Signature", "target": "signature", "type": "burst_corruption", "class": FaultClass.BURST, "burst_len": 4},
        {"name": "SEU_Message", "target": "message", "type": "single_bit_flip", "class": FaultClass.SEU},
        {"name": "SEU_PublicKey", "target": "public_key", "type": "single_bit_flip", "class": FaultClass.SEU},
        {"name": "Truncated_Signature", "target": "signature", "type": "truncation", "class": FaultClass.BURST, "trunc_len": 3000},
    ]

    campaign_results = {}

    for c in campaigns:
        print(f"\n[+] Executing {c['name']} ({c['target']})...")
        counts = {o.value: 0 for o in OutcomeClass}
        detailed_samples = []

        if c["type"] == "single_bit_flip":
            target_len = sig.length_signature if c["target"] == "signature" else (
                len(base_msg) if c["target"] == "message" else sig.length_public_key
            )
            fault_gen = scheduler.schedule_seu_campaign(
                "ML-DSA", "ML-DSA-65", c["target"], target_len, "pre_verify", iterations
            )
        else:
            fault_gen = scheduler.schedule_burst_campaign(
                "ML-DSA", "ML-DSA-65", c["target"], sig.length_signature, 4, "pre_verify", iterations
            )

        for fault in fault_gen:
            pk, sk = sig.keypair()
            signature = sig.sign(base_msg, sk)

            t0 = time.perf_counter_ns()
            outcome = OutcomeClass.CORRECT
            fault_detected = False
            recovered = False
            err_code = 0
            details = None

            try:
                if c["target"] == "signature":
                    if c["type"] == "single_bit_flip":
                        corrupted_sig = FaultInjectorEngine.inject_seu_bit_flip(signature, fault.target_index, fault.bit_index)
                    elif c["type"] == "truncation":
                        corrupted_sig = FaultInjectorEngine.inject_truncation(signature, c["trunc_len"])
                    else:
                        corrupted_sig = FaultInjectorEngine.inject_burst_corruption(signature, fault.target_index, 4, fault.seed)

                    valid = sig.verify(base_msg, corrupted_sig, pk)
                    if valid:
                        # Catastrophic: corrupted signature verified!
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                        details = "Corrupted signature accepted as valid by verifier"
                    else:
                        # Correct cryptographic behavior: invalid signature detected and rejected
                        outcome = OutcomeClass.EXPECTED_REJECTION
                        fault_detected = True
                        details = "Verifier correctly rejected corrupted signature"

                elif c["target"] == "message":
                    corrupted_msg = FaultInjectorEngine.inject_seu_bit_flip(base_msg, fault.target_index, fault.bit_index)
                    valid = sig.verify(corrupted_msg, signature, pk)
                    if valid:
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                    else:
                        outcome = OutcomeClass.EXPECTED_REJECTION
                        fault_detected = True
                        details = "Verifier correctly rejected signature on altered message"

                elif c["target"] == "public_key":
                    corrupted_pk = FaultInjectorEngine.inject_seu_bit_flip(pk, fault.target_index, fault.bit_index)
                    valid = sig.verify(base_msg, signature, corrupted_pk)
                    if valid:
                        outcome = OutcomeClass.SILENT_DATA_CORRUPTION
                    else:
                        outcome = OutcomeClass.EXPECTED_REJECTION
                        fault_detected = True
                        details = "Verifier correctly rejected signature under corrupted public key"

            except Exception as e:
                outcome = OutcomeClass.CRASH
                err_code = -1
                details = str(e)

            t1 = time.perf_counter_ns()
            runtime_us = (t1 - t0) / 1000.0

            res = FaultResult(
                fault=fault,
                baseline_result="VALID",
                faulted_result="VALID" if outcome == OutcomeClass.CORRECT else "REJECTED",
                outcome_class=outcome,
                fault_detected=fault_detected,
                recovered=recovered,
                runtime_us=round(runtime_us, 2),
                memory_bytes=len(signature) + len(pk),
                error_code=err_code,
                details=details
            )

            counts[outcome.value] += 1
            if len(detailed_samples) < 5:
                detailed_samples.append(res.to_dict())

        # Statistical analysis with Wilson score interval
        rejection_rate, rej_low, rej_high = calculate_wilson_ci(counts[OutcomeClass.EXPECTED_REJECTION.value], iterations)
        sdc_rate, sdc_low, sdc_high = calculate_wilson_ci(counts[OutcomeClass.SILENT_DATA_CORRUPTION.value], iterations)

        campaign_results[c["name"]] = {
            "target": c["target"],
            "fault_type": c["type"],
            "iterations": iterations,
            "counts": counts,
            "rates_pct": {
                "expected_rejection": {"rate": rejection_rate, "ci_95": [rej_low, rej_high]},
                "silent_data_corruption": {"rate": sdc_rate, "ci_95": [sdc_low, sdc_high]}
            },
            "sample_records": detailed_samples
        }

        print(f"  Outcome counts: {counts}")
        print(f"  Expected Rejection: {rejection_rate}% [95% CI: {rej_low}% - {rej_high}%]")

    return campaign_results


def main():
    print("==========================================================================")
    print(" PQC SPACE SYSTEMS FAULT RESILIENCE RESEARCH - PHASE 4A LEVEL 1 CAMPAIGN")
    print(f" Host: Apple M1 (arm64) | liboqs version: {get_liboqs_version()}")
    print("==========================================================================")

    kem_results = run_kem_level1_experiment(iterations=1000, master_seed=421098)
    dsa_results = run_dsa_level1_experiment(iterations=1000, master_seed=890123)

    output = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "liboqs_version": get_liboqs_version(),
            "phase": "4A_Level1_Input_API",
            "iterations_per_campaign": 1000
        },
        "ml_kem_768": kem_results,
        "ml_dsa_65": dsa_results
    }

    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../results"))
    os.makedirs(results_dir, exist_ok=True)
    out_file = os.path.join(results_dir, "level1_fault_experiment_results.json")

    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[+] Level 1 experimental campaign successfully recorded to: {out_file}")


if __name__ == "__main__":
    main()
