# Phase 6B: Duplicate Execution Robustness and Common-Mode Failure Audit

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6B — Independent Adversarial Validation and Scientific Audit  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Candidate A1 Architecture and Assumptions

Candidate A1 implements Dual-Modular Redundancy (DMR) around the decapsulation API:
```c
static uint32_t decaps_duplicate(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    uint8_t ss1[SS_BYTES], ss2[SS_BYTES];
    mlkem768_dec(ss1, ct, sk);
    mlkem768_dec(ss2, ct, sk);
    if (ct_memcmp(ss1, ss2, SS_BYTES) != 0) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    memcpy(ss, ss1, SS_BYTES);
    return RESILIENCE_OK_TOKEN;
}
```

The underlying hypothesis was that duplicate decapsulation catches internal faults before an out-of-sync session key is committed.

---

## 2. Adversarial Fault Evaluation Matrix

We evaluated Candidate A1 across 8 distinct failure modes (200 trials each):

| Failure Mode / Injection Scenario | Description | Outcome | Detection Rate | Cryptographic Consequence |
|:---|:---|:---|:---:|:---|
| **Mode 1: Single Transient in Pass 1** | SEU during 1st decapsulation (NTT / BaseMul) | `ss1` corrupted ($K_{\text{rand}}$), `ss2` clean ($K_{\text{true}}$) | **100.0% (200/200)** | Trapped safely; retry recovers session. |
| **Mode 2: Single Transient in Pass 2** | SEU during 2nd decapsulation | `ss1` clean, `ss2` corrupted | **100.0% (200/200)** | Trapped safely; retry recovers session. |
| **Mode 3: Persistent Stuck-at Fault** | Stuck-at bit in ALU or CPU register during both passes | Both passes execute identical corrupted math $\to$ `ss1 == ss2` | **0.0% (0/200 — SILENT FAIL)** | Silent divergence; both passes produce identical corrupted key. |
| **Mode 4: Shared Input Buffer Corruption** | Single bit flip in ciphertext $c$ before decapsulation | Both passes decode identical bad ciphertext $\to$ `ss1 == ss2` | **0.0% (0/200 — SILENT FAIL)** | Silent divergence; DMR cannot detect pre-existing buffer corruption. |
| **Mode 5: Shared Secret Key Buffer Corruption**| Bit flip in secret key $\mathbf{s}$ before decapsulation | Both passes execute with bad $sk$ $\to$ `ss1 == ss2` | **0.0% (0/200 — SILENT FAIL)** | Both passes trigger implicit rejection identically. |
| **Mode 6: Comparison Logic Corruption** | Bit flip in `diff` accumulator in `ct_memcmp` | Mismatch between `ss1` and `ss2` masked to 0 | **0.0% (Bypass)** | Corrupted key committed despite detected mismatch. |
| **Mode 7: Return Token Flip** | SEU in return register changing FAULT $\to$ OK | Return register forced to `RESILIENCE_OK_TOKEN` | Mitigated by Candidate D ($d_H = 32$) | Requires 32 coordinated bit flips. |
| **Mode 8: Correlated Clock/Voltage Glitch** | Glitch timed to fixed clock cycle in both loops | Deterministic glitch flips identical bit in both runs | **0.0% (0/200 — SILENT FAIL)** | SDC; identical garbled output accepted. |

---

## 3. Threat Model Applicability Boundary

DMR provides **meaningful protection strictly under the following bounded threat model:**
1. Faults are **statistically independent, transient Single Event Upsets** arriving with low Poisson probability ($\lambda \ll 1/\text{execution time}$).
2. Input buffers $c$ and $sk$ are protected by independent hardware mechanisms (e.g., SECDED ECC on RAM and ROM).
3. The CPU hardware core is free of permanent stuck-at defects.

**DMR Fails Completely Under:**
- Adversarial fault injection where an attacker triggers reproducible glitches at fixed cycle counts.
- Memory corruption in inputs prior to API invocation.
- Common-mode hardware faults.
