"""
Phase 4A (Corrected Taxonomy): Level 1 Fault Injection Campaign.
Evaluates ML-KEM-768 and ML-DSA-65 under controlled software fault abstractions.
Strictly separates:
- CORRECT_VALID_DECAPSULATION
- EXPECTED_IMPLICIT_REJECTION
- EXPECTED_SIGNATURE_REJECTION
- EXPLICIT_ERROR
- UNEXPECTED_INCORRECT_OUTPUT
- CRASH / TIMEOUT
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
    FaultClass, CryptoOutcomeClass, FaultDescriptor, CryptoFaultResult
)
from fault_injection.injector.engine import FaultInjectorEngine
from fault_injection.scheduler.scheduler import DeterministicScheduler


def calculate_wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float, float]:
    """Computes binomial proportion and Wilson score interval (percentage)."""
    if n == 0:
        return 0.0, 0.0, 0.0

    p_hat = k / n
    z = 1.95996

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
    print("\n" + "=" * 75)
    print(" RUNNING PHASE 4A: ML-KEM-768 LEVEL 1 FAULT CAMPAIGN (CORRECTED TAXONOMY)")
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
        counts = {o.value: 0 for o in CryptoOutcomeClass}
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
            pk, sk = kem.keypair()
            ct, ss_enc = kem.encaps(pk)

            t0 = time.perf_counter_ns()
            outcome = CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION
            fault_detected = False
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
                        outcome = CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION
                    else:
                        # FIPS 203 Section 7.3: Standard-mandated implicit rejection
                        outcome = CryptoOutcomeClass.EXPECTED_IMPLICIT_REJECTION
                        fault_detected = False
                        details = "FO transform executed implicit rejection (pseudorandom shared secret returned)"

                elif c["target"] == "public_key":
                    corrupted_pk = FaultInjectorEngine.inject_seu_bit_flip(pk, fault.target_index, fault.bit_index)
                    try:
                        ct_f, ss_enc_f = kem.encaps(corrupted_pk)
                        ss_dec_f = kem.decaps(ct_f, sk)
                        if ss_enc_f == ss_dec_f:
                            outcome = CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION
                        else:
                            outcome = CryptoOutcomeClass.EXPECTED_IMPLICIT_REJECTION
                            details = "Corrupted public key caused re-encryption check mismatch in decapsulation"
                    except RuntimeError as e:
                        outcome = CryptoOutcomeClass.EXPLICIT_ERROR
                        err_code = 1
                        fault_detected = True
                        details = f"Library validation caught invalid public key encoding: {e}"

                elif c["target"] == "secret_key":
                    corrupted_sk = FaultInjectorEngine.inject_seu_bit_flip(sk, fault.target_index, fault.bit_index)
                    try:
                        ss_dec = kem.decaps(ct, corrupted_sk)
                        if ss_dec == ss_enc:
                            outcome = CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION
                            details = "Bit-flip in unused/rejection-only portion of secret key did not affect valid decapsulation"
                        else:
                            outcome = CryptoOutcomeClass.EXPECTED_IMPLICIT_REJECTION
                            details = "Corrupted secret key altered decoded message, triggering FO implicit rejection"
                    except RuntimeError as e:
                        outcome = CryptoOutcomeClass.EXPLICIT_ERROR
                        err_code = 1
                        fault_detected = True
                        details = f"Library validation caught invalid secret key encoding (modulus violation): {e}"

            except Exception as e:
                outcome = CryptoOutcomeClass.CRASH
                err_code = -1
                details = str(e)

            t1 = time.perf_counter_ns()
            runtime_us = (t1 - t0) / 1000.0

            res = CryptoFaultResult(
                fault=fault,
                baseline_result=ss_enc.hex()[:16] + "...",
                faulted_result=ss_dec.hex()[:16] + "..." if 'ss_dec' in locals() else "N/A",
                outcome_class=outcome,
                fault_detected=fault_detected,
                runtime_us=round(runtime_us, 2),
                memory_bytes=len(ct) + len(pk) + len(sk),
                error_code=err_code,
                details=details
            )

            counts[outcome.value] += 1
            if len(detailed_samples) < 5:
                detailed_samples.append(res.to_dict())

        imp_rate, imp_low, imp_high = calculate_wilson_ci(counts[CryptoOutcomeClass.EXPECTED_IMPLICIT_REJECTION.value], iterations)
        err_rate, err_low, err_high = calculate_wilson_ci(counts[CryptoOutcomeClass.EXPLICIT_ERROR.value], iterations)
        cor_rate, cor_low, cor_high = calculate_wilson_ci(counts[CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION.value], iterations)

        campaign_results[c["name"]] = {
            "target": c["target"],
            "fault_type": c["type"],
            "iterations": iterations,
            "counts": counts,
            "rates_pct": {
                "expected_implicit_rejection": {"rate": imp_rate, "ci_95": [imp_low, imp_high]},
                "explicit_error": {"rate": err_rate, "ci_95": [err_low, err_high]},
                "correct_valid_decapsulation": {"rate": cor_rate, "ci_95": [cor_low, cor_high]}
            },
            "sample_records": detailed_samples
        }

        print(f"  Counts: {counts}")
        print(f"  EXPECTED_IMPLICIT_REJECTION: {imp_rate}% [95% CI: {imp_low}% - {imp_high}%]")
        print(f"  EXPLICIT_ERROR:              {err_rate}% [95% CI: {err_low}% - {err_high}%]")
        print(f"  CORRECT_VALID_DECAPSULATION: {cor_rate}% [95% CI: {cor_low}% - {cor_high}%]")

    return campaign_results


def run_dsa_level1_experiment(
    iterations: int = 1000,
    master_seed: int = 890123
) -> Dict[str, Any]:
    print("\n" + "=" * 75)
    print(" RUNNING PHASE 4A: ML-DSA-65 LEVEL 1 FAULT CAMPAIGN (CORRECTED TAXONOMY)")
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
        counts = {o.value: 0 for o in CryptoOutcomeClass}
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
            outcome = CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION
            fault_detected = False
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
                        outcome = CryptoOutcomeClass.UNEXPECTED_INCORRECT_OUTPUT
                        details = "Corrupted signature unexpectedly accepted as valid by verifier"
                    else:
                        outcome = CryptoOutcomeClass.EXPECTED_SIGNATURE_REJECTION
                        fault_detected = True
                        details = "Verifier rejected corrupted signature under tested API corruption conditions"

                elif c["target"] == "message":
                    corrupted_msg = FaultInjectorEngine.inject_seu_bit_flip(base_msg, fault.target_index, fault.bit_index)
                    valid = sig.verify(corrupted_msg, signature, pk)
                    if valid:
                        outcome = CryptoOutcomeClass.UNEXPECTED_INCORRECT_OUTPUT
                    else:
                        outcome = CryptoOutcomeClass.EXPECTED_SIGNATURE_REJECTION
                        fault_detected = True
                        details = "Verifier rejected signature on altered message"

                elif c["target"] == "public_key":
                    corrupted_pk = FaultInjectorEngine.inject_seu_bit_flip(pk, fault.target_index, fault.bit_index)
                    valid = sig.verify(base_msg, signature, corrupted_pk)
                    if valid:
                        outcome = CryptoOutcomeClass.UNEXPECTED_INCORRECT_OUTPUT
                    else:
                        outcome = CryptoOutcomeClass.EXPECTED_SIGNATURE_REJECTION
                        fault_detected = True
                        details = "Verifier rejected signature under corrupted public key"

            except Exception as e:
                outcome = CryptoOutcomeClass.CRASH
                err_code = -1
                details = str(e)

            t1 = time.perf_counter_ns()
            runtime_us = (t1 - t0) / 1000.0

            res = CryptoFaultResult(
                fault=fault,
                baseline_result="VALID",
                faulted_result="VALID" if outcome == CryptoOutcomeClass.CORRECT_VALID_DECAPSULATION else "REJECTED",
                outcome_class=outcome,
                fault_detected=fault_detected,
                runtime_us=round(runtime_us, 2),
                memory_bytes=len(signature) + len(pk),
                error_code=err_code,
                details=details
            )

            counts[outcome.value] += 1
            if len(detailed_samples) < 5:
                detailed_samples.append(res.to_dict())

        rej_rate, rej_low, rej_high = calculate_wilson_ci(counts[CryptoOutcomeClass.EXPECTED_SIGNATURE_REJECTION.value], iterations)

        campaign_results[c["name"]] = {
            "target": c["target"],
            "fault_type": c["type"],
            "iterations": iterations,
            "counts": counts,
            "rates_pct": {
                "expected_signature_rejection": {"rate": rej_rate, "ci_95": [rej_low, rej_high]}
            },
            "sample_records": detailed_samples
        }

        print(f"  Counts: {counts}")
        print(f"  EXPECTED_SIGNATURE_REJECTION: {rej_rate}% [95% CI: {rej_low}% - {rej_high}%]")

    return campaign_results


def main():
    print("==========================================================================")
    print(" PQC SPACE SYSTEMS FAULT RESILIENCE - LEVEL 1 CAMPAIGN (CORRECTED)")
    print(f" Host: Apple M1 (arm64) | liboqs version: {get_liboqs_version()}")
    print("==========================================================================")

    kem_results = run_kem_level1_experiment(iterations=1000, master_seed=421098)
    dsa_results = run_dsa_level1_experiment(iterations=1000, master_seed=890123)

    output = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "liboqs_version": get_liboqs_version(),
            "phase": "4A_Level1_Corrected_Taxonomy",
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
