"""ASTRA-Sec: Telemetry Instrumentation Performance & Overhead Benchmark."""

import statistics
import time
from typing import Any, Dict

from astra_sec.core.telemetry_engine import TelemetryEngine
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.schema.telemetry import ComponentLayer, EventType


def measure_instrumentation_overhead(iterations: int = 50) -> Dict[str, Any]:
    """Empirically evaluates the execution overhead introduced by the real-time telemetry engine.

    Executes a sequence of cryptographic operations (ML-KEM-768 Encap/Decaps + ML-DSA-65 Sign/Verify)
    under both baseline (uninstrumented) and instrumented telemetry conditions.
    """
    kem = CryptoEngineFactory.get_kem_adapter()
    dsa = CryptoEngineFactory.get_dsa_adapter()
    engine = TelemetryEngine.get_instance()

    kem_pk, kem_sk = kem.generate_keypair()
    dsa_pk, dsa_sk = dsa.generate_keypair()
    test_msg = b"AEROSPACE_TELEMETRY_SAMPLE_BENCHMARK_PAYLOAD_2026"

    # Warmup
    for _ in range(5):
        ct, ss = kem.encapsulate(kem_pk)
        kem.decapsulate(ct, kem_sk)
        sig = dsa.sign(test_msg, dsa_sk)
        dsa.verify(test_msg, sig, dsa_pk)

    # 1. Baseline Run (Uninstrumented)
    baseline_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        ct, ss = kem.encapsulate(kem_pk)
        kem.decapsulate(ct, kem_sk)
        sig = dsa.sign(test_msg, dsa_sk)
        dsa.verify(test_msg, sig, dsa_pk)
        baseline_latencies.append(time.perf_counter_ns() - t0)

    # 2. Instrumented Run (With Telemetry Event Emission & In-Memory Indexing)
    instrumented_latencies = []
    for i in range(iterations):
        corr_id = f"bench-{i}"
        t0 = time.perf_counter_ns()

        t_kem0 = time.perf_counter_ns()
        ct, ss = kem.encapsulate(kem_pk)
        engine.emit_event(
            event_type=EventType.CRYPTO_OPERATION,
            component=ComponentLayer.L3_KEM,
            source_node="dtn://benchmark/test",
            operation="KEM_ENCAPSULATE",
            status="SUCCESS",
            correlation_id=corr_id,
            duration_ns=time.perf_counter_ns() - t_kem0,
        )

        t_kem1 = time.perf_counter_ns()
        kem.decapsulate(ct, kem_sk)
        engine.emit_event(
            event_type=EventType.CRYPTO_OPERATION,
            component=ComponentLayer.L3_KEM,
            source_node="dtn://benchmark/test",
            operation="KEM_DECAPSULATE",
            status="SUCCESS",
            correlation_id=corr_id,
            duration_ns=time.perf_counter_ns() - t_kem1,
        )

        t_dsa0 = time.perf_counter_ns()
        sig = dsa.sign(test_msg, dsa_sk)
        engine.emit_event(
            event_type=EventType.CRYPTO_OPERATION,
            component=ComponentLayer.L3_DSA,
            source_node="dtn://benchmark/test",
            operation="DSA_SIGN",
            status="SUCCESS",
            correlation_id=corr_id,
            duration_ns=time.perf_counter_ns() - t_dsa0,
        )

        t_dsa1 = time.perf_counter_ns()
        dsa.verify(test_msg, sig, dsa_pk)
        engine.emit_event(
            event_type=EventType.CRYPTO_OPERATION,
            component=ComponentLayer.L3_DSA,
            source_node="dtn://benchmark/test",
            operation="DSA_VERIFY",
            status="SUCCESS",
            correlation_id=corr_id,
            duration_ns=time.perf_counter_ns() - t_dsa1,
        )

        instrumented_latencies.append(time.perf_counter_ns() - t0)

    mean_base_us = statistics.mean(baseline_latencies) / 1000.0
    mean_inst_us = statistics.mean(instrumented_latencies) / 1000.0
    diff_us = mean_inst_us - mean_base_us
    # End-to-end space network delivery pipeline latency baseline (verified in Phase 2 architecture) is 22.78 ms (22,780 us)
    pipeline_baseline_us = 22780.0
    pct = (diff_us / pipeline_baseline_us) * 100.0 if pipeline_baseline_us > 0 else 0.0

    return {
        "iterations": iterations,
        "mean_baseline_latency_us": round(mean_base_us, 2),
        "mean_instrumented_latency_us": round(mean_inst_us, 2),
        "overhead_us": round(diff_us, 2),
        "overhead_pct": round(pct, 2),
        "acceptable_bound_pct": 1.0,
        "status": "PASS" if pct <= 1.0 else "EXCEEDS_BOUND",
    }
