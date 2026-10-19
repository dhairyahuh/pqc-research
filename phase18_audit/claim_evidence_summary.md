# Workstream 7 Summary: Claim-to-Evidence Audit Findings

**Auditor:** Independent Cryptographic Implementation & Empirical Verification Auditor  
**Date:** October 2026  
**Audited Artifact:** `phase17b_corrected/manuscript_draft.md` against reproduced source code and experimental data  
**Target Ledger:** [`phase18_audit/claim_evidence_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/claim_evidence_matrix.csv)

---

## 1. Executive Breakdown of Claim Statuses

A forensic audit of the 14 primary claims in the revised manuscript draft was conducted against actual source code, executable tests, fresh empirical reproductions, and mathematical derivations.

### Status Tally across 14 Core Claims:
- **Supported by Reproduced Evidence (Direct Strength):** 6 / 14 (42.9%)
- **Partially Supported (Requires Explicit Qualification / Range):** 5 / 14 (35.7%)
- **Contradicted or Materially Inaccurate (Requires Source Correction):** 3 / 14 (21.4%)

```
========================================================================
CLAIM AUDIT STATUS DISTRIBUTION (N = 14)
========================================================================
[  42.9%  ] Supported by Reproduced Evidence (Direct Evidence)
[  35.7%  ] Partially Supported (Requires Framing/Range Qualification)
[  21.4%  ] Contradicted / Inaccurate (Requires Direct Source Correction)
========================================================================
```

---

## 2. Analysis of Contradicted and Materially Inaccurate Claims

### 2.1. Claim CLM-12: The Decapsulation Transform Flow Narrative
- **Manuscript Statement (§3.1):**
  > *"Decapsulation involves: 1. Inverse NTT of the received ciphertext polynomials $\mathbf{u}$ ($k=3$); 2. Forward NTT on secret key vector $\mathbf{s}$ ($k=3$)..."*
- **Audit Reality (`indcpa.c:603-628`):**
  - **CONTRADICTED.** In NIST FIPS 203 and the `mlkem-native` codebase, the secret key $\hat{\mathbf{s}}$ is unpacked directly into the NTT domain; it **never undergoes forward or inverse NTT** during decapsulation.
  - The received ciphertext vector $\mathbf{u}$ is unpacked in the standard polynomial domain and undergoes a **Forward NTT** (`mlk_polyvec_ntt(b)`), not an inverse transform.
- **Impact:** While the total butterfly count ($9{,}856$) is mathematically exact, the narrative explanation of *which* vector undergoes *which* transform is factually inverted.
- **Action:** Rewrite §3.1 of the manuscript to accurately describe the FIPS 203 transform flow.

### 2.2. Claim CLM-13: Certified Constant-Time Security
- **Manuscript Statement (§4.3):**
  > *"The empirical timing ratio between fault-triggered and clean execution paths is $1.0005\times$, consistent with constant-time behavior."*
- **Audit Reality (`poly.c:408` & `mlkem_fault_hooks.c:631`):**
  - **UNSUPPORTED FOR RECOVERY PATH.** While nominal arithmetic uses branch-free masking, error detection triggers a conditional branch into the rollback and retry block (`if (diff_c != 0 || sum_c != 0)`).
  - No formal microarchitectural timing leakage analysis (TVLA or dudect Welch's t-test) has been performed on the compiled machine binary.
- **Action:** Excise all suggestions of certified constant-time security under fault conditions; explicitly state that the recovery path introduces conditional control flow.

### 2.3. Claim CLM-14: Hardware Stuck-At Fault Modeling
- **Manuscript Statement (§2.3 Table 1):**
  > *"F5B: True Hardware Stuck-At-0 Fault... Model Semantics: Abstract software debug model"*
- **Audit Reality (`mlkem_fault_hooks.c:265`):**
  - **CONTRADICTED.** Target $F5B$ is implemented as `*t = 0`, forcing an intermediate C scalar variable to zero in software.
  - It does not model physical hardware gate-oxide breakdown, power-rail droop, or silicon latch-up.
- **Action:** Consistently label Target $F5B$ as a *"software force-value variable-zeroing debug model"*.

---

## 3. Analysis of Supported Core Claims

The following core technical claims were **100% verified through fresh execution**:

1. **Transient Fault Recovery ($F4$):** 100/100 genuine recoveries reproduced on production objects (`mlkem768_inst.o`, `mlkem_fault_hooks.o`). Every trial demonstrated that the single-butterfly retry executed, restored authentic outputs, and emitted $K_{\text{valid}}$ matching the clean-room reference oracle ($95\%$ Wilson score CI: $[96.3\%, 100.0\%]$).
2. **Safe Fail-Stop Escalation ($F5A, F5B$):** 200/200 safe aborts reproduced. Under recurring bit-inversion and software force-value zeroing, the monitor recorded persistent failure and emitted $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ identically ($95\%$ Wilson score CI: $[98.1\%, 100.0\%]$).
3. **Absence of SDC ($H_2$):** Across 300 active software fault trials, zero SDC instances were observed (0/300, 95% Wilson score CI: $[0.00\%, 1.26\%]$).
4. **FIPS 203 Implicit Rejection Conformance:** 100/100 invalid ciphertext mutations emitted keys matching the clean-room Keccak-f[1600] reference oracle identically.
5. **Outer FO Containment:** Confirmed by source inspection and trial execution. When local monitors are blind (e.g., twiddle factor faults $C02/C05$), the outer FO re-encryption check detects the ciphertext discrepancy and forces implicit rejection.
