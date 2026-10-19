# Phase 7 Claim Revision and Evidentiary Boundaries

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Critical Reassessment of Phase 7 Findings and Evidentiary Claims  

---

## 1. Executive Summary

Phase 7 conducted an audit of Phase 6, correcting an oracle reference collision bug and formalizing the arithmetic properties of the recovery verifier. However, Phase 7 did not explicitly distinguish between:
1. Logic executed by the **authentic production binary** (`bin/obj/mlkem_fault_hooks.o`).
2. Logic executed by a **harness-level reimplementation** of the monitor.
3. Constructed **software fault simulations** versus **physical hardware fault feasibility**.

This audit systematically reviews each Phase 7 claim, defining its exact defensible boundaries.

---

## 2. Claim-by-Claim Audit and Revision

### Claim 1: "Internal False Recovery (H1) is genuinely demonstrated using an independent oracle."
- **Phase 7 Finding:** H1 occurs in 98% of F1, 70% of F2, 100% of F3, 100% of F6, 93% of F9, and 100% of F10 trials.
- **Phase 8 Revision:** **CONFIRMED with Critical Implementation Qualification.**
  - The arithmetic proof that the recovery verifier accepts corrupted inputs ($u_{\text{saved}}'$) is mathematically sound.
  - However, the tests **did not execute `bin/obj/mlkem_fault_hooks.o`**. The harness reimplemented `native_ntt_monitor_butterfly` with local fault injection hooks because the in-tree production source provides no mechanism to corrupt stack-passed parameters (`u_saved`).
  - **Defensible Statement:** *"The internal recovery verifier algorithmically exhibits verifier blindness under snapshot corruption, as demonstrated in a software model matching the production arithmetic."*

### Claim 2: "F1's 98% pass rate is explained by signed 16-bit overflow."
- **Phase 7 Finding:** Bits 0–14 always pass ($94/94$), while Bit 15 overflows in 2 of 6 trials ($4/6$ pass), giving $98/100$ (98.0%).
- **Phase 8 Revision:** **FULLY CONFIRMED.**
  - Formally traced to C11 integer promotion and two's-complement narrowing conversions (§6.3.1.3).
  - Empirically verified across 5 compiler optimization levels (`-O0` to `-Os`).
  - **Defensible Statement:** *"The 98.0% pass rate in Target F1 is an exact mathematical consequence of two's-complement algebraic cancellation in the absence of 16-bit truncation, combined with the sign distribution of bit 15 in the test seed."*

### Claim 3: "F2's stage-dependent split (30% genuine / 70% FO rejection) is verified."
- **Phase 7 Finding:** In Stages 1 and 2, $+100$ bias diffuses below the 10-bit compression quantization threshold, yielding genuine recovery.
- **Phase 8 Revision:** **FULLY CONFIRMED.**
  - Direct empirical measurements of `trace_f2_stages` confirm that Stages 1 and 2 diffuse across 128 and 64 coefficients, producing `memcmp(ct, tmp) == 0` (`fail == 0x00`) and returning the true shared secret.
  - Stages 3–7 diffuse across $\le 32$ coefficients, exceeding the $\Delta_{\text{bin}} \approx 3.25$ threshold, setting `fail == 0xFF`, and triggering safe implicit rejection.
  - **Defensible Statement:** *"Empirical measurements verify that the 30%/70% outcome split in Target F2 is caused by NTT butterfly diffusion depth relative to the 10-bit ciphertext compression rounding margin."*

### Claim 4: "F4 false recovery in Phase 6 was an artifact of an oracle reference collision bug."
- **Phase 7 Finding:** Phase 6 used a 1D reference table that compared Polynomial 0 against Polynomial 5, falsely reporting 100% H1. In Phase 7, F4 is 100% genuine recovery.
- **Phase 8 Revision:** **FULLY CONFIRMED & REPRODUCED ON PRODUCTION OBJECTS.**
  - Linking directly against `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o` reproduces 100% genuine recovery for transient butterfly faults under `NTT_NATIVE_MONITOR_RECOMPUTED_T`.
  - **Defensible Statement:** *"Phase 6's claim that Target F4 exhibited false recovery was an artifact of an underspecified 1D reference table. When evaluated with correct polynomial indexing, Target F4 achieves 100% genuine recovery."*

### Claim 5: "Hypothesis H2 (Accepted Incorrect Shared Secret) is 0% due to outer FO re-encryption."
- **Phase 7 Finding:** 0/1,200 trials accepted an incorrect shared secret.
- **Phase 8 Revision:** **FULLY CONFIRMED.**
  - Traced directly to the compiled object `bin/obj/mlkem768_inst.o` (`kem.c:466-519`), where constant-time ciphertext comparison and reverse dual-rail verification unconditionally guard key derivation.
  - **Defensible Statement:** *"In ML-KEM-768 decapsulation, internal recovery-verifier blindness does not lead to end-to-end key corruption because the outer Fujisaki-Okamoto transform enforces implicit rejection on invalid ciphertexts."*

### Claim 6: "DSPC is vulnerable to correlated 2-bit linear collisions."
- **Phase 7 Finding:** DSPC achieves 93% bypass under correlated linear bitflips (F9) and 100% under branch skip (F10).
- **Phase 8 Revision:** **QUALIFIED AS A SOFTWARE MODEL.**
  - DSPC does not exist in `algorithms/source_ref/` or any compiled object. It was implemented exclusively as an experimental prototype inside test harnesses.
  - While mathematically sound, the fault models (simultaneous 2-bit correlated inversion and control-flow branch skipping) are constructed software simulations rather than experimentally measured physical attacks.
  - **Defensible Statement:** *"The Dual-Snapshot Parity Checksum (DSPC), as modeled in software, is theoretically vulnerable to linear parity collisions and control bypass, but has not been implemented or evaluated in production firmware."*
