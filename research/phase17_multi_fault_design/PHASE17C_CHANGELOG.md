# Phase 17C Changelog: Residual Statistical & Implementation-Semantics Audit

**Document:** `research/phase17_multi_fault_design/PHASE17C_CHANGELOG.md`  
**Date:** 2026-10-11  
**Target Specification:** `PHASE17_EXPERIMENT_DESIGN.md` & `PHASE17B_METHODS_CORRECTION.md` $\rightarrow$ Audited by `PHASE17C_RESIDUAL_AUDIT.md`  

---

## 1. Summary of Changes and Formal Specifications

1. **Fixed-Quota Block Sampling Enforced (Section A):**
   - Replaced probabilistic stratum assignment with fixed-quota block sampling to eliminate sample size shortfall risks ($N_{\text{admitted}} = 300$, $N_{\text{blocking}} = 100$, $N_{\text{control}} = 20$).
   - Established complete-case reporting rules for ineligible seeds without outcome-dependent replacement.
   - Formally defined the primary SDC denominator $\mathcal{D}_{\text{SDC}}$ as Attempt 1 active fault decapsulations on delivered ciphertexts.
   - Recalculated exact one-sided Wilson ($0.8938\%$), two-sided Wilson ($1.2643\%$), and Clopper-Pearson ($0.9934\%$) bounds for $n=300$.
   - Established a mandatory shortfall rule prohibiting below-1% claims if realized $n < 300$.
2. **Protocol Contrast Population Partitioning (Section B):**
   - Disproved universal validity of $p_{10} = p_{11} = 0$, noting dormant Index 0 and sham masks yield $p_{10} = 1.0$.
   - Partitioned evaluation into Population 1 (active mutations) and Population 2 (controls), preserving the unconstrained general contrast $\hat{\Delta}_{\text{proto}} = \hat{p}_{11} - \hat{p}_{10} - \hat{p}_{01} + \hat{p}_{00}$.
   - Disentangled protocol failure due to cryptographic rejection from link-layer drops.
3. **Control-Flow Code Tracing of 7 Channel Classes (Section C):**
   - Traced `combined_campaign.c` lines 70–130.
   - Identified that `CH_BIT` is the **only** class passing corrupted ciphertext to decapsulation.
   - Documented that `CH_DUP` and `CH_REORDER` pass clean ciphertexts, while `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_INTERRUPT` never invoke decapsulation.
   - Restricted the guaranteed SDC decapsulation stratum strictly to `CH_BIT`.
4. **Independent Vector Validation Protocol (Section D):**
   - Disclosed exact vector inventory: 1 official static NIST KAT vector + 399 locally derived deterministic test cases.
   - Specified a 4-step cross-implementation preflight verification pipeline (`mlkem-native` vs `liboqs` keygen/encaps/decaps cross-checks + standalone rejection derivation).
5. **Execution Guard Reaffirmed (Section E):**
   - Maintained strictly read-only audit status; no implementation code, compilation, or execution performed.
