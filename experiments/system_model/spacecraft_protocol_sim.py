"""
Abstract Spacecraft-Ground Communication Model: Protocol-Level Fault Desynchronization Experiment.
Evaluates how an abstract space communication protocol detects, reacts to, and recovers from
ML-KEM implicit rejection events resulting from space-link ciphertext corruptions.

NOTE: This is an abstract simulation model designed to investigate protocol-layer resilience
trade-offs; it does not claim to represent any specific physical satellite hardware or proprietary protocol.
"""

import os
import sys
import time
import json
import hmac
import hashlib
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from algorithms.oqs_wrapper import MLKEM, get_liboqs_version
from fault_injection.fault_models.fault_definitions import (
    FaultClass, ProtocolOutcomeClass, FaultDescriptor, ProtocolFaultResult
)
from fault_injection.injector.engine import FaultInjectorEngine
from fault_injection.scheduler.scheduler import DeterministicScheduler


def calculate_wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float, float]:
    """Computes binomial proportion and Wilson score interval (percentage)."""
    if n == 0:
        return 0.0, 0.0, 0.0
    import math
    p_hat = k / n
    z = 1.95996
    denominator = 1.0 + (z**2) / n
    center_adj = p_hat + (z**2) / (2 * n)
    spread = z * math.sqrt((p_hat * (1 - p_hat) / n) + ((z**2) / (4 * n**2)))
    lower = max(0.0, (center_adj - spread) / denominator) * 100.0
    upper = min(1.0, (center_adj + spread) / denominator) * 100.0
    return round(p_hat * 100.0, 2), round(lower, 2), round(upper, 2)


def compute_frame_mac(session_key: bytes, frame_payload: bytes) -> bytes:
    """Computes a 32-byte HMAC-SHA256 authentication tag over a frame payload."""
    return hmac.new(session_key, frame_payload, hashlib.sha256).digest()


def simulate_spacecraft_protocol_campaign(
    iterations: int = 1000,
    master_seed: int = 771234,
    use_authenticated_protocol: bool = True,
    max_retries: int = 2
) -> Dict[str, Any]:
    kem = MLKEM("ML-KEM-768")
    scheduler = DeterministicScheduler(master_seed, "SPACECRAFT-PROTO-SIM")
    protocol_type_str = "Authenticated (HMAC/AEAD)" if use_authenticated_protocol else "Unauthenticated (Raw Stream)"

    print(f"\n[+] Running Abstract Spacecraft Communication Campaign (N={iterations})")
    print(f"    Protocol Mode: {protocol_type_str} | Max Retries: {max_retries}")

    counts = {p.value: 0 for p in ProtocolOutcomeClass}
    detailed_samples = []

    fault_gen = scheduler.schedule_seu_campaign(
        "ML-KEM", "ML-KEM-768", "uplink_ciphertext", kem.length_ciphertext, "uplink_rf_channel", iterations
    )

    for fault in fault_gen:
        # Spacecraft generates long-term keypair
        sc_pk, sc_sk = kem.keypair()

        # Ground station initiates session: encaps(sc_pk)
        ground_ct, ground_ss = kem.encaps(sc_pk)
        telecommand_payload = b"Telecommand Frame #5021: [ADCS_POINT_NADIR, SUN_ACQUIRE_ENABLE]"
        ground_mac = compute_frame_mac(ground_ss, telecommand_payload)

        # Space RF Link: Invert 1 bit in transmitted ciphertext
        received_ct = FaultInjectorEngine.inject_seu_bit_flip(ground_ct, fault.target_index, fault.bit_index)

        # Spacecraft receives and decapsulates
        t0 = time.perf_counter_ns()
        sc_ss = kem.decaps(received_ct, sc_sk)
        keys_match = (ground_ss == sc_ss)

        outcome = ProtocolOutcomeClass.KEY_MATCH
        retries_used = 0

        if keys_match:
            outcome = ProtocolOutcomeClass.KEY_MATCH
        else:
            # Session key mismatch occurred due to implicit rejection
            if not use_authenticated_protocol:
                # No framing authentication tag: Spacecraft accepts corrupted stream without detection!
                outcome = ProtocolOutcomeClass.KEY_MISMATCH_UNDETECTED
            else:
                # Authenticated protocol: Spacecraft checks authentication tag
                sc_mac = compute_frame_mac(sc_ss, telecommand_payload)
                if hmac.compare_digest(ground_mac, sc_mac):
                    # MAC collision (theoretically negligible for SHA-256)
                    outcome = ProtocolOutcomeClass.KEY_MISMATCH_UNDETECTED
                else:
                    # Authentication failure detected by spacecraft protocol handler!
                    # Trigger session recovery protocol (request retransmission from ground)
                    recovered = False
                    for retry in range(1, max_retries + 1):
                        retries_used += 1
                        # Retransmission over clean RF channel
                        retry_ct, retry_ss = kem.encaps(sc_pk)
                        retry_sc_ss = kem.decaps(retry_ct, sc_sk)
                        if retry_ss == retry_sc_ss:
                            recovered = True
                            break

                    if recovered:
                        outcome = ProtocolOutcomeClass.SESSION_RECOVERED
                    else:
                        outcome = ProtocolOutcomeClass.SESSION_ABORTED

        t1 = time.perf_counter_ns()
        latency_us = (t1 - t0) / 1000.0

        res = ProtocolFaultResult(
            fault=fault,
            ground_key=ground_ss.hex()[:16] + "...",
            spacecraft_key=sc_ss.hex()[:16] + "...",
            keys_match=keys_match,
            protocol_outcome=outcome,
            detection_latency_us=round(latency_us, 2),
            details=f"Retries used: {retries_used}"
        )

        counts[outcome.value] += 1
        if len(detailed_samples) < 5:
            detailed_samples.append(res.to_dict())

    # Statistics
    stats = {}
    for p_out in ProtocolOutcomeClass:
        rate, low, high = calculate_wilson_ci(counts[p_out.value], iterations)
        stats[p_out.value] = {"rate_pct": rate, "ci_95": [low, high]}

    print(f"    Outcome Counts: {counts}")
    return {
        "protocol_mode": protocol_type_str,
        "iterations": iterations,
        "counts": counts,
        "statistics": stats,
        "sample_records": detailed_samples
    }


def main():
    print("==========================================================================")
    print(" ABSTRACT SPACECRAFT-GROUND PROTOCOL DESYNCHRONIZATION EXPERIMENT")
    print(" Protocol Layer Evaluation: ML-KEM-768 Uplink Single Event Upsets")
    print("==========================================================================")

    # 1. Unauthenticated Protocol Campaign
    unauth_results = simulate_spacecraft_protocol_campaign(
        iterations=1000, master_seed=771234, use_authenticated_protocol=False, max_retries=0
    )

    # 2. Authenticated Protocol with Autonomous Retry
    auth_results = simulate_spacecraft_protocol_campaign(
        iterations=1000, master_seed=771234, use_authenticated_protocol=True, max_retries=2
    )

    output = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "experiment": "Abstract Spacecraft Protocol Desynchronization",
            "iterations_per_mode": 1000
        },
        "unauthenticated_protocol": unauth_results,
        "authenticated_protocol": auth_results
    }

    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../results"))
    os.makedirs(results_dir, exist_ok=True)
    out_file = os.path.join(results_dir, "spacecraft_protocol_desync_results.json")

    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[+] Protocol desynchronization experiment saved to: {out_file}")


if __name__ == "__main__":
    main()
