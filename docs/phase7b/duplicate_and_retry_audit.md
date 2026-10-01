# Phase 7B Independent Audit: Duplicate Execution and Transient Retry Mechanics

**Auditor:** Independent Fault Mitigation Auditor  
**Target:** Full Duplicate Decapsulation (DMR) & Autonomous Retry Logic  
**Date:** October 2026  

---

## 1. Audit of Full Duplicate Decapsulation (DMR)

Phase 6 and Phase 7 evaluate DMR as Candidate A1 / Config 4:
```c
static uint32_t decaps_duplicate(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    uint8_t ss1[SS_BYTES], ss2[SS_BYTES];
    mlkem768_dec(ss1, ct, sk);
    mlkem768_dec(ss2, ct, sk);
    if (memcmp(ss1, ss2, SS_BYTES) != 0) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    memcpy(ss, ss1, SS_BYTES);
    return RESILIENCE_OK_TOKEN;
}
```

### Architectural Analysis & Common-Mode Weaknesses

1. **Shared State and Memory:**
   - Both passes read from the identical input pointers `const uint8_t *ct` and `const uint8_t *sk`.
   - The memory buffers are not duplicated prior to execution.
   - Any corruption residing in `ct` or `sk` before invocation is completely invisible to DMR (**0.0% detection**).
2. **Computational Overhead:**
   - Because ML-KEM-768 decapsulation is deterministic and arithmetic-heavy, executing it twice requires double the CPU cycles:
     - Baseline: 43.07 µs
     - Duplicate Decapsulation: 86.17 µs (**+100.1% overhead**)
   - Stack memory is doubled (~7.6 KB) due to allocating dual 32-byte shared secret buffers and internal IND-CPA structures across two passes.
3. **Transient Fault Coverage:**
   - For an independent single-event transient (SET) that occurs during only one of the two execution passes, DMR achieves **96.7% to 100.0% detection**.
   - If an SET occurs in both passes (e.g. during a high-flux solar particle event), DMR fails.

---

## 2. Audit of the Controlled Transient Retry Mechanism

In Layer 4 of the Layered Architecture:
```c
if (status != RESILIENCE_OK_TOKEN && allow_retry) {
    mlkem_fault_reset();
    dec_res = mlkem768_dec(ss, ct, sk);
    ...
    if (status == RESILIENCE_OK_TOKEN) {
        return RESILIENCE_RETRY_TOKEN;
    }
    memset(ss, 0, SS_BYTES);
    return RESILIENCE_FAULT_TOKEN;
}
```

### Critical Auditor Analysis

1. **Retry Trigger:**
   - Retry is triggered if and only if Layer 2 (NTT invariant) or Layer 3 (Multi-rail gate) flags a fault on a ciphertext that successfully passed Layer 1 (CRC32).
   - If Layer 1 fails (CRC mismatch), **no retry is attempted**, and execution is aborted immediately (`RESILIENCE_FAULT_TOKEN`). This prevents infinite re-decapsulation of corrupted ciphertext buffers.
2. **Transient vs Persistent Fault Demarcation:**
   - The harness models a transient fault by clearing the injection hook (`mlkem_fault_reset()`) before the retry pass.
   - The retry pass executes cleanly, producing the authentic shared secret $ss_{\text{expected}}$, returning `RESILIENCE_RETRY_TOKEN`.
   - **Persistent Fault Behavior:** If the fault is persistent (Class 8), `mlkem_fault_reset()` does not clear a hardware stuck-at condition; the retry pass fails again, and the function safely aborts with `RESILIENCE_FAULT_TOKEN` and zeroes the output buffer.
3. **Can Retry Conceal an Incorrect Result?**
   - No. In ML-KEM-768 decapsulation, operations are fully deterministic. A transient fault will produce an incorrect key; on retry under clean conditions, the deterministic calculation yields the unique mathematically correct shared secret.

---

## 3. Summary of Comparison

| Dimension | Full Duplicate Decapsulation (DMR) | Layered Defense + 1-Shot Retry |
| :--- | :--- | :--- |
| **Normal Latency (Fault-Free)** | **86.17 µs (+100.1%)** | **52.25 µs (+21.3%)** |
| **Latency Under Transient SEU** | 86.17 µs (Detects & Aborts) | ~95.0 µs (Detects & Recovers) |
| **Input Buffer SEU Detection** | **0.0% (Common-Mode Blind Spot)** | **100.0% (Via Pre-Invocation CRC32)** |
| **Persistent Stuck-At Detection** | **0.0% (Common-Mode Blind Spot)** | **100.0% (Via Polynomial Invariant)** |
| **Stack Allocation** | ~7.6 KB | ~4.1 KB |
