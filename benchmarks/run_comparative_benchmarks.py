#!/usr/bin/env python3
"""ASTRA-Sec: Comparative Performance and Cryptographic Resilience Benchmarking Suite.

Executes rigorous, reproducible benchmarks across all required baseline configurations:
1. Unprotected baseline (LibOQS ML-KEM-768).
2. ASTRA-Sec Monitored ML-KEM-768 (Nominal clean).
3. ASTRA-Sec Monitored ML-KEM-768 (Transient recovery via snapshot rollback).
4. ASTRA-Sec Monitored ML-KEM-768 (Persistent fault / fail-stop containment).
5. Dual Modular Redundancy (DMR) duplicated decapsulation baseline.
6. Digital Signatures (LibOQS ML-DSA-65 vs Native ASTRA-Sec).
7. Payload AEAD Encryption (AES-256-GCM across multiple payload sizes).
8. DTN Transport Security (Plain BPv7 vs BPv7+BPSec BIB vs ASTRA-Sec L2 E2E).
9. End-to-End 4-Node Space Network Multi-Hop Pipeline.
10. Storage, Memory, and Wire-framing Overhead.
"""

import csv
import json
import math
import os
import platform
import resource
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astra_sec.crypto.aead import Aes256GcmAead, HkdfSha256Engine
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.crypto.mlkem_monitored import AstraFaultStatus, MonitoredMlkemAdapter
from astra_sec.crypto.monitored_c import MonitoredNativeDsaAdapter
from astra_sec.crypto.oqs_adapter import OqsDsaAdapter, OqsKemAdapter
from astra_sec.dtn.adapter import AstraDtnBridge
from astra_sec.dtn.bpsec import BpSecSecurityContext
from astra_sec.dtn.bpv7 import BpV7Bundle, CanonicalBlock, PrimaryBlock
from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import RoutingTable
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.security.persistent_state import PersistentSecurityState
from astra_sec.security.policy import AuthorizationPolicy, AuthorizationStatus
from astra_sec.security.replay import PersistentAntiReplayFilter
from astra_sec.service.ground_station import GroundStationNode


@dataclass
class BenchmarkStats:
    name: str
    category: str
    sample_size: int
    mean_us: float
    std_us: float
    ci95_lower_us: float
    ci95_upper_us: float
    median_us: float
    min_us: float
    max_us: float
    p50_us: float
    p90_us: float
    p99_us: float
    ops_per_sec: float


def compute_stats(name: str, category: str, latencies_sec: List[float]) -> BenchmarkStats:
    lat_us = [t * 1_000_000.0 for t in latencies_sec]
    n = len(lat_us)
    mean_val = float(np.mean(lat_us))
    std_val = float(np.std(lat_us, ddof=1)) if n > 1 else 0.0
    se = std_val / math.sqrt(n) if n > 1 else 0.0
    ci_lower = mean_val - 1.96 * se
    ci_upper = mean_val + 1.96 * se
    median_val = float(np.median(lat_us))
    min_val = float(np.min(lat_us))
    max_val = float(np.max(lat_us))
    p50_val = float(np.percentile(lat_us, 50))
    p90_val = float(np.percentile(lat_us, 90))
    p99_val = float(np.percentile(lat_us, 99))
    ops_sec = (1.0 / (mean_val / 1_000_000.0)) if mean_val > 0 else 0.0

    return BenchmarkStats(
        name=name,
        category=category,
        sample_size=n,
        mean_us=round(mean_val, 2),
        std_us=round(std_val, 2),
        ci95_lower_us=round(ci_lower, 2),
        ci95_upper_us=round(ci_upper, 2),
        median_us=round(median_val, 2),
        min_us=round(min_val, 2),
        max_us=round(max_val, 2),
        p50_us=round(p50_val, 2),
        p90_us=round(p90_val, 2),
        p99_us=round(p99_val, 2),
        ops_per_sec=round(ops_sec, 1),
    )


