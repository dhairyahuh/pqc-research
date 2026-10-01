# Implementation Audit: Phase 7C Native ML-KEM Resilience & Harness

## 1. Executive Audit Summary

This document presents an adversarial, code-level and assembly-level audit of the Phase 7C native ML-KEM decapsulation monitoring implementation (`algorithms/source_ref/mlkem/src/kem.c`), the resilience harness (`experiments/phase7c/phase7c_oracle_free_harness.c`), and raw trial data (`results/phase7c/raw/phase7c_raw_trials.json`).

While Phase 7C successfully eliminated the external `expected_ss` oracle from the decapsulation function, adversarial inspection reveals **critical implementation bugs, test harness artifacts, and architectural blind spots** that undermine the reported 100% detection and resilience claims.

---

## 2. Critical Defects and Harness Artifacts Identified

### Defect 1: Class 6 (Checker Perturbation) Was Hardcoded in Test Harness
- **Location:** `experiments/phase7c/phase7c_oracle_free_harness.c`, lines 496–501.
- **Audited Code:**
  ```c
  } else if (cls == 5) {
      /* Class 6: Checker Perturbation */
      d1 = false; d2 = false; d3 = false; d4 = false;
      d5 = true;
      tok6 = RESILIENCE_FAULT_TOKEN;
      d6 = true;
  }
  ```
- **Finding:** No fault was injected into the checker, no decapsulation function was executed, and no multi-rail verification logic was tested. The reported 100% detection rate for Class 6 (150/150 trials) in Phase 7C was an **untested harness artifact**.
- **Impact:** The claim that checker perturbation is 100% detected by native multi-rail barriers was unsupported by empirical evidence prior to Phase 7D.

### Defect 2: Array Size Mismatch in `g_inv_zetas_layer7` (117 vs 128 elements)
- **Location:** `experiments/phase7c/phase7c_oracle_free_harness.c` (lines 62–74) and `experiments/phase7b/independent_validation_harness.c` (lines 61–73).
- **Audited Code:**
  ```c
  static const int16_t g_inv_zetas_layer7[128] = {
      -1090, 1090, 1374, -1374, 927, -927, 442, -442, -748, 748, 1422,
      /* ... 10 lines of 11 elements + 1 line of 7 elements ... */
      -680, -583, 583, 568, -568, -17, 17
  };
  ```
- **Finding:** The initializer contains exactly **117 elements** for a 128-element array. Under ISO C standards, the remaining 11 array elements (`g_inv_zetas_layer7[117..127]`) default to zero (`0x0000`).
- **Mathematical Impact:** In `verify_complementary_ntt`, when `i` ranges from 117 to 127:
  $$w_i = 0 \implies (e_i \cdot w_i) \equiv 0 \pmod q$$
  The weighted invariant completely ignores polynomial coefficients at indices $2 \times 117$ through 255. Any fault injected in the highest 22 coefficients of the NTT output polynomial produces zero change in the weighted invariant sum $\psi_{\text{even}}$, creating a silent 8.6% blind spot in the transform domain.

### Defect 3: Invalid Ciphertext Triggers Redundant Retry (Timing Leak & DoS)
- **Location:** `experiments/phase7c/phase7c_oracle_free_harness.c`, lines 236–262.
- **Audited Code:**
  ```c
  bool dec_reject = (internal_status == MLK_STATUS_REJECT);
  uint32_t rail1 = (!dec_fault && !dec_reject && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
  uint32_t rail2 = (!dec_fault && !dec_reject && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
  uint32_t status = verify_multi_rail_barrier(rail1, rail2);

  if (status != RESILIENCE_OK_TOKEN && allow_retry) {
      mlkem_fault_reset();
      /* Unconditionally retries full decapsulation! */
      dec_res = mlkem768_dec_monitored(ss, ct, sk, &retry_status);
      ...
  }
  ```
- **Finding:** Legitimate invalid ciphertexts (a standard protocol operation under IND-CCA2) produce `internal_status = MLK_STATUS_REJECT`. The wrapper treats `dec_reject` as a failure token and executes a redundant second full decapsulation attempt before returning `RESILIENCE_REJECT_TOKEN`.
- **Impact:**
  1. *Timing Side-Channel:* Valid ciphertexts complete in $\sim 72\,\mu\text{s}$, while invalid ciphertexts take $\sim 148\,\mu\text{s}$ ($2\times$ latency), exposing a remote network oracle.
  2. *DoS Amplification:* An external attacker sending stream of random nonces forces $100\%$ CPU overhead doubling decapsulation latency.

