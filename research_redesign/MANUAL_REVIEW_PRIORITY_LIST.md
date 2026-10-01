# High-Priority Papers for Manual Human Review
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Protocol Phase:** Mandatory Literature Access, Verification, and Evidence Protocol  
**Date:** October 2026  
**Auditor Action:** Prioritized Action Items for Student & Faculty Supervisor  

---

## 1. Rationale for Manual Human Verification

While the automated review examined 20 primary sources and verified 16 full-text articles directly, several critical works are subject to publisher paywalls, closed database access, or recent 2026 conference publication cycles that restrict full-text web access without university proxy credentials.

To ensure absolute academic rigor before final manuscript submission, the student and supervisor must manually retrieve and review the following prioritized candidate papers through university library subscriptions (e.g., IEEE Xplore, ScienceDirect, ACM DL).

---

## 2. Prioritized Manual Review Register

### Priority 1: Critical — Mandatory Before System Implementation
* **Paper Identifier:** **P01 — El Bizri et al. (IEEE ICC 2026)**
* **Full Title:** *Channel-Adaptive Post-Quantum Cryptography for Secure and Efficient Non-Terrestrial Networks*
* **Authors:** Mustafa El Bizri, Ahmad M. El-Hajj, Layth Sliman, Ali Massoud Haidar
* **Venue:** IEEE International Conference on Communications (ICC 2026), Glasgow, Scotland, May 2026.
* **DOI:** [10.1109/ICC59461.2026.11587307](https://doi.org/10.1109/ICC59461.2026.11587307)
* **Access Limitation:** Full-text PDF is behind the IEEE Xplore conference paywall. Our review examined the published abstract, conference technical program, and author profiles.
* **Manual Verification Checklist for Student/Supervisor:**
  1. Inspect Section III (System Model): Verify the exact mathematical channel model used (Rayleigh, Rician, or Markov loss).
  2. Inspect Section IV (Adaptation Algorithm): Confirm whether their adaptation switches algorithm parameter sets (e.g., Kyber-512 vs Kyber-1024) or adjusts packet fragmentation.
  3. Verify whether the authors mention *any* onboard hardware fault assumptions, soft errors, or Single-Event Upsets (SEUs).
* **Retrieval Route:** University IEEE Xplore institutional login or direct author email request (`layth.sliman@efrei.fr`).

---

### Priority 2: High — Relevant Space Constraint Survey
* **Paper Identifier:** **P02 — Kim (Acta Astronautica 2026)**
* **Full Title:** *Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey*
* **Author:** Hyunmin Kim
* **Venue:** *Acta Astronautica*, Vol. 241, April 2026, pp. 278–294.
* **DOI:** [10.1016/j.actaastro.2026.04.041](https://doi.org/10.1016/j.actaastro.2026.04.041)
* **Access Limitation:** Partial full-text access via ScienceDirect snippet and abstract indexing.
* **Manual Verification Checklist for Student/Supervisor:**
  1. Inspect Section 4.2 (Lattice-Based Implementations in Space): Cross-check whether any published flight experiments or cyclotron beam tests on ML-KEM/Kyber are cited that were omitted from our review.
  2. Review Table 3 (Memory and Energy Constraints for SmallSats): Ensure our simulator's memory budget (< 512 KB) matches the latest aerospace consensus.
* **Retrieval Route:** ScienceDirect institutional portal or Elsevier inter-library loan.

---

### Priority 3: Medium — FPGA Invariant Counterpart Confirmation
* **Paper Identifier:** **P10 — Paul et al. (ACM TECS 2024/2026)**
* **Full Title:** *Efficient Error Detection for NTT Using Algebraic Invariants (AIC) Checking for PQC and FHE on FPGA*
* **Authors:** Rourab Paul, Paresh Baidya, Swagata Mandal, Krishnendu Guha
* **Venue:** *ACM Transactions on Embedded Computing Systems (TECS)*, DOI: [10.1145/3674838](https://doi.org/10.1145/3674838).
* **Access Limitation:** Journal version published online; technical content confirmed via author preprints (arXiv:2508.03062) and technical reports.
* **Manual Verification Checklist for Student/Supervisor:**
  1. Inspect Section 4 (PR-AIC Formulation): Confirm whether their checking equations extend beyond Cooley-Tukey forward butterflies.
  2. Confirm that their reported LUT overhead (+14% to +38%) is strictly hardware-based and provides zero in-place software rollback.
* **Retrieval Route:** ACM Digital Library institutional subscription.

---

## 3. Human-Assisted Review Protocol & Sign-Off Procedure

1. **Step 1:** The student retrieves the PDF copies of P01 and P02 using university library credentials.
2. **Step 2:** The student completes the three verification questions for P01 to confirm that El Bizri et al. do not incorporate endpoint computational fault tolerance.
3. **Step 3:** The supervisor signs off on the verification log in `research_redesign/LITERATURE_ACCESS_REGISTER.md`.
4. **Step 4:** Once P01 is verified, the transition from Level 3 (Unresolved) to Level 1 (Full-Text Reviewed) will be formally committed to Git.
