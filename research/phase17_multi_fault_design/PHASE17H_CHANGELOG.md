# Phase 17H Changelog: Operator Ratification, Integrity Audit, and Next-Phase Decision

**Document:** `research/phase17_multi_fault_design/PHASE17H_CHANGELOG.md`  
**Date:** 2026-10-12  
**Target Specification:** `PHASE17H_OPERATOR_RATIFICATION.md`  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** COMPLETE — Strictly Read-Only  

---

## 1. Summary of Actions and Deliverables

Phase 17H formally recorded the explicit operator approval of all Phase 17 multi-fault experimental design choices, performed an independent repository and statistical audit, and determined the next authorized phase under the **Mandatory Research Integrity and Anti-Hallucination Protocol**.

The phase operated under strict read-only constraints:
- No existing source code, test scripts, or prior phase artifacts were modified.
- No binaries were compiled or linked.
- No virtual memory was mutated.
- No test vectors were generated or validated.
- No experiments or trials were executed.
- No Git commits, pushes, cleans, or discards were performed.

Created files:
1. `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md`
2. `research/phase17_multi_fault_design/PHASE17H_CHANGELOG.md`

All prior artifacts across Phases 17, 17B, 17C, 17D, 17E, 17F, and 17G were preserved byte-for-byte.

---

## 2. Key Actions Recorded

1. **Formal Operator Approval (Section 1):**
   - Recorded approval received on **2026-10-11 at 18:46:06 UTC** (supplied conversation timestamp).
   - Formally adopted locked quotas: Q1 ($N_1 = 300$, primary active `CH_BIT`), Q2 ($N_2 = 40$, admitted-clean), Q3 ($N_3 = 60$, 15 each across 4 blocking classes), Q4 ($N_4 = 20$, 5 each across $2 \times 2$ control grid). Total: $420$ master seeds ($1,680$ planned trial records).
   - Formally adopted matched 4-condition protocol ($C_{00}, C_{10}, C_{01}, C_{11}$) with persistent twiddle mutation held across retries.
   - Formally adopted analysis plan: channel-stratified contrasts as primary; equal weighting of $1/7$ as strictly exploratory; three distinct outcome families (Protocol, Crypto-Integrity, Execution-Reliability).

2. **Statistical Corrections and Recomputations (Section 2):**
   - Derived exact one-sided 95% Clopper–Pearson upper bound for $k = 0$: $p_U = 1 - 0.05^{1/n}$.
   - Verified that $n \ge 299$ completed trials are required to obtain $p_U < 1.0\%$ ($p_U(298) = 1.000243\% \ge 1.0\%$; $p_U(299) = 0.996915\% < 1.0\%$; $p_U(300) = 0.993608\% < 1.0\%$).
   - Defined $n = 0$ as `INCONCLUSIVE_NO_COMPLETED_TRIALS` without a numerical bound.
   - Corrected historical pilot wording: for 0 failures in 16 trials, the exact binomial bound is $17.07\%$, while $18.75\%$ ($3/16$) is the rule-of-three approximation.

3. **Repository and Design Audit (Section 3):**
   - Inspected `combined_campaign.c`: confirmed only `CH_BIT` inverts ciphertext; `CH_TRUNC`, `LOSS`, `DELAY`, `INTERRUPT` block delivery before decapsulation; `CH_DUP`, `REORDER` alter metadata only.
   - Inspected `independent_oracle.c` and `fips202_ref.c`: confirmed secret seed $z$ extracted at $sk + 2368$ and hashed with wire ciphertext via standalone TweetFIPS-202 Keccak-f[1600].
   - Audited vector inventory: exactly 1 static NIST KAT vector on disk (`mlkem_expected_kat.h`); zero locally generated vectors exist on disk (Vectors 1–419 are preflight generation specifications).

4. **Next-Phase Decision (Section 5):**
   - Confirmed design closure on paper.
   - Recommended next authorized step: **Phase 18: Implementation Review and Isolated Harness Verification** (drafting and auditing runner code, preflight vector generator, and memory safety checks in isolation).
   - Delivered final status verdict: **`DESIGN CLOSED — READY FOR SEPARATE IMPLEMENTATION REVIEW`**.
   - Explicitly affirmed that campaign execution remains UNAUTHORIZED.