### Defect 4: Benchmarking Methodology Distortion (Apple Silicon DVFS Artifact)
- **Location:** `experiments/phase7c/phase7c_oracle_free_harness.c`, lines 596–640.
- **Finding:** Config 1 (Baseline) was executed first without any CPU cache or clock frequency warm-up. On Apple Silicon (macOS), thread execution began on an efficiency core / idle clock state ($\approx 148.49\,\mu\text{s}$). By the time Config 5 and Config 6 executed (after 4,000 decapsulations), the CPU frequency boosted to peak Performance-core clocks ($\approx 82.74\,\mu\text{s}$).
- **Impact:** The reported "$-44.3\%$ overhead" (faster than baseline) was entirely a thermal/DVFS benchmarking artifact. Controlled warm-up testing in Phase 7D establishes true baseline decapsulation at $72.42\,\mu\text{s}$ and monitored decapsulation at $72.49\,\mu\text{s}$ (overhead $+0.10\%$).

---

## 3. Class-by-Class Injection and Detection Audit

| Fault Class | Injection Point | Timing | Real Detection Mechanism | Identified Blind Spot / Limitation |
| :--- | :--- | :--- | :--- | :--- |
| **Class 1: Intermediate T** | Butterfly $t$ reg | Mid-NTT | FO re-encryption / Weighted NTT | Unweighted parity has 0.0% coverage; Weighted NTT blind outside Layer 7. |
| **Class 2: Twiddle $\zeta$** | Twiddle memory load | Mid-NTT | FO re-encryption ($tmp \neq ct$) | DMR misses 14.7% due to identical branch execution. Layered catches via FO. |
| **Class 3: Output Add Reg** | Stage write-back | Stage 7 | Parity & Weighted NTT & FO | Symmetric additive faults ($\pm \delta$) cancel out in parity sum. |
| **Class 4: Correlated Mult** | Polymul vector inner prod | IND-CPA | FO re-encryption check | NTT invariants completely inactive; relies entirely on in-tree FO check. |
| **Class 5: Pre-Invoc Input** | Memory buffer `ct` | Pre-decaps | CRC32 input check | Pre-CRC tampering, simultaneous CT+CRC corruption, and TOCTOU completely bypass CRC. |
| **Class 6: Checker Perturb** | Rail variables, ALU flags | Post-FO | Multi-rail barrier complementarity | Hardcoded in Phase 7C. Stuck ALU comparator causes simultaneous symmetric rail corruption. |
| **Class 7: FO Control Gate** | Predicate flag `fail` | FO compare | Reverse XOR dual-rail check | Correlated glitches flipping both `fail` and `fail_chk` bypass discrepancy check. |
| **Class 8: Persistent Stuck** | ALU / bus bit-slice | Persistent | FO / NTT failure (Detected) | **Zero recovery possible.** Retrying persistent faults fails 100% of the time. |

---

## 4. Disassembly and Machine Code Verification

Disassembly of `algorithms/source_ref/mlkem/src/kem.c` compiled under Clang `-O3` (`_mlkem768_dec_monitored`):

```assembly
; Dual-rail forward comparison (ct_memcmp unrolled)
0x10c38: eor.16b   v23, v19, v7
0x10c48: orr.16b   v0, v23, v0
; Reverse comparison loop executed sequentially
0x10d14: eor.16b   v4, v16, v4
0x10d18: rev64.16b v4, v4
0x10d44: orr.16b   v0, v4, v0
; Status evaluation
0x10d94: mov       w10, #0x5a5a
0x10d98: movk      w10, #0x5a5a, lsl #16  ; 0x5A5A5A5A (SUCCESS)
0x10d9c: cinv      w10, w10, ne           ; 0xA5A5A5A5 (REJECT) if fail != 0
0x10da4: cmp       w8, w9                 ; compare fail_chk (w8) with fail (w9)
0x10da8: csel      w24, w24, w11, eq      ; if w8 != w9, force fail = 0xFF
0x10dac: csinv     w8, w10, wzr, eq       ; if w8 != w9, status = 0xFFFFFFFF
0x10db0: str       w8, [x22]              ; write to *internal_status
```

### Compiler Invariance Findings
1. **Branchless Execution:** The compiler generates branchless conditional selection (`csel`, `csinv`, `cinv`) without secret-dependent jumps.
2. **Distinct Register Usage:** `fail` (`w9`) and `fail_chk` (`w8`) are held in distinct registers prior to comparison at `0x10da4`.
3. **Common-Mode Vulnerability:** A single physical fault targeting the processor condition flag register (specifically the Zero flag $Z$ evaluated by `eq`) will cause both `csel` and `csinv` to misclassify a discrepancy as an equality, allowing a glitched FO flag to leak candidate shared secrets.
