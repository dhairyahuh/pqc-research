# Phase 18G — Evidence-Driven Implementation Gate and Standards Claim Correction

**Document:** `research/phase17_multi_fault_design/PHASE18G_IMPLEMENTATION_GATE_PLAN.md`  
**Date:** 2026-10-12  
**Target Specification Audited:** [PHASE18F_FINAL_SPECIFICATION_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18F_FINAL_SPECIFICATION_AUDIT.md)  
**Historical Proposal References:**
- [PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md)
- [PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md)
- [PHASE18C_INDEPENDENT_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md)
- [PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)  
**Active Source Files Directly Inspected:**
- [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c)
- [pilot_runner.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase14_persistent_arm_design/pilot_runner.c)
- [poly.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) & [zetas.inc](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc)
- [independent_oracle.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/independent_oracle.c) & [fips202_ref.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/fips202_ref.c)
- [mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h)  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** IMPLEMENTATION GATE PLAN AND STANDARDS CORRECTION (Documentation Only)  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified or created, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary & Final Verdict

# **READY FOR IMPLEMENTATION REVIEW**

### Executive Statement:
Phase 18G resolves the remaining standards claim discrepancies identified in Phase 18F and establishes a phased, evidence-driven implementation plan for the multi-fault experiment.

This document achieves four critical objectives:
1. **Correction of External Standards Claims (§1):** Removes unverified colloquial aliases (e.g., "CRC-16/AUTOSAR") from the CRC specification, defining the routine strictly by its verified mathematical parameters. Corrects external space-protocol citations by disentangling framing standards (CCSDS 355.0-B-1) from cryptographic algorithm suites (CCSDS 352.0-B-1), explicitly classifying the research transport protocol as a simplified software model rather than a flight-qualified standard.
2. **Audit of Implementation Contracts (§2):** Systematically inspects the actual C codebase against the proposed architecture, explicitly delineating implemented primitives from untested architectural designs across signal attribution, write-ahead logging, manifest expansion, and rejection oracle mechanics.
3. **Phased Implementation Sequence (Gates A through E, §3):** Defines the minimal, testable implementation sequence comprising five independently verifiable gates:
   - **Gate A:** Vector Preflight & Oracle Validation Harness (pure software cross-check against `liboqs v0.16.0`, 0 memory mutations).
   - **Gate B:** Ledger Validator with Synthetic Anomaly Test Fixtures (8 synthetic test files validating all error and tamper paths).
   - **Gate C:** Process Supervisor & Signal Attribution Test Suite (validating POSIX return codes, out-of-band IPC tokens, and unverified restoration logging).
   - **Gate D:** Single-Seed End-to-End Engineering Test ($i=1$, 4 condition trials, exercising persistent memory mutation, channel retry recovery, and baseline rechecks).
   - **Gate E:** Implementation Evidence Review & Operator Authorization Gate (formal audit of Gates A–D before the full 1,680-trial campaign).
4. **Traceability and Untested Boundaries (§4 & §5):** Documents the exact repository status, provides independently recomputed digests, and formally certifies that no implementation code has been written, compiled, or executed.

---

## 1. Correction of Unsupported Standards Claims

