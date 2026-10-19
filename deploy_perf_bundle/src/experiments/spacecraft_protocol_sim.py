"""
Abstract Spacecraft-Ground Communication Model: Protocol-Level Fault Desynchronization Experiment.
Evaluates how an abstract space communication protocol detects, reacts to, and recovers from
ML-KEM implicit rejection events resulting from space-link ciphertext corruptions.

IMPORTANT DISCLAIMER:
This is an Abstract Spacecraft Communication Model designed for academic fault resilience research.
It is NOT an actual operational spacecraft protocol or proprietary standard (e.g. CCSDS/ECSS).

Models receiver explicitly:
  decrypt -> plaintext validity check -> command format check -> sequence number check
          -> semantic validity check -> execution

Possible Outcomes:
- KEY_MATCH: Spacecraft and Ground keys identical. Command successfully decrypted and executed.
- AUTHENTICATION_FAILURE: Cryptographic MAC / AEAD tag verification failed prior to parsing.
- FORMAT_REJECTED: Magic sync word, packet length, or framing header invalid.
- SEMANTIC_REJECTED: Subsystem ID, command opcode, parameter bounds, or CRC16 check failed.
- GARBLED_PAYLOAD_ACCEPTED: Highly improbable pseudorandom collision passing all format and semantic checks.
- SESSION_RECOVERED: Session re-established via autonomous handshake retransmission.
- SESSION_ABORTED: Handshake retries exhausted.
"""