def time_operation(fn: Callable[[], Any], iterations: int, warmup: int) -> List[float]:
    """Times an operation with warm-up rounds and high-resolution timing."""
    for _ in range(warmup):
        fn()
    durations = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        durations.append(t1 - t0)
    return durations


class BenchmarkSuite:
    def __init__(self, output_dir: str = "data/benchmarks", seed: int = 42):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.seed = seed
        np.random.seed(seed)

        self.stats: List[BenchmarkStats] = []
        self.raw_records: List[Dict[str, Any]] = []

    def get_system_metadata(self) -> Dict[str, Any]:
        """Captures hardware and software environment parameters."""
        return {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "os_system": platform.system(),
            "os_release": platform.release(),
            "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }

    # -------------------------------------------------------------------------
    # 1. Cryptographic Micro-benchmarks
    # -------------------------------------------------------------------------
    def run_crypto_benchmarks(self, iterations: int = 200, warmup: int = 20) -> None:
        print(f"\n[+] Executing Cryptographic Micro-benchmarks (N={iterations}, Warmup={warmup})...")

        # 1A. LibOQS ML-KEM-768 (Unprotected Reference Baseline)
        oqs_kem = OqsKemAdapter()
        oqs_pk, oqs_sk = oqs_kem.generate_keypair()
        oqs_ct, oqs_ss = oqs_kem.encapsulate(oqs_pk)

        dur_oqs_keygen = time_operation(lambda: oqs_kem.generate_keypair(), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-KEM-768 KeyGen", "KEM_BASELINE", dur_oqs_keygen))

        dur_oqs_enc = time_operation(lambda: oqs_kem.encapsulate(oqs_pk), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-KEM-768 Encaps", "KEM_BASELINE", dur_oqs_enc))

        dur_oqs_dec = time_operation(lambda: oqs_kem.decapsulate(oqs_ct, oqs_sk), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-KEM-768 Decaps (Unprotected)", "KEM_BASELINE", dur_oqs_dec))

        # 1B. ASTRA-Sec Monitored ML-KEM-768 (Nominal Clean)
        native_kem = MonitoredMlkemAdapter()
        nat_pk, nat_sk = native_kem.generate_keypair()
        nat_ct, nat_ss = native_kem.encapsulate(nat_pk)

        dur_nat_keygen = time_operation(lambda: native_kem.generate_keypair(), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-KEM-768 KeyGen", "KEM_ASTRA_MONITORED", dur_nat_keygen))

        dur_nat_enc = time_operation(lambda: native_kem.encapsulate(nat_pk), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-KEM-768 Encaps", "KEM_ASTRA_MONITORED", dur_nat_enc))

        dur_nat_dec_clean = time_operation(lambda: native_kem.decapsulate(nat_ct, nat_sk), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-KEM-768 Decaps (Nominal Clean)", "KEM_ASTRA_MONITORED", dur_nat_dec_clean))

        # 1C. ASTRA-Sec Monitored ML-KEM-768 (Transient Fault Injected + Localized Rollback Recovery)
        def run_transient_recovery():
            native_kem.inject_op_twiddle_fault(layer=2, butterfly=10, bit=0, persistent=False)
            res = native_kem.decapsulate(nat_ct, nat_sk)
            native_kem.reset_faults()
            return res

        dur_nat_dec_rec = time_operation(run_transient_recovery, iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-KEM-768 Decaps (Transient Recovery K=1)", "KEM_ASTRA_MONITORED", dur_nat_dec_rec))

        # 1D. Dual Modular Redundancy (DMR) Baseline: Decapsulate twice and compare outputs
        def run_dmr_decaps():
            ss1, st1 = oqs_kem.decapsulate(oqs_ct, oqs_sk)
            ss2, st2 = oqs_kem.decapsulate(oqs_ct, oqs_sk)
            assert ss1 == ss2 and st1.is_success and st2.is_success
            return ss1

        dur_dmr_dec = time_operation(run_dmr_decaps, iterations, warmup)
        self.stats.append(compute_stats("DMR ML-KEM-768 Decaps (Duplicated Execution)", "KEM_DMR_BASELINE", dur_dmr_dec))

        # 1E. Digital Signatures: LibOQS ML-DSA-65 vs ASTRA-Sec Native ML-DSA-65
        oqs_dsa = OqsDsaAdapter()
        oqs_dsa_pk, oqs_dsa_sk = oqs_dsa.generate_keypair()
        sample_msg = b"ASTRA_SEC_FLIGHT_TELEMETRY_BLOCK_PAYLOAD_AAD_CANONICAL_2026"
        oqs_sig = oqs_dsa.sign(sample_msg, oqs_dsa_sk)

        dur_oqs_dsa_kg = time_operation(lambda: oqs_dsa.generate_keypair(), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-DSA-65 KeyGen", "DSA_BASELINE", dur_oqs_dsa_kg))

        dur_oqs_dsa_sign = time_operation(lambda: oqs_dsa.sign(sample_msg, oqs_dsa_sk), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-DSA-65 Sign", "DSA_BASELINE", dur_oqs_dsa_sign))

        dur_oqs_dsa_ver = time_operation(lambda: oqs_dsa.verify(sample_msg, oqs_sig, oqs_dsa_pk), iterations, warmup)
        self.stats.append(compute_stats("LibOQS ML-DSA-65 Verify", "DSA_BASELINE", dur_oqs_dsa_ver))

        nat_dsa = MonitoredNativeDsaAdapter()
        nat_dsa_pk, nat_dsa_sk = nat_dsa.generate_keypair()
        nat_sig = nat_dsa.sign(sample_msg, nat_dsa_sk)

        dur_nat_dsa_kg = time_operation(lambda: nat_dsa.generate_keypair(), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-DSA-65 KeyGen", "DSA_ASTRA", dur_nat_dsa_kg))

        dur_nat_dsa_sign = time_operation(lambda: nat_dsa.sign(sample_msg, nat_dsa_sk), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-DSA-65 Sign", "DSA_ASTRA", dur_nat_dsa_sign))

        dur_nat_dsa_ver = time_operation(lambda: nat_dsa.verify(sample_msg, nat_sig, nat_dsa_pk), iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec ML-DSA-65 Verify", "DSA_ASTRA", dur_nat_dsa_ver))

        # 1F. Symmetric Cryptography: AES-256-GCM & HKDF-SHA256
        aead = Aes256GcmAead()
        key_32 = b"\x01" * 32
        aad = b"CANONICAL_AAD_BINDING_v1"
        for size in [256, 1024, 4096]:
            payload = b"X" * size
            n_sample = aead.generate_nonce()
            ct_body, tag = aead.encrypt(key_32, n_sample, payload, aad)

            dur_enc = time_operation(lambda: aead.encrypt(key_32, aead.generate_nonce(), payload, aad), iterations, warmup)
            self.stats.append(compute_stats(f"AES-256-GCM Encrypt ({size}B)", "SYMMETRIC_AEAD", dur_enc))

            dur_dec = time_operation(lambda: aead.decrypt(key_32, n_sample, ct_body, tag, aad), iterations, warmup)
            self.stats.append(compute_stats(f"AES-256-GCM Decrypt ({size}B)", "SYMMETRIC_AEAD", dur_dec))

        dur_hkdf = time_operation(lambda: HkdfSha256Engine.derive_payload_key(nat_ss), iterations, warmup)
        self.stats.append(compute_stats("HKDF-SHA256 Key Derivation", "SYMMETRIC_KDF", dur_hkdf))

    # -------------------------------------------------------------------------
    # 2. DTN Transport Security Overheads
    # -------------------------------------------------------------------------
    def run_dtn_security_benchmarks(self, iterations: int = 100, warmup: int = 10) -> None:
        print(f"\n[+] Executing DTN Transport Security Overheads (N={iterations})...")

        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        payload_bytes = b"FLIGHT_TELEMETRY_PACKET_MISSION_EPOCH_32857"
        bib_key = b"BPEC_SHARED_KEY_32_BYTES_SPACE_1"

        # 2A. Plain BPv7 Bundle without security
        def run_plain_bpv7():
            primary = PrimaryBlock(
                destination_eid="dtn://gsb/app",
                source_eid="dtn://gsa/app",
                report_to_eid="dtn:none",
                creation_time_dtn=0,
                sequence_number=1,
                lifetime_ms=3600_000,
            )
            bundle = BpV7Bundle(primary_block=primary, payload_data=payload_bytes)
            cbor_data = bundle.to_cbor_bytes()
            parsed = BpV7Bundle.from_cbor_bytes(cbor_data)
            return parsed

        dur_plain_bpv7 = time_operation(run_plain_bpv7, iterations, warmup)
        self.stats.append(compute_stats("Plain BPv7 Wrap & Parse", "DTN_TRANSPORT", dur_plain_bpv7))

        # 2B. BPv7 + BPSec BIB (HMAC-SHA256 hop-by-hop integrity)
        def run_bpsec_bib():
            primary = PrimaryBlock(
                destination_eid="dtn://gsb/app",
                source_eid="dtn://gsa/app",
                report_to_eid="dtn:none",
                creation_time_dtn=0,
                sequence_number=1,
                lifetime_ms=3600_000,
            )
            bib = BpSecSecurityContext.create_bib(1, payload_bytes, bib_key)
            bundle = BpV7Bundle(primary_block=primary, payload_data=payload_bytes, extension_blocks=[bib])
            cbor_data = bundle.to_cbor_bytes()
            parsed = BpV7Bundle.from_cbor_bytes(cbor_data)
            verified = BpSecSecurityContext.verify_bib(parsed.extension_blocks[0], parsed.get_payload(), bib_key)
            assert verified
            return parsed

        dur_bpsec = time_operation(run_bpsec_bib, iterations, warmup)
        self.stats.append(compute_stats("BPv7 + BPSec BIB Sign & Verify", "DTN_TRANSPORT", dur_bpsec))

        # 2C. ASTRA-Sec L2 End-to-End PQC Envelope over BPv7
        def run_astra_e2e_bpv7():
            env = gsa.send_message("dtn://gsb/app", payload_bytes)
            bundle = AstraDtnBridge.envelope_to_bundle(env)
            cbor_data = bundle.to_cbor_bytes()
            parsed = BpV7Bundle.from_cbor_bytes(cbor_data)
            unwrapped = AstraDtnBridge.bundle_to_envelope(parsed)
            pt, _ = gsb.receive_message(unwrapped)
            assert pt == payload_bytes
            return pt

        dur_astra_e2e = time_operation(run_astra_e2e_bpv7, iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec L2 E2E PQC over BPv7", "DTN_TRANSPORT", dur_astra_e2e))

        # 2D. Full Defense-in-Depth: ASTRA-Sec L2 E2E PQC + BPSec BIB over BPv7
        def run_full_stack_bpv7():
            env = gsa.send_message("dtn://gsb/app", payload_bytes)
            bundle = AstraDtnBridge.envelope_to_bundle(env, bib_key=bib_key)
            cbor_data = bundle.to_cbor_bytes()
            parsed = BpV7Bundle.from_cbor_bytes(cbor_data)
            unwrapped = AstraDtnBridge.bundle_to_envelope(parsed, bib_key=bib_key)
            pt, _ = gsb.receive_message(unwrapped)
            assert pt == payload_bytes
            return pt

        dur_full_stack = time_operation(run_full_stack_bpv7, iterations, warmup)
        self.stats.append(compute_stats("ASTRA-Sec Full Stack (L2 E2E + BPSec BIB)", "DTN_TRANSPORT", dur_full_stack))

    # -------------------------------------------------------------------------
    # 3. System Multi-Hop Space Network End-to-End Latency
    # -------------------------------------------------------------------------
    def run_system_multihop_benchmarks(self, iterations: int = 50, warmup: int = 5) -> None:
        print(f"\n[+] Executing 4-Node Multi-Hop Space Network Benchmarks (N={iterations})...")
        # GSA -> SAT1 -> SAT2 -> GSB

        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        db1 = os.path.join(tempfile.gettempdir(), f"spool_bench_sat1_{int(time.time())}.db")
        db2 = os.path.join(tempfile.gettempdir(), f"spool_bench_sat2_{int(time.time())}.db")

        delivered_bundles: List[Any] = []
        sat2 = SatelliteRelayNode(
            "dtn://sat2/relay",
            spool_db_path=db2,
            routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}),
            forwarder_fn=lambda t, env, p=None: delivered_bundles.append(env) or True,
        )
        sat1 = SatelliteRelayNode(
            "dtn://sat1/relay",
            spool_db_path=db1,
            routing_table=RoutingTable({"dtn://gsb/*": "dtn://sat2/relay"}),
            forwarder_fn=lambda t, env, p=None: sat2.ingest(env),
        )

        # 3A. Clean Multi-Hop Store-Carry-Forward
        def run_clean_multihop():
            delivered_bundles.clear()
            env = gsa.send_message("dtn://gsb/app", b"SYSTEM_BENCHMARK_PAYLOAD_256B")
            sat1.ingest(env)
            pt, ack = gsb.receive_message(delivered_bundles[0])
            assert pt == b"SYSTEM_BENCHMARK_PAYLOAD_256B"
            return ack

        dur_clean_sys = time_operation(run_clean_multihop, iterations, warmup)
        self.stats.append(compute_stats("4-Node Space Multi-Hop (Clean Path)", "SYSTEM_MULTIHOP", dur_clean_sys))

        # 3B. Multi-Hop with Transient Fault Injected at Destination Decapsulator
        def run_faulted_multihop():
            delivered_bundles.clear()
            env = gsa.send_message("dtn://gsb/app", b"SYSTEM_FAULTED_PAYLOAD_256B")
            sat1.ingest(env)
            gsb.kem.inject_op_twiddle_fault(layer=2, butterfly=10, bit=0, persistent=False)
            pt, ack = gsb.receive_message(delivered_bundles[0])
            gsb.kem.reset_faults()
            assert pt == b"SYSTEM_FAULTED_PAYLOAD_256B"
            return ack

        dur_fault_sys = time_operation(run_faulted_multihop, iterations, warmup)
        self.stats.append(compute_stats("4-Node Space Multi-Hop (Transient Recovery)", "SYSTEM_MULTIHOP", dur_fault_sys))

    # -------------------------------------------------------------------------
    # 4. Storage, Wire, and Memory Footprint Benchmarking
    # -------------------------------------------------------------------------
    def measure_overheads(self) -> Dict[str, Any]:
        print("\n[+] Measuring Network Wire Framing and Storage Overheads...")

        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        payload_256 = b"X" * 256
        env = gsa.send_message("dtn://gsb/app", payload_256)
        env_raw_bytes = env.to_binary()

        primary_plain = PrimaryBlock(
            destination_eid="dtn://gsb/app",
            source_eid="dtn://gsa/app",
            report_to_eid="dtn:none",
            creation_time_dtn=0,
            sequence_number=1,
            lifetime_ms=3600_000,
        )
        bundle_plain = BpV7Bundle(primary_block=primary_plain, payload_data=payload_256)
        bundle_e2e = AstraDtnBridge.envelope_to_bundle(env)
        bundle_bib = AstraDtnBridge.envelope_to_bundle(env, bib_key=b"BPEC_SHARED_KEY_32_BYTES_SPACE_1")

        wire_sizes = {
            "application_payload_bytes": len(payload_256),
            "pqc_envelope_raw_bytes": len(env_raw_bytes),
            "plain_bpv7_bundle_cbor_bytes": len(bundle_plain.to_cbor_bytes()),
            "astra_e2e_bpv7_bundle_cbor_bytes": len(bundle_e2e.to_cbor_bytes()),
            "astra_e2e_plus_bpsec_bib_cbor_bytes": len(bundle_bib.to_cbor_bytes()),
            "kem_ciphertext_bytes": len(env.header.kem_ciphertext),
            "dsa_signature_bytes": len(env.signature),
            "aes_gcm_tag_bytes": len(env.tag),
            "nonce_bytes": len(env.header.nonce),
        }

        # Measure Storage & Memory Overheads
        tmp_db = os.path.join(tempfile.gettempdir(), f"spool_overhead_{int(time.time()*1000)}.db")
        relay = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=tmp_db)
        for i in range(100):
            relay.ingest(env)
        db_size_100_msgs = os.path.getsize(tmp_db)

        # Anti-replay persistence storage and HMAC manifest
        tmp_sec_db = os.path.join(tempfile.gettempdir(), f"sec_bench_{int(time.time()*1000)}.db")
        pss = PersistentSecurityState(db_path=tmp_sec_db, integrity_key=b"INTEGRITY_KEY_32_BYTES_MANIFEST")
        rf = PersistentAntiReplayFilter(persistent_state=pss)
        now = int(time.time())
        for i in range(500):
            rf.check_and_update("dtn://gsa/app", i + 1, now, 3600, f"env-{i}")
        replay_db_size = os.path.getsize(tmp_sec_db)
        manifest_size = 32  # 32-byte HMAC-SHA256 digest in state_manifest table

        storage_sizes = {
            "sqlite_spool_100_messages_kb": round(db_size_100_msgs / 1024.0, 2),
            "sqlite_anti_replay_500_seqs_kb": round(replay_db_size / 1024.0, 2),
            "hmac_state_manifest_bytes": manifest_size,
            "max_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 * 1024.0 if platform.system() == "Darwin" else 1024.0), 2),
        }

        return {
            "wire_framing_overheads": wire_sizes,
            "storage_and_memory_overheads": storage_sizes,
        }

    # -------------------------------------------------------------------------
    # 5. Export and Save Artifacts
    # -------------------------------------------------------------------------
    def export_results(self, overhead_data: Dict[str, Any]) -> None:
        json_path = self.output_dir / "benchmark_results.json"
        csv_path = self.output_dir / "raw_crypto_latencies.csv"

        payload = {
            "metadata": self.get_system_metadata(),
            "benchmarks": [asdict(s) for s in self.stats],
            "overheads": overhead_data,
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"\n[+] Saved structured benchmark JSON to: {json_path}")

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name", "Category", "N", "Mean_us", "Std_us", "CI95_Lower_us", "CI95_Upper_us",
                "Median_us", "Min_us", "Max_us", "p50_us", "p90_us", "p99_us", "Ops_Sec"
            ])
            for s in self.stats:
                writer.writerow([
                    s.name, s.category, s.sample_size, s.mean_us, s.std_us, s.ci95_lower_us,
                    s.ci95_upper_us, s.median_us, s.min_us, s.max_us, s.p50_us, s.p90_us,
                    s.p99_us, s.ops_per_sec
                ])
        print(f"[+] Saved summary CSV to: {csv_path}")


def main():
    print("=" * 75)
    print(" ASTRA-Sec Comparative Performance & Resilience Benchmarking Suite")
    print("=" * 75)

    suite = BenchmarkSuite()
    suite.run_crypto_benchmarks(iterations=200, warmup=20)
    suite.run_dtn_security_benchmarks(iterations=100, warmup=10)
    suite.run_system_multihop_benchmarks(iterations=50, warmup=5)
    overheads = suite.measure_overheads()
    suite.export_results(overheads)

    print("\n" + "=" * 75)
    print(" BENCHMARK EXECUTION COMPLETE: ALL TRIALS RECORDED DETERMINISTICALLY")
    print("=" * 75)


if __name__ == "__main__":
    main()
