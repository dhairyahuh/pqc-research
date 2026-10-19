# Phase 18B Changelog: Formal Implementation Proposal and Architecture Specification

**Document:** `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md`  
**Date:** 2026-10-12  
**Target Specification:** `PHASE18B_IMPLEMENTATION_PROPOSAL.md`  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** PROPOSAL COMPLETED — Strictly Read-Only  

---

## 1. Summary of Actions and Deliverables

Phase 18B formulated a comprehensive, reviewable implementation proposal and architecture specification for the ratified Phase 17 multi-fault experiment (*Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software Study*), following the readiness findings established in Phase 18A.

In strict adherence to the **Mandatory Research Integrity and Anti-Hallucination Protocol**:
- No implementation source code or build files were modified or created.
- No binaries were compiled or linked.
- No virtual memory protections were altered or mutated.
- No test vectors were generated or validated.
- No experimental trials or runner scripts were executed.
- No Git commits, pushes, resets, cleans, or discards were performed.
- All 10 pre-existing working-tree modifications were preserved untouched.
- All historical artifacts across Phases 17 through 18A were preserved byte-for-byte.

**Created Deliverables:**
1. `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md`
2. `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md`

---

## 2. Key Specifications Formulated in Phase 18B

1. **Unified Runner Architecture (`multi_fault_runner.c`):**
   - Coordinated six subsystems: scenario manifest reader, preflight vector suite, Darwin ARM64 persistent memory mutation harness (`pilot_runner.c`), 7-class channel fault injection and retry engine (`combined_campaign.c`), SUT ML-KEM-768, and independent TweetFIPS-202 rejection oracle.
   - Formalized a 10-step session lifecycle covering manifest verification, preflight checks, baseline memory validation, matched condition execution, retry loop with continuous memory fault persistence, terminal in-process restoration, canary validation, and clean baseline KAT rechecks.
   - Defined fail-closed error handling and signal containment: explicit distinction between operating-system process cleanup upon hardware trap signals (`SIGBUS`, `SIGSEGV`) and verified in-process memory restoration. Signal aborts log `UNVERIFIED_PROCESS_ABORTED`.

2. **Deterministic Scenario Manifest (`manifest.json`):**
   - Specified a canonical JSON / JSONL schema embedding master seed IDs, vector derivation seeds, memory fault targets ($k \in [1, 127]$, mask $\neq 0$ or explicit dormant/sham control), channel class parameters, retry budgets, and matched condition links.
   - Defined strict canonical serialization rules (sorted keys, compact delimiters, lowercase hex) and SHA-256 manifest integrity hashing.
   - Formulated strict validation rules enforcing ratified quotas (Q1: 300, Q2: 40, Q3: 60, Q4: 20; total $N=420$ seeds, $1,680$ trials) and rejecting duplicate seeds or invalid parameters before any memory mutation.

3. **Vector Corpus and Independent Oracle Contract:**
   - Distinguished the single existing official NIST KAT vector on disk (`mlkem_expected_kat.h`) from 419 local vectors to be generated deterministically at preflight runtime.
   - Specified a 6-point preflight validation contract against `liboqs v0.16.0` covering keypair derivation, encapsulation, clean decapsulation, independent rejection derivation, tamper response, and size invariants.
   - Defined golden secret and rejection semantics under channel corruption: rejection secret $J(z_i \parallel \tilde{c}, 32) = \text{SHAKE256}(z_i \parallel \tilde{c}, 32)$ derived using exact received wire bytes $\tilde{c}$. Canonical rejection is never classified as cryptographic SDC.
   - Formally designated the TweetFIPS-202 oracle as an **architecturally independent reference implementation**, documenting that lack of institutional firewall documentation precludes calling it a legal "clean-room" implementation.

