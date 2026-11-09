# ASTRA-Sec Phase 3: Cryptographic Fault Campaign Results and SDC Suppression

## 1. Threat Model & Fault Injection Mechanics

The Layer 4 fault-resilient execution subsystem is designed to protect space-borne cryptographic operations against radiation-induced soft errors:
1. **Single-Event Upsets (SEU)**: Transient bit flips in processor registers, ALU intermediate values, or cache during NTT butterfly transformations.
2. **Persistent Register Faults**: Stuck bits in registers or memory locations causing recurring errors across iterations.
3. **Twiddle-Factor ROM Corruption**: Persistent single-bit or multi-bit corruption in precomputed twiddle factor tables ($ZETAS$).
4. **Wire / Memory Payload Corruption**: In-transit or DMA buffer corruption targeting ciphertext coefficients or signature blocks.

The primary safety requirement of ASTRA-Sec is **Zero Silent Data Corruption ($SDC = 0$)**: corrupted cryptographic computations must either be recovered locally within a bounded retry budget ($K \le 2$) or deterministically fail-stop, never emitting compromised plaintexts or invalid key agreements.

---

## 2. Experimental Campaign: Group J (`EXP-J01-FAULT-SEU`)

### 2.1. Parameter Configuration
- **Scenario ID**: `EXP-J01-FAULT-SEU`
- **Baseline Type**: `FULL_ASTRA_SEC`
- **Total Messages Dispatched**: 10
- **Payload Size**: 512 B
- **Fault Type**: Single-Event Upset (SEU bit flip)
- **Fault Target**: Cryptographic payload / signature envelope in transit
- **Injection Probability**: $P_{inj} = 1.0$ (100% of messages subjected to bit flips)
- **Deterministic Seed**: 9009

---

### 2.2. Empirical Measurements & Telemetry

| Metric | Measured Value | Standard Target | Status |
| :--- | :--- | :--- | :--- |
| **Total Injected Faults** | 10 | 10 | Complete |
| **Faults Detected** | 10 | 10 | **100.0% Detection** |
| **Detection Coverage** | **100.0%** | $\ge 99.0\%$ | **PASS** |
| **Silent Data Corruption (SDC)** | **0** | **0** | **PASS** |
| **Delivered / Corrupted Plaintexts** | 0 | 0 | **PASS** |
| **Detection Mechanism Triggered** | `SignatureVerificationError` (ML-DSA-65) | Explicit Exception | Verified |
| **Mean End-to-End Latency** | 12.92 ms | N/A (Failed Safe) | Recorded |
| **Mean CPU Utilization** | 14.96% | < 50.0% | Normal |
| **Peak RSS Memory** | 95.03 MB | < 250 MB | Bounded |

---

### 2.3. Low-Level Invariant & Rollback Analysis

In complementary native C fault experiments (Phases 7G–7K and `experiments/fault_injection/mlkem768_internal_fault_experiment.c`):
1. **NTT Invariant Checking**:
   During forward and inverse Number Theoretic Transforms, the native C kernel executes the Montgomery butterfly relation:
   $$r \equiv t \cdot \zeta \pmod q$$
   Injecting single-bit SEUs into intermediate coefficients triggers immediate invariant violations at the sub-word monitoring stage.
2. **Snapshot Rollback ($K \le 2$)**:
   When an SEU occurs during transient execution, the butterfly engine rolls back coefficient registers to the pre-transform snapshot and re-executes.
3. **Fail-Stop Containment**:
   When persistent stuck faults or twiddle corruptions prevent recovery after $K=2$ retries, the engine aborts the NTT, zeros intermediate registers, and triggers deterministic implicit rejection or fail-stop signaling. No corrupted shared secret or plaintexts are ever released to the application layer.
