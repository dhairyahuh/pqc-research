# Phase 15E — Findings Matrix & Verification Ledger

**Auditor:** Independent Skeptical Cryptographic Implementation Auditor  
**Audit Target:** Phase 15D Code, Artifacts, and Technical Claims  
**Date:** 2026-10-11  
**Target Directory:** `research/phase14_persistent_arm_design/`

---

## Findings Matrix

| Finding ID | Area | Dimension | Status | Severity | Exact File / Function / Line | Evidence | Impact | Concrete Remediation |
|:---:|:---|:---|:---:|:---:|:---|:---|:---|:---|
| **F-15E-01** | Audit A | FIPS 202 SHAKE256 Implementation | **PASS** | INFORMATIONAL | `pilot_runner.c` / `independent_shake256()` (lines 110–182) | Clean-room Keccak-f[1600] / SHAKE256 implementation with rate 136, standard little-endian indexing, and `pad10*1` padding with `0x1F` suffix. Zero shared code with SUT. | Guarantees genuine cryptographic oracle independence from the SUT. | None required. |
| **F-15E-02** | Audit A | Rejection Key Inputs & Concatenation | **PASS** | INFORMATIONAL | `pilot_runner.c` / `main()` (lines 304–323) | Secret $z$ extracted from terminal 32 bytes of `sk`; concatenated with complete 1088-byte ciphertext $c$ (total: 1120 bytes) to compute $J(z \parallel c, 32)$. | Conforms bit-for-bit to NIST FIPS 203 Section 6.3 Algorithm 17, Step 5. | None required. |
| **F-15E-03** | Audit A | Four-Way Endpoint Classification | **PASS** | INFORMATIONAL | `pilot_runner.c` / `oracle_classify_endpoint()` (lines 250–271) | Compares `ss_out` against `golden_ss` and independently derived `krej`. Distinguishes `EXPECTED_OUTPUT`, `REJECTION`, `DIFFERENT_OUTPUT`, and `NO_OUTPUT`. | Eliminates false rejection labelling; prevents silent data corruption (SDC) from being misclassified as rejection. | None required. |
| **F-15E-04** | Audit A | Oracle Preflight Self-Test & Derivation | **PASS** | INFORMATIONAL | `pilot_runner.c` / `main()` (lines 293–340) | Verifies $\text{SHAKE256}(\text{""}, 32)$ against NIST CAVP KAT; derives $J(z \parallel c, 32)$ and verifies against `expected_krej_kat`. Supports `--check-oracle` read-only test mode. | Guarantees oracle correctness before any memory protection transition is attempted. | None required. |
| **F-15E-05** | Audit B | Structured Single-Path Memory Cleanup | **PASS** | INFORMATIONAL | `pilot_runner.c` / `main()` (lines 562–645) | Every mutation trial passes through a mandatory 6-step transactional cleanup sequence (restore $\rightarrow$ readback $\rightarrow$ reprotect $\rightarrow$ live VM check $\rightarrow$ canary check $\rightarrow$ baseline KAT). | Precludes cross-trial contamination; guarantees read-only restoration on both normal and error paths. | None required. |
| **F-15E-06** | Audit B | Signal Trap Handling & Process Exit | **PASS** | LOW | `pilot_runner.c` / `handle_trap_signal()` (lines 198–203) | Intercepts `SIGBUS` and `SIGSEGV` using async-signal-safe `write()` and `_exit(128 + sig)`. Tears down process virtual address space. | Safely destroys mapping on fatal trap, but prevents in-process post-mortem CSV emission. | Downstream test harnesses must capture and handle non-zero exit status codes (138/139). |
| **F-15E-07** | Audit C | Target Index Upper Bounds Check | **PASS** | INFORMATIONAL | `pilot_runner.c` / `main()` (lines 468–477) | Asserts `target_idx < 128` before calculating addresses or unprotecting page; fails closed if out-of-bounds. | Prevents out-of-bounds pointer arithmetic or heap corruption. | None required. |
| **F-15E-08** | Audit C | Negative Sentinel Validation | **PASS** | LOW | `pilot_runner.c` / `main()` (line 480 & line 647) | Any negative index (`target_idx < 0`) is routed to unmutated baseline check. Does not strictly assert `target_idx == -1`. | An invalid negative sentinel (e.g. -2) would be executed as an unmutated baseline trial rather than rejected. | Refactor guard to explicitly require `target_idx == -1` for baseline, rejecting any other negative index. |
| **F-15E-09** | Audit C | Runner Stdout CSV Schema Column Count | **PASS** | LOW | `pilot_runner.c` / `main()` (lines 678–695) | Stdout CSV emits 8 columns (`output_ss` added), omitting the 9th column (`expected_behavior`) present in historical `PHASE15B_TRIAL_LEDGER.csv`. | Minor schema mismatch between raw runner output and historical 9-column ledger file. | Update downstream parsers or add `expected_behavior` to runner summary loop. |
| **F-15E-10** | Audit D | Historical Hash Ledger Inaccuracy | **FAIL** | MEDIUM | `PHASE15D_REPORT.md` / Section 5 (lines 181–182) | `PHASE15D_REPORT.md` recorded incorrect SHA-256 digests for `PHASE15B_REPORT.md` (reported `c6bba92f...`, actual `0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (reported `7973715d...`, actual `5cf48fb9...`). | Documentation integrity error in Phase 15D provenance record. | Correct the two erroneous hashes in project records with verified values. |
| **F-15E-11** | Audit D | Claim Boundaries & Untested Behaviors | **PASS** | INFORMATIONAL | `PHASE15D_REPORT.md` / Section 2 & Section 6 | Formally retracted FO key leakage prevention claim; documented 5 explicit untested behaviors (no live trials, no live mutation, no injected traps). | Preserves rigorous scientific boundaries; prevents overstating static code verification as empirical proof. | None required. |

---

## Summary of Findings by Severity

| Severity Level | Count | Finding IDs |
|:---|:---:|:---|
| **CRITICAL** | 0 | None |
| **HIGH** | 0 | None |
| **MEDIUM** | 1 | **F-15E-10** (Historical hash ledger mismatch in report) |
| **LOW** | 3 | **F-15E-06** (Trap signal exit logging), **F-15E-08** (Negative sentinel check), **F-15E-09** (CSV column schema) |
| **INFORMATIONAL / PASS** | 7 | **F-15E-01**, **F-15E-02**, **F-15E-03**, **F-15E-04**, **F-15E-05**, **F-15E-07**, **F-15E-11** |

---

## Overall Audit Status

### **CONDITIONAL — SPECIFIC FINDINGS MUST BE RESOLVED**

**Audit Decision Rationale:**  
The cryptographic implementation and safety hardening in `pilot_runner.c` pass all technical criteria: the independent oracle is standard-conformant, the 4-way classifier is robust, and the 6-step transactional cleanup path guarantees memory safety.

However, because `PHASE15D_REPORT.md` recorded incorrect hashes for `PHASE15B_REPORT.md` and `PHASE15B_TRIAL_LEDGER.csv` (**F-15E-10**), and minor input/schema discrepancies exist (**F-15E-08**, **F-15E-09**), this audit issues a **CONDITIONAL** verdict. Project provenance records must be updated with the verified SHA-256 digests before live pilot authorization.