import os
import sys
import time
import json
import struct
import hmac
import hashlib
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from algorithms.oqs_wrapper import MLKEM
from fault_injection.fault_models.fault_definitions import (
    ProtocolOutcomeClass, ProtocolFaultResult
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


def compute_crc16_ccitt(data: bytes) -> int:
    """Computes standard CRC-16-CCITT (poly 0x1021, init 0xFFFF)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def build_telecommand_frame(seq_num: int, subsystem_id: int, opcode: int, param1: int, param2: int) -> bytes:
    """
    Constructs an abstract 18-byte telecommand frame:
    - 4 bytes magic word: 0x53504143 ("SPAC")
    - 2 bytes sequence counter (uint16 big-endian)
    - 1 byte subsystem ID (1=ADCS, 2=EPS, 3=COMM)
    - 1 byte command opcode (e.g. 0x10, 0x11, 0x20)
    - 4 bytes param 1 (int32 big-endian, e.g. target attitude angle)
    - 4 bytes param 2 (uint32 big-endian, e.g. duration ms)
    - 2 bytes CRC16-CCITT
    """
    header_and_payload = struct.pack(">4sHBBii", b"SPAC", seq_num, subsystem_id, opcode, param1, param2)
    crc = compute_crc16_ccitt(header_and_payload)
    return header_and_payload + struct.pack(">H", crc)


def simulate_stream_cipher(key: bytes, plaintext: bytes) -> bytes:
    """Simulates symmetric encryption using keystream derived from session key."""
    # Deterministic Keystream = SHA256(key || block_counter)
    keystream = b""
    block = 0
    while len(keystream) < len(plaintext):
        h = hashlib.sha256(key + struct.pack(">I", block)).digest()
        keystream += h
        block += 1
    return bytes(p ^ k for p, k in zip(plaintext, keystream[:len(plaintext)]))


def evaluate_spacecraft_command_receiver(
    raw_plaintext: bytes, expected_seq_window: Tuple[int, int]
) -> Tuple[ProtocolOutcomeClass, str]:
    """
    Explicit Spacecraft Command Receiver Verification Pipeline:
    1. Plaintext validity check: length == 18 bytes
    2. Magic sync check: magic == 'SPAC' (0x53504143)
    3. Sequence number check: seq in [window_min, window_max]
    4. Command format check: valid subsystem ID (1..3) & valid opcode
    5. Semantic validity check: parameter bounds & CRC16 checksum
    6. Command execution: only if all previous checks pass!
    """
    if len(raw_plaintext) != 18:
        return ProtocolOutcomeClass.FORMAT_REJECTED, "Invalid frame length"

    magic, seq, sub_id, opcode, p1, p2, crc = struct.unpack(">4sHBBiiH", raw_plaintext)

    # 1. Framing / Magic sync check
    if magic != b"SPAC":
        return ProtocolOutcomeClass.FORMAT_REJECTED, f"Magic sync mismatch: {magic.hex()}"

    # 2. Sequence counter window check
    w_min, w_max = expected_seq_window
    if not (w_min <= seq <= w_max):
        return ProtocolOutcomeClass.FORMAT_REJECTED, f"Sequence counter {seq} outside window [{w_min}, {w_max}]"

    # 3. Subsystem and Opcode dictionary check
    valid_commands = {
        1: [0x10, 0x11, 0x12],  # ADCS: POINT_NADIR, SUN_ACQUIRE, DESATURATE
        2: [0x20, 0x21],        # EPS:  HEATER_ON, HEATER_OFF
        3: [0x30, 0x31]         # COMM: DOWNLINK_START, DOWNLINK_STOP
    }
    if sub_id not in valid_commands or opcode not in valid_commands[sub_id]:
        return ProtocolOutcomeClass.SEMANTIC_REJECTED, f"Unknown Subsystem/Opcode: sub={sub_id}, op={hex(opcode)}"

    # 4. Semantic Parameter bounds check
    if sub_id == 1:  # ADCS angles must be -180 <= p1 <= 180
        if not (-180 <= p1 <= 180):
            return ProtocolOutcomeClass.SEMANTIC_REJECTED, f"ADCS parameter out of bounds: {p1} deg"
    if p2 < 0 or p2 > 3600000:  # Timeout <= 1 hour
        return ProtocolOutcomeClass.SEMANTIC_REJECTED, f"Timeout parameter out of bounds: {p2} ms"

    # 5. Integrity Check (CRC16)
    expected_crc = compute_crc16_ccitt(raw_plaintext[:16])
    if crc != expected_crc:
        return ProtocolOutcomeClass.SEMANTIC_REJECTED, f"CRC16 checksum mismatch: {hex(crc)} != {hex(expected_crc)}"

    # 6. All checks passed: Command accepted for execution
    return ProtocolOutcomeClass.GARBLED_PAYLOAD_ACCEPTED, "Payload passed all format, sequence, and semantic checks!"


def simulate_spacecraft_protocol_campaign(
    iterations: int = 1000,
    master_seed: int = 771234,
    use_authenticated_protocol: bool = True,
    max_retries: int = 2
) -> Dict[str, Any]:
    kem = MLKEM("ML-KEM-768")
    scheduler = DeterministicScheduler(master_seed, "SPACECRAFT-PROTO-SIM")
    protocol_type_str = "Authenticated (HMAC-SHA256)" if use_authenticated_protocol else "Unauthenticated (Raw Stream)"

    print(f"\n[+] Running Abstract Spacecraft Communication Campaign (N={iterations})")
    print(f"    Protocol Mode: {protocol_type_str} | Max Retries: {max_retries}")

    tracked_outcomes = [
        ProtocolOutcomeClass.KEY_MATCH,
        ProtocolOutcomeClass.AUTHENTICATION_FAILURE,
        ProtocolOutcomeClass.FORMAT_REJECTED,
        ProtocolOutcomeClass.SEMANTIC_REJECTED,
        ProtocolOutcomeClass.GARBLED_PAYLOAD_ACCEPTED,
        ProtocolOutcomeClass.SESSION_RECOVERED,
        ProtocolOutcomeClass.SESSION_ABORTED
    ]
    counts = {p.value: 0 for p in tracked_outcomes}
    detailed_samples = []

    fault_gen = scheduler.schedule_seu_campaign(
        "ML-KEM", "ML-KEM-768", "uplink_ciphertext", kem.length_ciphertext, "uplink_rf_channel", iterations
    )

    base_seq = 5020

    for idx, fault in enumerate(fault_gen):
        seq_num = base_seq + (idx % 10)
        expected_window = (seq_num - 2, seq_num + 32)

        # Spacecraft generates long-term keypair
        sc_pk, sc_sk = kem.keypair()

        # Ground station encapsulates session key
        ground_ct, ground_ss = kem.encaps(sc_pk)

        # Telecommand payload: ADCS Point Nadir, 45 degrees, 60000 ms
        telecommand_frame = build_telecommand_frame(
            seq_num=seq_num, subsystem_id=1, opcode=0x10, param1=45, param2=60000
        )
        ground_encrypted_payload = simulate_stream_cipher(ground_ss, telecommand_frame)
        ground_mac = hmac.new(ground_ss, ground_encrypted_payload, hashlib.sha256).digest()

        # Uplink RF Channel: Radiation Single Event Upset in ML-KEM ciphertext
        received_ct = FaultInjectorEngine.inject_seu_bit_flip(ground_ct, fault.target_index, fault.bit_index)

        # Spacecraft decapsulation
        t0 = time.perf_counter_ns()
        sc_ss = kem.decaps(received_ct, sc_sk)
        keys_match = (ground_ss == sc_ss)

        outcome = ProtocolOutcomeClass.KEY_MATCH
        retries_used = 0
        details = ""

        if keys_match:
            outcome = ProtocolOutcomeClass.KEY_MATCH
            details = "Keys match: Command decrypted and executed successfully."
        else:
            # Session key mismatch occurred due to implicit rejection
            if not use_authenticated_protocol:
                # UNAUTHENTICATED PROTOCOL: Spacecraft decrypts stream using wrong session key
                decrypted_bytes = simulate_stream_cipher(sc_ss, ground_encrypted_payload)
                outcome, details = evaluate_spacecraft_command_receiver(decrypted_bytes, expected_window)
            else:
                # AUTHENTICATED PROTOCOL: Verify HMAC tag before parsing
                sc_mac = hmac.new(sc_ss, ground_encrypted_payload, hashlib.sha256).digest()
                if hmac.compare_digest(ground_mac, sc_mac):
                    # Infeasible cryptographic MAC collision
                    decrypted_bytes = simulate_stream_cipher(sc_ss, ground_encrypted_payload)
                    outcome, details = evaluate_spacecraft_command_receiver(decrypted_bytes, expected_window)
                else:
                    # Authenticated integrity failure detected at crypto layer!
                    outcome = ProtocolOutcomeClass.AUTHENTICATION_FAILURE
                    details = "MAC verification failed; command payload discarded before parsing."

                    # Autonomous session recovery via retransmission
                    recovered = False
                    for retry in range(1, max_retries + 1):
                        retries_used += 1
                        retry_ct, retry_ss = kem.encaps(sc_pk)
                        retry_sc_ss = kem.decaps(retry_ct, sc_sk)
                        if retry_ss == retry_sc_ss:
                            recovered = True
                            break

                    if recovered:
                        outcome = ProtocolOutcomeClass.SESSION_RECOVERED
                        details = f"Handshake retransmission recovered session on retry {retries_used}."
                    else:
                        outcome = ProtocolOutcomeClass.SESSION_ABORTED
                        details = f"All {max_retries} retransmission attempts exhausted."

        t1 = time.perf_counter_ns()
        latency_us = (t1 - t0) / 1000.0

        res = ProtocolFaultResult(
            fault=fault,
            ground_key=ground_ss.hex()[:16] + "...",
            spacecraft_key=sc_ss.hex()[:16] + "...",
            keys_match=keys_match,
            protocol_outcome=outcome,
            detection_latency_us=round(latency_us, 2),
            details=details
        )

        counts[outcome.value] += 1
        if len(detailed_samples) < 5:
            detailed_samples.append(res.to_dict())

    # Calculate statistics with Wilson 95% Confidence Intervals
    stats = {}
    for p_val in counts.keys():
        rate, low, high = calculate_wilson_ci(counts[p_val], iterations)
        stats[p_val] = {"count": counts[p_val], "rate_pct": rate, "ci_95": [low, high]}

    print(f"    Outcome Distribution:")
    for k, v in stats.items():
        if v["count"] > 0:
            print(f"      - {k:25s}: {v['count']:4d} ({v['rate_pct']:6.2f}%) [95% CI: {v['ci_95'][0]}% - {v['ci_95'][1]}%]")

    return {
        "protocol_mode": protocol_type_str,
        "iterations": iterations,
        "counts": counts,
        "statistics": stats,
        "sample_records": detailed_samples
    }


def main():
    print("==========================================================================")
    print(" ABSTRACT SPACECRAFT COMMUNICATION MODEL: PROTOCOL FAULT RESILIENCE")
    print(" Explicit Receiver Verification: ML-KEM-768 Uplink Single Event Upsets")
    print(" (DISCLAIMER: Research simulation model; not an actual operational protocol)")
    print("==========================================================================")

    # 1. Unauthenticated Protocol Campaign (Raw Stream)
    unauth_results = simulate_spacecraft_protocol_campaign(
        iterations=1000, master_seed=771234, use_authenticated_protocol=False, max_retries=0
    )

    # 2. Authenticated Protocol Campaign (HMAC with Autonomous Retries)
    auth_results = simulate_spacecraft_protocol_campaign(
        iterations=1000, master_seed=771234, use_authenticated_protocol=True, max_retries=2
    )

    output = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "experiment": "Abstract Spacecraft Communication Model",
            "model_pipeline": "decrypt -> plaintext validity check -> command format check -> sequence number check -> semantic validity check -> execution",
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

    print(f"\n[+] Protocol experiment results saved to: {out_file}")


if __name__ == "__main__":
    main()
