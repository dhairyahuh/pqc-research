# Phase 18A Changelog: Independent Implementation-Readiness Audit

**Document:** `research/phase17_multi_fault_design/PHASE18A_CHANGELOG.md`  
**Date:** 2026-10-12  
**Target Specification:** `PHASE18A_READINESS_AUDIT.md`  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** AUDIT COMPLETED — Strictly Read-Only  

---

## 1. Summary of Actions and Deliverables

Phase 18A performed an independent, strictly read-only implementation-readiness audit to evaluate whether the ratified Phase 17 multi-fault ML-KEM-768 campaign can be implemented faithfully and reproducibly using the actual repository source code and state.

In accordance with strict audit guardrails:
- No existing source code, test scripts, or build configurations were modified.
- No binaries were compiled or linked.
- No virtual memory was mutated.
- No test vectors were generated or validated.
- No experimental trials were run.
- No Git commits, pushes, cleans, or discards were performed.

Created files:
1. `research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md`
2. `research/phase17_multi_fault_design/PHASE18A_CHANGELOG.md`

All prior artifacts across Phases 17, 17B, 17C, 17D, 17E, 17F, 17G, and 17H were preserved byte-for-byte.

---

## 2. Key Audit Findings by Section

1. **Audit 1: Ratification and Protocol Consistency (Section 1):**
   - Constructed a requirement-to-evidence matrix evaluating all 11 ratified design choices against actual C source files (`combined_campaign.c`, `pilot_runner.c`, `poly.c`, `zetas.inc`).
   - Identified that while low-level primitives exist, no single existing C runner implements the unified multi-fault flow combining persistent Darwin ARM64 page mutation with external channel impairments under the ratified 420-seed stratified quota schedule.
   - Recommended specifying a clean, dedicated runner (`multi_fault_runner.c`) in the implementation proposal.

2. **Audit 2: Trial Accounting and Statistical Estimands (Section 2):**
   - Traced the 5-tier funnel ($N_{\text{assigned}} \to N_{\text{eligible}} \to N_{\text{attempted}} \to N_{\text{completed}} \to N_{\text{analysable}}$).
   - Confirmed that process crashes and OS trap signals are availability failures recorded in the Execution/Reliability ledger, coded as protocol failure ($Y=0$) in ITT analysis, and strictly excluded from completed SDC decapsulations ($n_{\text{completed}}$).
   - Independently recomputed the exact one-sided 95% Clopper–Pearson upper bound for $k = 0$: $n=300 \implies 0.993608\% < 1\%$; $n=299 \implies 0.996915\% < 1\%$; $n=298 \implies 1.000243\% \ge 1\%$; $n=0 \implies \text{UNDEFINED}$ (inconclusive).

3. **Audit 3: Vector Corpus and Independent Oracle (Section 3):**
   - Audited on-disk inventory: exactly 1 static NIST KAT vector exists in `references/test_vectors/mlkem_expected_kat.h`; zero locally generated vectors exist on disk (Vectors 1–419 are specifications for runtime preflight generation).
   - Documented a 6-point preflight contract enforcing deterministic PRF generation, `liboqs v0.16.0` cross-checks, baseline decapsulation, independent TweetFIPS-202 rejection derivation, secret key layout compliance ($z = sk + 2368$), and fail-closed manifest hashing.
   - Audited oracle provenance: verified source-code independence in `fips202_ref.c` and `independent_oracle.c`, while noting that source separation alone does not constitute formal institutional clean-room provenance.
   - Disentangled golden secret semantics under channel faults: sender expected output vs. receiver decapsulation output vs. rejection output vs. protocol key agreement.

4. **Audit 4: Fault Injection and Recovery Safety (Section 4):**
   - Directly inspected `pilot_runner.c`, `poly.c`, and `zetas.inc`.
   - Verified bounds checks ($k \in [0, 127]$), dormant index 0, sham mask `0x0000`, 16,128-byte padding canaries, and `vm_protect` RW/RO transitions.
   - Evaluated early exit paths, signal handlers (`SIGBUS`, `SIGSEGV`), and partial ledger flagging (`trials_recorded < 16`).
   - Verified that research-only mutation hooks are strictly isolated behind `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)`, preventing accidental execution in production builds via link-time failure.

5. **Audit 5: Prioritized Blockers and Final Verdict (Sections 6, 8):**
   - Prioritized four technical blockers: B-01 (runner unification), B-02 (stratified manifest generator), B-03 (preflight vector validation harness), B-04 (retry memory persistence across attempts).
   - Delivered formal verdict: **`READY FOR SEPARATE IMPLEMENTATION PROPOSAL`**.
   - Re-affirmed that campaign execution remains strictly UNAUTHORIZED.