### 1.1 CRC Terminology and Alias Removal
- **Prior Claim in Phase 18F:** Described the framing CRC as "CRC-16/CCITT-FALSE (also known as CRC-16/AUTOSAR or CRC-16/IBM-3740)".
- **Audit Finding & Discrepancy:**
  - While informal online algorithm catalogues (e.g., Greg Cook's RevEng catalogue, crccalc) assign the label "CRC-16/AUTOSAR" to the parameter tuple `(poly=0x1021, init=0xFFFF, refin=false, refout=false, xorout=0x0000, check=0x29B1)`, AUTOSAR (AUTOmotive Open System ARchitecture) is an automotive industry software specification. Attributing an automotive domain standard to space-resilience research is extraneous and conceptually misleading.
  - Furthermore, under official ITU-T Recommendation V.41 (the formal CCITT standard), standard CRC-CCITT specifies bit reflection or specific complementation, making the colloquial term "CCITT-FALSE" an informal reverse-engineering moniker rather than an official standard name.
- **Formal Correction:**
  - Remove all colloquial and domain-mismatched aliases ("AUTOSAR", "CCITT-FALSE", "IBM-3740").
  - Define the algorithm strictly and exclusively by its source-verified mathematical parameters:
    - **Width:** 16 bits (`uint16_t`).
    - **Generator Polynomial (poly):** `0x1021` ($x^{16} + x^{12} + x^5 + 1$).
    - **Initial Register State (init):** `0xFFFF`.
    - **Input Bit Reflection (refIn):** `false` (MSB-first processing; byte shifted left by 8).
    - **Output Bit Reflection (refOut):** `false` (MSB-first processing; accumulator returned without reversal).
    - **Final XOR Mask (xorOut):** `0x0000` (None).
    - **Mathematical Check Value:** Exactly **`0x29B1`** on standard ASCII input `"123456789"` `[INDEPENDENTLY RECOMPUTED]`.
    - **Source Grounding:** Traced directly to [combined_campaign.c:39-44](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L39-L44) `[DIRECTLY OBSERVED]`.

### 1.2 Spacecraft Security Protocol Citations (CCSDS Scope Correction)
- **Prior Claim in Phase 18F:** Asserted that operational satellite links follow CCSDS 355.0-B-1 (SDLS), claiming that CCSDS 355.0-B-1 mandates "AES-GCM-256 or AES-CBC-256 with HMAC-SHA-256".
- **Audit Finding & Discrepancy:**
  - In Consultative Committee for Space Data Systems (CCSDS) literature:
    - **CCSDS 355.0-B-1** (Space Data Link Security Protocol) defines the protocol framing, Security Header (SPI, Sequence Number), Security Trailer (Authentication Tag), and security association management. It does **not** specify concrete cryptographic cipher suites.
    - Specific cryptographic algorithms are defined in a separate companion Blue Book: **CCSDS 352.0-B-1** (*CCSDS Cryptographic Algorithms*).
    - Furthermore, CCSDS standards allow configurable security service profiles (Authentication-only, Encryption-only, Authenticated Encryption) depending on mission constraints; AES-GCM is an approved profile, not a universally mandated requirement across all space links.
  - Asserting that CCSDS 355.0-B-1 directly mandates AES-GCM-256 conflated the protocol standard with the algorithm standard.
- **Formal Correction:**
  - Explicitly mark external claims regarding mandatory algorithms in CCSDS 355.0-B-1 as **corrected and disambiguated**: CCSDS 355.0-B-1 defines data-link security framing, while CCSDS 352.0-B-1 specifies algorithm suites (including AES-GCM and HMAC-SHA-256).
  - **Model Realism Boundary Re-Affirmed:** The transport protocol implemented in `combined_campaign.c:39-67` is a **simplified academic software simulation model** created to evaluate cross-layer interaction between physical/link layer faults and memory corruption. It is **not flight-qualified, not operational, and not standards-compliant** with CCSDS 355.0-B-1 or ECSS standards `[INFERRED]`.

---

## 2. Audit of the Implementation Contract (Direct Source vs. Proposed Specifications)

| Subsystem Contract | Active Repository Source Reality | Proposed Architecture Specification | Implementation Status & Boundary |
| :--- | :--- | :--- | :--- |
| **1. Signal Attribution** | `pilot_runner.c:198-203` installs handler calling `_exit(128+sig)`. In-process termination is normal POSIX exit (`138`/`139`). Direct signals yield `returncode < 0`. | Supervisor wrapper evaluates `proc.returncode < 0` vs `138`/`139`, using dedicated IPC pipe token (`TRAP_SIGNAL:...`) to verify handled traps. | **Untested Proposal:** IPC pipe and supervisor wrapper do not exist on disk `[PROPOSED / NOT YET TESTED]`. |
| **2. Write-Ahead Ledger** | `combined_campaign.c:236` uses single buffered `fopen("w")` and `fprintf`. `pilot_runner.c` buffers in memory array. | Two-phase logging (`START_ENTRY` and `FINALIZE_ENTRY`) with `fflush()` and `fsync()`. Hash covers bytes $0..M-1$ excluding seal. | **Untested Proposal:** Two-phase write-ahead ledger does not exist in any runner binary `[PROPOSED / NOT YET TESTED]`. |
| **3. Quotas & Manifest** | `combined_campaign.c:214-220` draws classes via `rand() % 7`. `pilot_runner.c` hardcodes 16 trials on KAT. | `manifest.json` serializes 420 master scenario objects enforcing exact quotas (Q1: 300, Q2: 40, Q3: 60, Q4: 20), expanded to 1,680 trials. | **Untested Proposal:** Manifest generator and canonical JSON do not exist on disk `[PROPOSED / NOT YET TESTED]`. |
| **4. Retry & PRF Semantics** | `combined_campaign.c:160-163` derives attempt seeds via PRF, but uses transient TFIB hooks and unstratified draws. | Unified runner applies persistent table mutation across retries ($a \in [0, 2]$) while re-drawing channel fault seeds under persistent mode. | **Untested Proposal:** Unified runner coordinating Mach-O mutations with channel retries does not exist `[PROPOSED / NOT YET TESTED]`. |
| **5. Memory Protection** | `pilot_runner.c:292-315` demonstrates Darwin ARM64 `vm_protect` RW/RO mutation on 1 KAT vector, restoring after 1 trial. | Session lifecycle holds table mutation active across all retries ($a \in [0, 2]$), restoring strictly at terminal session exit. | **Untested Proposal:** Multi-attempt persistent memory holding loop does not exist in code `[PROPOSED / NOT YET TESTED]`. |
| **6. Vector Preflight & Oracle** | Only Vector 0 exists in `mlkem_expected_kat.h`. Rejection oracle exists in `fips202_ref.c` / `independent_oracle.c`. | 6-point preflight validation against `liboqs v0.16.0` on Vectors 1–419, feeding exact wire bytes $\tilde{c}$ to TweetFIPS oracle. | **Untested Proposal:** Preflight harness linking `liboqs` does not exist on disk `[PROPOSED / NOT YET TESTED]`. |
| **7. Outcome Separation** | Historical harnesses conflated outcomes into single status columns. | Strict separation of Protocol Key Agreement ($Y_{\text{proto}}$), Cryptographic SDC ($Y_{\text{crypto}}$), and Execution Reliability ($Y_{\text{exec}}$). | **Fully Ratified Design:** Mathematical definitions verified, awaiting code implementation `[PROPOSED / NOT YET TESTED]`. |

---

## 3. Phased Implementation Sequence: Gates A through E

To transition from specification to dynamic execution without risking premature unverified testing, implementation must proceed through five sequential, independently verifiable gates:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PHASED IMPLEMENTATION ROADMAP                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GATE A: Vector Preflight & Oracle Validation Harness                  │
│ - Standalone tool: validate_vectors.c linking liboqs v0.16.0           │
│ - Zero virtual memory mutations (vm_protect NOT called)                │
│ - Verifies 420 keypairs, encapsulations, decapsulations, and oracles   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ PASS: All 420 vectors validated
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GATE B: Semantic Ledger Validator & Synthetic Test Suite               │
│ - Standalone validator: validate_ledger.py                             │
│ - Evaluates 8 synthetic test fixtures (valid, duplicates, truncated)   │
│ - Verifies byte-level SHA-256 seal and quota invariants (300/40/60/20) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ PASS: 100% fixture classification
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GATE C: Process Supervisor & Signal Attribution Test Suite             │
│ - Standalone supervisor: runner_supervisor.py                          │
│ - Evaluates 5 synthetic child exit scenarios (normal, abort, trap, kill│
│ - Verifies IPC pipe token and UNVERIFIED_PROCESS_ABORTED logging       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ PASS: Unambiguous signal attribution
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GATE D: Single-Seed End-to-End Engineering Test                       │
│ - Master Seed 1 executed under multi_fault_runner + supervisor         │
│ - Exercises 4 matched conditions (C00, C10, C01, C11)                  │
│ - Darwin ARM64 vm_protect + channel retries + canary + baseline KAT    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ PASS: Exact state matching
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ GATE E: Implementation Evidence Review & Operator Authorization Gate   │
│ - Independent audit of all logs, digests, and artifacts from Gates A-D │
│ - Explicit operator sign-off required prior to full campaign execution │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 3.1 Gate A: Vector Preflight and Rejection-Oracle Validation Harness
- **Purpose:** Validate the mathematical correctness of all 420 vector derivation seeds and the TweetFIPS-202 rejection oracle against an independent reference before touching virtual memory.
- **Software Boundary:** Zero memory mutation. `vm_protect` is strictly prohibited. Pure software execution.
- **Inputs:**
  - `manifest.json` (420 master scenario objects).
  - SUT ML-KEM-768 implementation (`algorithms/source_ref/mlkem/`).
  - Independent reference library: Open Quantum Safe (`liboqs v0.16.0`).
  - Standalone TweetFIPS-202 implementation (`tfib_experiments/phase11_oracle/fips202_ref.c`).
- **Pass / Fail Acceptance Criteria:**
  1. Keypair derivation: $pk_{\text{SUT}} == pk_{\text{OQS}}$ (1,184 bytes) and $sk_{\text{SUT}} == sk_{\text{OQS}}$ (2,400 bytes) across all 420 seeds.
  2. Encapsulation: $ct_{\text{SUT}} == ct_{\text{OQS}}$ (1,088 bytes) and $ss_{\text{SUT}} == ss_{\text{OQS}}$ (32 bytes) across all 420 seeds.
  3. Clean decapsulation: SUT decapsulation on clean $(ct, sk)$ returns status 0 and derives expected $ss$.
  4. Oracle rejection derivation: $K_{\text{rej}} = \text{SHAKE256}(z_i \parallel ct, 32)$ produces 32-byte secret distinct from valid $ss$.
  5. Tampered ciphertext rejection: Tampering $ct[0] \oplus 0x01$ causes decapsulation to match oracle rejection secret $K_{\text{rej}}(\tilde{c})$.
  6. Overall: Exactly 420/420 vectors pass. A single failure terminates execution with non-zero exit code.
- **Retained Artifacts:** `research/results/phase18_gates/gate_a_preflight_report.json` embedding SHA-256 digest of verified vectors.
- **Failure Behavior:** Fail-closed. Halts implementation before any memory-mutation harness is linked.

---

### 3.2 Gate B: Semantic Ledger Validator & Synthetic Test Suite
- **Purpose:** Empirically verify that `validate_ledger.py` correctly detects every valid ledger, structural tampering, quota violation, and crash anomaly.
- **Software Boundary:** Evaluated purely on synthetic, deterministic fixture files.
- **Inputs:** Eight synthetic ledger fixtures:
  1. `fixture_valid_complete.jsonl`: Exactly 1,680 valid finalized trial records (420 scenarios $\times$ 4 conditions) with matching quotas and valid `CAMPAIGN_SEAL`. Expected: `COMPLETE`.
  2. `fixture_duplicate_start.jsonl`: Contains two `START` records for trial `(12, C11)`. Expected: `INVALID_LEDGER`.
  3. `fixture_orphan_finalize.jsonl`: Contains a `FINALIZE` record without a preceding `START`. Expected: `INVALID_LEDGER`.
  4. `fixture_dangling_start.jsonl`: Contains a `START` record followed by EOF without `FINALIZE`. Expected: `PARTIAL_ABORTED`.
  5. `fixture_missing_condition.jsonl`: Seed 45 contains only $C_{00}, C_{10}, C_{01}$ (missing $C_{11}$). Expected: `PARTIAL_ABORTED`.
  6. `fixture_quota_violation.jsonl`: 299 Quota 1 scenarios instead of 300. Expected: `INVALID_LEDGER`.
  7. `fixture_corrupted_seal.jsonl`: Valid ledger where `content_sha256` has 1 altered bit. Expected: `INVALID_LEDGER`.
  8. `fixture_truncated_write.jsonl`: Trailing line missing `\n` or invalid JSON syntax. Expected: `INVALID_LEDGER`.
- **Pass / Fail Acceptance Criteria:**
  - `validate_ledger.py` achieves 100% (8/8) exact classification agreement with expected verdicts.
  - Verification of non-self-referential byte range ($0..M-1$) matches byte-for-byte.
- **Retained Artifacts:** `research/results/phase18_gates/gate_b_validator_report.json`.
- **Failure Behavior:** Halts implementation; ledger validator must be amended before runner integration.

---

### 3.3 Gate C: Process Supervisor and Signal Attribution Test Suite
- **Purpose:** Empirically verify that `runner_supervisor.py` correctly disambiguates exit codes, catches POSIX signals, reads IPC pipe tokens, and enforces unverified restoration logging.
- **Software Boundary:** Evaluated against dedicated synthetic mock child binaries (`mock_child_runner.c`).
- **Inputs:** Five synthetic child execution scenarios:
  1. *Clean Child Exit:* Child writes `START` and `FINALIZE`, exits with code 0. Expected: `NORMAL`.
  2. *Normal Error Exit:* Child writes `START`, exits with code 1. Expected: Supervisor finalizes ledger with `ABNORMAL_PROCESS_EXIT`, `restoration_status = UNVERIFIED_PROCESS_ABORTED`.
  3. *Handled Hardware Trap:* Child intercepts `SIGBUS`, writes `"TRAP_SIGNAL:SIGBUS\n"` to IPC pipe (FD 3), and calls `_exit(138)`. Expected: Supervisor detects IPC token and exit code 138, finalizes ledger with `SIGNAL_TERMINATION_HANDLER`, `restoration_status = UNVERIFIED_PROCESS_ABORTED`.
  4. *Direct Kernel Signal Kill:* Child receives unhandled `SIGSEGV` (`kill -11`). Expected: Supervisor detects `proc.returncode == -11`, finalizes ledger with `SIGNAL_TERMINATION_DIRECT`, `restoration_status = UNVERIFIED_PROCESS_ABORTED`.
  5. *Ambiguous Status 138 Exit:* Child exits with code 138 without writing IPC token. Expected: Supervisor detects absence of IPC token, finalizes ledger with `ABNORMAL_PROCESS_EXIT_AMBIGUOUS`, `restoration_status = UNVERIFIED_PROCESS_ABORTED`.
- **Pass / Fail Acceptance Criteria:**
  - 100% (5/5) correct attribution across all scenarios.
  - Zero cases where `restoration_status` is marked `RESTORED_AND_VERIFIED` following child process termination.
- **Retained Artifacts:** `research/results/phase18_gates/gate_c_supervisor_report.json`.
- **Failure Behavior:** Halts implementation; supervisor wrapper logic must be hardened.

---

### 3.4 Gate D: Controlled Single-Seed End-to-End Engineering Test
- **Purpose:** Execute a live, fully instrumented engineering test on exactly **Master Seed 1** ($N=1$, 4 trials: $C_{00}, C_{10}, C_{01}, C_{11}$) to verify live coordination between Darwin virtual memory mutations, external channel retries, canary checks, and write-ahead ledger logging.
- **Software Boundary:** Limited strictly to Master Seed 1. Full campaign ($N=420$) remains strictly unauthorized.
- **Inputs:** Master Seed 1 configuration from `manifest.json`.
- **Pass / Fail Acceptance Criteria:**
  1. *Condition $C_{00}$ (Clean Table, Clean Channel):* Attempt 0 establishes key ($Y_{\text{proto}} = 1$), decapsulation matches golden shared secret, table unmodified.
  2. *Condition $C_{10}$ (Mutated Table, Clean Channel):* Active twiddle mutation applied via `vm_protect`, page verified RO, Attempt 0 fails authentication (`K_MISMATCH`), Attempts 1 and 2 retry with persistent memory fault and fail, session exits with protocol abort ($Y_{\text{proto}} = 0$), table restored to golden twiddle, 16,128 padding bytes verified zero, baseline KAT decapsulation passes.
  3. *Condition $C_{01}$ (Clean Table, Channel Impaired):* Attempt 0 impaired by transient `CH_BIT`, decapsulation executes and yields canonical rejection ($K_{\text{rej}}$), MAC fails (`K_MISMATCH`), Attempt 1 transmits clean wire, decapsulation yields golden shared secret, key established on retry ($Y_{\text{proto}} = 1$, `RECOVERED_ON_RETRY`).
  4. *Condition $C_{11}$ (Mutated Table, Channel Impaired):* Combined fault active, Attempt 0 wire corrupted, decapsulation yields canonical rejection, MAC fails, Attempts 1 and 2 retry with persistent memory fault, all retries fail, session aborts ($Y_{\text{proto}} = 0$), table restored, canaries verified zero, baseline KAT decapsulation passes.
  5. *Ledger Integrity:* Output ledger `gate_d_ledger.jsonl` contains exactly 4 `START` records and 4 matching `FINALIZE` records, zero dangling starts, verified by `validate_ledger.py`.
- **Retained Artifacts:** `research/results/phase18_gates/gate_d_engineering_ledger.jsonl` and execution console log.
- **Failure Behavior:** If any step fails (e.g., memory restoration canary failure or baseline KAT mismatch), execution halts closed immediately (`EXIT_FAILURE = 1`).

---

### 3.5 Gate E: Implementation Evidence Review & Operator Authorization Gate
- **Purpose:** Formal audit and operator review of all evidence generated by Gates A, B, C, and D before any large-scale campaign is launched.
- **Inputs:** All test logs, JSON reports, ledgers, and SHA-256 digests from Gates A through D.
- **Pass / Fail Acceptance Criteria:**
  - Gate A: 420/420 vector validation passes.
  - Gate B: 8/8 ledger validator fixtures pass.
  - Gate C: 5/5 supervisor signal attribution scenarios pass.
  - Gate D: Master Seed 1 completes with exact expected condition outcomes, verified table restoration, and clean baseline KAT rechecks.
  - Independent Cryptographic Software Auditor issues formal certification of implementation readiness.
  - Explicit human operator authorization granted in repository records.
- **Failure Behavior:** If operator authorization is withheld or any test evidence is inconclusive, the full campaign remains **strictly unauthorized**.

---

## 4. Repository State and Recomputed SHA-256 File Hashes `[DIRECTLY OBSERVED]`

Computed via `shasum -a 256` on actual on-disk bytes:

| File Path | SHA-256 Digest | Status / Role |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18G_IMPLEMENTATION_GATE_PLAN.md` | *(Computed upon file write)* | **Phase 18G Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18G_CHANGELOG.md` | *(Computed upon file write)* | **Phase 18G Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18F_FINAL_SPECIFICATION_AUDIT.md` | `3669419d0cbee4f85e1b8581d5c940d9bf8cb72a1f5408fdc7ebd3aa8aba4bf0` | Historical Specification `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18F_CHANGELOG.md` | `b2159a970f0e6b598fad087e3b2b43e3d9708200fd42f48f3148c18746cef453` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md` | `f2f51ab6c8a9ad91efb7396d64b88a8c6e84a4266895c597048b689791e97a7d` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18E_CHANGELOG.md` | `9f87827e9c625aee41c73405e55638912c66d31185582e6bc0db0ac837f3402c` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md` | `987925793b543a4456c32bbaf47cc7f60ede0a1f88df7b7308861524fc624dac` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CHANGELOG.md` | `e5f631029d5a717819c5c7b51eff360291060344673e4e1e305829392a06a74e` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | `77dfabfe672e42de281e6299c8c692006e3fa3e707d5f2ec31cf902851aa6561` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | `2947278c38c14347ed24e199aada4ec00ebfe80377ede55efe81881571dfe782` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Superseded Proposal `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Ratification `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Architectural Reference `[DIRECTLY OBSERVED]` |

### Git Working Tree Status (`git status --short`) `[DIRECTLY OBSERVED]`
```
 M Makefile
 M README.md
 M algorithms/source_ref/mlkem/src/poly.c
 M algorithms/source_ref/mlkem/src/zetas.inc
 M experiments/fault_injection/mlkem768_internal_fault_experiment.c
 M experiments/system_model/spacecraft_protocol_sim.py
 M fault_injection/fault_models/fault_definitions.py
 M results/phase7i/processed/phase7i_e2e_results.json
 M results/spacecraft_protocol_desync_results.json
 M tests/test_fips_kats.c
?? research/phase17_multi_fault_design/PHASE18G_IMPLEMENTATION_GATE_PLAN.md
?? research/phase17_multi_fault_design/PHASE18G_CHANGELOG.md
```
- All 10 pre-existing tracked modifications preserved untouched.
- Zero files staged, committed, pushed, or reverted.

---

## 5. Final Status and Authorization Statement

# **READY FOR IMPLEMENTATION REVIEW**

### Explicit Governance Boundary:
Phase 18G establishes a testable, five-stage implementation roadmap (Gates A through E) and corrects all external standards claims.

**This document does NOT authorize compiling binaries, linking test harnesses, mutating virtual memory, generating vector corpora, or executing experimental trials.** Those actions require separate human operator authorization under subsequent review gates.