4. **Statistical Contract and Estimand Specifications:**
   - Defined the primary interaction contrast per channel class: $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$.
   - Defined the exploratory aggregate contrast as an equal $1/7$ weighting across active classes ($\hat{\Delta}_{\text{std}} = \frac{1}{7} \sum \hat{\Delta}_c$).
   - Established strict, separate tracking across six denominator tiers ($N_{\text{assigned}} \to N_{\text{eligible}} \to N_{\text{attempted}} \to N_{\text{completed\_sessions}} \to n_{\text{completed\_decaps}} \to N_{\text{analysable\_quads}}$).
   - Confirmed exact Clopper–Pearson upper bounds for $k=0$ SDCs: $n=300 \implies 0.9936\%$, $n=299 \implies 0.9969\%$, $n=298 \implies 1.0002\%$, $n=0 \implies \text{UNDEFINED}$ (inconclusive).
   - Strictly decoupled Protocol ($Y_{\text{proto}}$), Cryptographic Integrity ($Y_{\text{crypto}}$), and Execution Reliability ($Y_{\text{exec}}$) outcomes.

5. **Fault Isolation and Research Build Boundaries:**
   - Isolated research accessors behind `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)` in `zetas.inc` and `poly.c`.
   - Specified an authoritative trial ledger schema with discrete, non-overlapping status values.
   - Established fail-closed partial campaign handling (no final summary markers on premature exit).

6. **Phased Review Roadmap:**
   - Structured implementation into six sequential gates: Gate 1 (Architecture Approval), Gate 2 (Manifest Schema Review), Gate 3 (Vector Preflight Review), Gate 4 (Runner C Source Review), Gate 5 (Statistical Pipeline Review), and Gate 6 (Operator Execution Authorization).

---

## 3. Resolution of Phase 18A Blockers

| Blocker ID | Description | Phase 18B Specification Resolution | Status |
| :---: | :--- | :--- | :---: |
| **B-01** | Lack of Unified Multi-Fault Runner | Formulated `multi_fault_runner.c` coordinating persistent memory mutations, channel impairments, retry loops, independent oracle, and structured ledgers. | **SPECIFIED** |
| **B-02** | Unstratified Quota Sampling in Code | Specified canonical deterministic `manifest.json` schema enforcing exact quotas (Q1: 300, Q2: 40, Q3: 60, Q4: 20) with SHA-256 pre-hashing. | **SPECIFIED** |
| **B-03** | Unexecuted Vector Corpus (Vectors 1–419) | Specified 6-point preflight validation protocol against `liboqs v0.16.0` with fail-closed abort prior to memory mutation. | **SPECIFIED** |
| **B-04** | Retry Memory Persistence Gap | Formalized session lifecycle holding table mutation across attempt loop ($a \in [0, 2]$) and restoring strictly at terminal session exit. | **SPECIFIED** |

---

## 4. Evidence Standards and Hash Verifications

### 4.1 SHA-256 File Hashes `[DIRECTLY OBSERVED]`
Computed via `shasum -a 256` on actual on-disk bytes:

| File Path | SHA-256 Digest | Role / Status |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Artifact Preserved `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_CHANGELOG.md` | `6c3a4ce7e3d4a69c83fd8606c79aaf1ba549f5a61bc871148bea4dba6b42e673` | Historical Artifact Preserved `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md` | `faf155420c3dad1fe0085729943e2b899289165f8f38f3becb9b244a03b92340` | Historical Artifact Preserved `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_CHANGELOG.md` | `b0fed1b4e5fdfa9821baf35300dbc97e140e929c19b38063cdc09bd1b23f768b` | Historical Artifact Preserved `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Architecture Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Phase 18B Deliverable `[DIRECTLY OBSERVED]` |

### 4.2 Git Repository State `[DIRECTLY OBSERVED]`
- Active Branch: `space-resilience-framework`.
- Preserved 10 uncommitted tracked files in the working tree.
- Zero files staged, committed, pushed, or reverted.

---

## 5. Final Status and Authorization Statement

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Formal Boundary:
Phase 18B delivers a complete, reviewable architecture specification and implementation proposal. **It does not authorize compiling binaries, linking test harnesses, mutating memory, generating test vectors, or executing experiments.** Proceeding to implementation review requires human operator authorization.
