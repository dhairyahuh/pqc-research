# Recovery Analysis and Retry Contract Specification

## 1. The Autonomous Recovery Contract

In high-reliability space computing, fault tolerance requires strict mathematical distinction between **fault detection** (identifying that an anomaly occurred) and **fault recovery** (restoring correct cryptographic state). Equating detection with recovery is an engineering failure.

### Formal Recovery Contract:
1. **Pre-Condition:** An execution of `mlk_kem_dec_monitored` or an auxiliary integrity check signals a physical fault (`status == MLK_STATUS_FAULT` or `actual_crc != expected_crc`).
2. **Action Boundary:** If retry is enabled (`allow_retry == true`) and retry limit ($k_{\text{max}} = 1$) is not exceeded:
   - Clear volatile processor pipeline state and transient fault flags (`mlkem_fault_reset()`).
   - Re-execute the complete decapsulation routine from trusted immutable input buffers.
3. **Post-Condition (Transient Fault):** If the re-execution produces a valid token (`status == RESILIENCE_OK_TOKEN`), release the authentic shared secret $K$. Return `RESILIENCE_RETRY_TOKEN`.
4. **Post-Condition (Persistent Fault / Retry Exhaustion):** If the re-execution fails or produces a recurring fault token:
   - **Immediately zeroize the output key buffer:** `memset(ss, 0, 32)`.
   - Lock down the output release gate.
   - Return `RESILIENCE_FAULT_TOKEN`.
   - Log an anomaly event to spacecraft health telemetry.

---

## 2. Quantitative Metric Disaggregation

Across an adversarial campaign of 1,200 trials disaggregated into the eight threat classes, we measure four distinct outcomes:

| Metric | Formal Definition | Desired Objective | Observed (Transient) | Observed (Persistent / Input) |
| :--- | :--- | :--- | :--- | :--- |
| **Fault Detection Rate ($R_D$)** | $\frac{\text{Detected Faults}}{\text{Total Injected Faults}}$ | $100\%$ | **100.0%** (Classes 1–4, 6–7) | **100.0%** (Class 5, Class 8) |
| **Successful Recovery Rate ($R_R$)** | $\frac{\text{Correct Key Recovered}}{\text{Total Injected Faults}}$ | Maximize | **100.0%** (Single-event SEU) | **0.0%** (Cannot recover) |
| **Safe Rejection Rate ($R_S$)** | $\frac{\text{Safe Abort \& Zeroization}}{\text{Total Injected Faults}}$ | Maximize on Unrecoverable | **0.0%** (Not needed) | **100.0%** (Safe zeroization) |
| **Undetected Bad-Key Rate ($R_U$)** | $\frac{\text{Corrupted Key Released}}{\text{Total Injected Faults}}$ | **0.0% (Zero Tolerance)** | **0.0%** | **0.0%** |

### Key Scientific Insight:
- For **Class 8 (Persistent Stuck-At Faults)**: Detection Rate is **100.0%**, but Recovery Rate is **0.0%**. The safe rejection rate is **100.0%**.
- For **Class 5 (Pre-Invocation Input Corruption)**: Detection Rate is **100.0%** (when CRC is intact), but Recovery Rate is **0.0%**. Retrying corrupted memory cannot restore original ciphertext bytes.
- Reporting "100% resilience" without disaggregating recovery from safe rejection masks the fundamental fact that persistent faults permanently degrade cryptographic availability until sub-assembly reset.

---

## 3. Latency Penalties and Denial-of-Service (DoS) Analysis

We profile the wall-clock execution time on Apple Silicon across execution states:

```
[Clean Baseline Decapsulation] ──────────────────────────► 72.4 us (1.0x)

[Monitored Decapsulation (Valid CT)] ────────────────────► 72.5 us (1.0x, +0.10%)

[Recovered Transient Fault (1 Retry)] ───────────────────► 145.8 us (2.01x)

[Persistent Fault Exhaustion (Safe Abort)] ──────────────► 146.1 us (2.02x)

[Phase 7C Unpatched Invalid CT (Redundant Retry)] ───────► 145.8 us (2.01x) [UNWANTED]

[Phase 7D Patched Invalid CT (Immediate Rejection)] ─────► 72.6 us (1.00x) [RESTORED]
```

### Denial-of-Service Risk Assessment:
1. **Adversarial Fault Flooding:** If an adversary with laser or EM fault injection equipment continuously triggers transient faults at high frequency, the decapsulation engine spends 100% of its operational time in retry loops, cutting peak cryptographic transaction throughput from $\approx 13,800\,\text{ops/s}$ to $\approx 6,850\,\text{ops/s}$.
2. **Retry Clamping:** To prevent unbounded retry DoS, the architecture strictly enforces $k_{\text{max}} = 1$. Under no circumstances may an implementation loop indefinitely on recurring fault tokens.
3. **Invalid Ciphertext Decoupling:** In Phase 7D, invalid ciphertexts do not trigger retries, guaranteeing that unauthenticated network traffic cannot degrade legitimate spacecraft command throughput.

---

## 4. Output Secret Release Barrier Verification

To guarantee that candidate shared secrets are never exposed prior to full multi-rail verification, the output path enforces the following invariants:

1. **Zeroization on Fault:** Whenever `status != RESILIENCE_OK_TOKEN` and `status != RESILIENCE_RETRY_TOKEN` and `status != RESILIENCE_REJECT_TOKEN`, the output buffer `ss` is actively overwritten with zeros (`memset(ss, 0, 32)`).
2. **Dual-Rail Discrepancy Suppression:** In `mlk_kem_dec_monitored`, if `fail != fail_chk`, line 490 overrides `fail = 0xFF`, forcing `mlk_ct_cmov_zero(ss, kr, 32, fail)` to unconditionally retain the pseudorandom rejection key $K_{\text{rej}}$ and completely overwrite candidate key $K_{\text{cand}}$.
3. **Memory Barrier Enforcement:** Status verification employs GCC/Clang memory barriers (`__asm__ volatile("" ::: "memory")`) preventing the compiler from reordering ciphertext write-backs across the verification boundary.
