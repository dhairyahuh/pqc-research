# Phase 1 — Document 10: Multi-Criteria Candidate Ranking and Selection

**Document ID:** `ASTRA-SEC-PH1-DOC-10`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Evaluation Model:** Weighted Multi-Criteria Decision Matrix  

---

## 1. Weighted Ranking Methodology

To avoid subjective bias, each of the five candidate contributions is scored from $1.0$ (poor) to $10.0$ (outstanding) across six weighted academic evaluation criteria:

1. **Novelty Against Prior Art (30% Weight):** Differentiation from existing publications, IETF standards, and ESA/NASA prototypes.
2. **Technical Depth (20% Weight):** Mathematical rigor, algorithmic complexity, and formal modeling requirements.
3. **Experimental Testability (15% Weight):** Ability to test against clear controls with measurable independent/dependent variables.
4. **Feasibility (15% Weight):** Practical viability of implementing and verifying the protocol within the existing C/Python codebase.
5. **Research Significance (10% Weight):** Impact on space systems, post-quantum standardization, and dependable distributed systems.
6. **Reproducibility (10% Weight):** Ease with which external researchers can replicate the experimental results.

$$\text{Final Score} = 0.30 N + 0.20 D + 0.15 T + 0.15 F + 0.10 S + 0.10 R$$

---

## 2. Quantitative Scoring Matrix

| Evaluation Criterion | Weight | Candidate 1: Cross-Layer State Machine | Candidate 2: Crash-Consistent Acceptance | Candidate 3: Fault-Aware Lifecycle | Candidate 4: TFIB-Ref Fault Checker | Candidate 5: Key-Transition Safety |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Novelty Against Prior Art** | 30% | **9.0** | 7.5 | 6.5 | 8.5 | 7.0 |
| **Technical Depth** | 20% | **9.0** | 8.5 | 6.0 | 9.0 | 7.5 |
| **Experimental Testability** | 15% | **8.5** | 8.0 | 7.5 | 9.5 | 7.0 |
| **Feasibility** | 15% | **8.5** | 9.0 | 8.0 | 9.5 | 7.5 |
| **Research Significance** | 10% | **9.5** | 8.5 | 7.0 | 8.0 | 8.0 |
| **Reproducibility** | 10% | **9.0** | 9.0 | 8.5 | 9.5 | 8.0 |
| **Weighted Total Score** | **100%** | **8.85 / 10.0** | **8.30 / 10.0** | **7.05 / 10.0** | **8.85 / 10.0** | **7.40 / 10.0** |
| **Academic Ranking** | — | **RANK 1 (Tied)** | **RANK 3** | **RANK 5** | **RANK 1 (Tied)** | **RANK 4** |

---

## 3. Detailed Justification for Scores

### Candidate 1: Cross-Layer Fault-Aware Security State Machine (Score: 8.85)
- **Strengths:** Solves the core scientific disconnect between low-level cryptographic rollback ($K \le 2$) and high-level DTN custody. Bridges two major communities (PQC hardware fault injection and space DTN networking). Unprecedented in primary literature.
- **Vulnerability:** Cross-layer architectures often face pushback from networking purists who favor strict layer encapsulation.
- **Verdict:** Selected as the **PRIMARY RESEARCH CONTRIBUTION** for the end-to-end systems paper.

### Candidate 4: Independent Fault-Checker Resilience for ML-KEM (TFIB-Ref) (Score: 8.85)
- **Strengths:** The C99 implementation of sub-word butterfly checking with bounded snapshot rollback is already fully implemented, passes 3,000 fault injection trials, and achieves $+2.29\%$ overhead vs $+101.49\%$ for DMR. It represents extraordinary algorithmic depth for a cryptographic hardware/embedded software venue (e.g., CHES / IEEE TCAD).
- **Vulnerability:** Focusing purely on Candidate 4 discards the larger DTN multi-node space network architecture.
- **Verdict:** Selected as the **FOUNDATIONAL LOW-LEVEL SUPPORTING CONTRIBUTION**. It serves as the algorithmic engine powering Candidate 1.

### Candidate 2: Crash-Consistent Cryptographic Command Acceptance (Score: 8.30)
- **Strengths:** Directly solves the critical "restart-replay vulnerability" in satellite telecommands by enforcing atomic WAL write barriers before application dispatch. Highly testable via `SIGKILL` fault schedules.
- **Vulnerability:** Reviewers may argue that applying Write-Ahead Logging to command execution is an application of known database transaction techniques (Gray et al., 1981) rather than a fundamentally new cryptographic primitive.
- **Verdict:** Selected as the **SECONDARY SUPPORTING PROTOCOL CONTRIBUTION**.

### Candidate 5: Key-Transition Safety During DTN Disconnection (Score: 7.40)
- **Evaluation:** Important for long-delay interplanetary links, but overlaps significantly with ongoing IETF Messaging Layer Security (MLS) asynchronous extensions. Lower novelty confidence.
- **Verdict:** Discarded as a standalone primary claim; incorporated into future work.

### Candidate 3: Fault-Aware DTN Message Lifecycle (Score: 7.05)
- **Evaluation:** Primarily an engineering heuristic adjusting bundle TTL based on retry counters. Does not possess sufficient mathematical or theoretical novelty for a top-tier publication.
- **Verdict:** Rejected.

---

## 4. Final Research Selection

Rather than diluting the research by claiming all five candidates, the research direction is focused cleanly on:

```
+-----------------------------------------------------------------------------------------------+
| THE CHOSEN RESEARCH ARCHITECTURE                                                             |
|                                                                                               |
| PRIMARY CONTRIBUTION:                                                                         |
| Cross-Layer Fault-Aware Security State Machine (Candidate 1)                                  |
| "Coordinating Post-Quantum Arithmetic Fault States with Delay-Tolerant Space Networking"     |
|                                                                                               |
| SUPPORTING CONTRIBUTION 1 (Low-Level Algorithmic Core):                                      |
| Software-Level Sub-Word NTT Invariant Monitoring with Bounded Rollback (Candidate 4)          |
| "+2.29% Latency Overhead vs +101.49% for DMR, 99.4% SEU Coverage, 0.00% SDC"                  |
|                                                                                               |
| SUPPORTING CONTRIBUTION 2 (Protocol Persistence):                                             |
| Crash-Consistent Cryptographic Command Acceptance (Candidate 2)                              |
| "Atomic WAL-Backed Replay Protection Preventing Re-Execution Across Power-Cycles"             |
+-----------------------------------------------------------------------------------------------+
```
