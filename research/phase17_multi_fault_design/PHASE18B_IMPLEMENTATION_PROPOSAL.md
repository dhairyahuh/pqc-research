# Phase 18B — Formal Implementation Proposal and Architecture Specification

**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Date:** 2026-10-12  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software Study  
**Status:** IMPLEMENTATION PROPOSAL (Planning and Static Analysis Only — No Code or Experiments)  
**Deliverable Directory:** `research/phase17_multi_fault_design/`  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified or created, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary & Final Verdict

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Proposal Overview:
This document defines the formal software architecture, interface contracts, state transitions, manifest schema, vector validation protocol, failure containment models, and review gates required to implement the ratified Phase 17 multi-fault experiment ([PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)).

### Core Structural Finding:
Existing repository implementations partition the required functionality across disconnected harnesses:
- [pilot_runner.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase14_persistent_arm_design/pilot_runner.c) demonstrates Darwin ARM64 persistent table mutation via `vm_protect`, padding canary verification, and readback checks, but hardcodes 16 trials on a single KAT vector without channel faults `[DIRECTLY OBSERVED]`.
- [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c) demonstrates external communication channel faults and transport retry handling, but applies transient TFIB software hooks instead of persistent Mach-O page mutations and uses unstratified random sampling `[DIRECTLY OBSERVED]`.
- [zetas.inc](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc) and [poly.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) provide compile-time isolated storage (`__DATA_CONST,__zetas_page`) guarded by `MLKEM_RESEARCH_RELOCATE_ZETAS` `[DIRECTLY OBSERVED]`.

This proposal specifies a dedicated, unified research-only runner—provisionally named `multi_fault_runner.c`—that unifies these subsystems under a deterministic, frozen scenario manifest. **No implementation code is written, compiled, or executed in this phase.**

---

## 1. Mandatory Research-Integrity Protocol and Evidence Standards

In strict accordance with the **Mandatory Research Integrity and Anti-Hallucination Protocol**, every factual statement, calculation, and finding in this document is labeled with its exact evidentiary basis:
- `[DIRECTLY OBSERVED]`: Supported by direct inspection of active source lines, local files, or command outputs in this session.
- `[INDEPENDENTLY RECOMPUTED]`: Verified by independent mathematical calculation from stated inputs.
- `[REPORTED BY A PRIOR PHASE]`: Present in historical documentation but not independently executed dynamically in this phase.
- `[INFERRED]`: Logically deduced from observed facts, with the deduction chain explicitly stated.
- `[PROPOSED / NOT YET TESTED]`: Formally specified design parameters or algorithm definitions awaiting implementation or execution.
- `[UNKNOWN / UNVERIFIED]`: Information that is missing, contradictory, or lacks empirical confirmation.

---

## 2. Unified Runner Architecture (`multi_fault_runner.c`)

### 2.1 Subsystem Coordination Model
The unified runner coordinates six functional subsystems in a single execution unit `[PROPOSED / NOT YET TESTED]`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      UNIFIED MULTI-FAULT RUNNER                        │
│                         (multi_fault_runner.c)                         │
└──────┬──────────────────┬──────────────────┬────────────────────┬──────┘
       │                  │                  │                    │
       ▼                  ▼                  ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐     ┌──────────────┐
│   Scenario   │   │  Preflight   │   │ Architecture │     │ Independent  │
│   Manifest   │   │ Vector Suite │   │ Memory Hook  │     │ Rejection    │
│ (manifest.   │   │  (liboqs vs  │   │ (__DATA_     │     │ Oracle       │
│    json)     │   │     SUT)     │   │   CONST)     │     │ (TweetFIPS)  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘     └──────┬───────┘
       │                  │                  │                    │
       └──────────────────┴─────────┬────────┴────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │   Transport & Retry Engine   │
                     │  - Channel Fault Injection   │
                     │  - CRC-16 Frame Encoding     │
                     │  - ML-KEM-768 Decapsulation  │
                     │  - Retry Loop (Attempts 0..2)│
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Structured Authoritative     │
                     │ Ledgers (CSV / JSONL)        │
                     │ - Protocol Endpoint          │
                     │ - Cryptographic Endpoint     │
                     │ - Execution Reliability Table│
                     └──────────────────────────────┘
```

### 2.2 Ten-Step Session Lifecycle Contract
For every master seed $i \in [1, 420]$ and matched condition $C \in \{C_{00}, C_{10}, C_{01}, C_{11}\}$, `multi_fault_runner.c` executes the following sequential lifecycle `[PROPOSED / NOT YET TESTED]`:

1. **Step 1: Manifest Ingestion and Verification:**
   - Ingest `manifest.json`. Compute SHA-256 digest of manifest bytes in memory.
   - Assert manifest digest matches expected preregistration hash. If mismatch, halt immediately (`EXIT_MANIFEST_CORRUPT`).
2. **Step 2: Preflight Vector Corpus Validation:**
   - Before any memory mutation or trial execution, execute the 6-point preflight cross-check against `liboqs v0.16.0` across all 419 local vectors.
   - Assert all vectors pass keypair, encapsulation, clean decapsulation, and rejection oracle baseline checks.
   - If any vector fails, halt immediately (`EXIT_PREFLIGHT_FAILED`) without modifying memory protections.
3. **Step 3: Baseline Memory State Snapshot:**
   - Resolve mutable table pointer via `mlkem_research_get_zetas_mutable_ptr()`.
   - Calculate 16KB page boundary: `page_addr = table_addr & ~(0x4000 - 1)`.
   - Query live Darwin virtual memory mapping via `vm_region_64`.
   - Assert page is strictly read-only (`VM_PROT_READ`), 16KB aligned, table matches `golden_zetas` (256 bytes), and all 16,128 padding bytes are zero.
4. **Step 4: Matched Condition Parameter Binding:**
   - Extract assigned parameters for condition $C$:
     - Table state: Clean ($C_{00}, C_{01}$) vs. Mutated ($C_{10}, C_{11}$).
     - Channel state: Clean ($C_{00}, C_{10}$) vs. Armed ($C_{01}, C_{11}$).
     - Persistence: Memory fault persistent across all retries; channel fault evaluated per `channel_persistence` (`TRANSIENT` vs. `PERSISTENT`).
5. **Step 5: Persistent Table Mutation (Conditions $C_{10}$ and $C_{11}$):**
   - Execute `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE)`.
   - Write mutated value: `vtable[target_idx] = orig_val ^ bit_mask`.
   - Perform immediate volatile readback: `ASSERT(vtable[target_idx] == target_val)`.
   - Reprotect to read-only: `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ)`.
   - Verify page protection is read-only via `vm_region_64` **prior to decapsulation**.
6. **Step 6: Protocol Transmission & Retransmission Execution:**
   - For attempt $a = 0, 1, 2$ ($\text{RETRY\_MAX} = 2$):
     - Determine channel state: Active if $a = 0$ or `channel_persistence == PERSISTENT`.
     - Construct frame: payload, CRC-16, keystream encryption, MAC tag.
     - Apply channel fault to wire buffer:
       - `CH_BIT`: inverts bit in ciphertext bytes (`wire[pos] ^= mask`, $pos < 1088$).
       - `CH_DUP`, `CH_REORDER`: sets sequence metadata; wire ciphertext bytes remain clean.
       - `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_INTERRUPT`: delivery blocks (`decaps_ran = 0`), returns appropriate transport code (`K_MALFORMED`, `K_LOST`, `K_TIMEOUT`).
     - If wire delivered: invoke SUT `mlkem768_dec(ss_dec, ct_wire, sk)` under read-only table permissions (`decaps_ran = 1`).
     - Derive canonical rejection secret: $K_{\text{rej}} = \text{SHAKE256}(z_i \parallel ct_{\text{wire}}, 32)$ using received wire bytes.
     - Evaluate MAC tag. If valid and frame parses, session succeeds ($Y_{\text{proto}} = 1$); break retry loop.
7. **Step 7: Terminal Table Restoration (Conditions $C_{10}$ and $C_{11}$):**
   - At terminal session exit (after attempt loop finishes or breaks):
   - Unprotect page: `vm_protect` to RW.
   - Restore original golden twiddle: `vtable[target_idx] = orig_val`.
   - Perform immediate volatile readback: `ASSERT(vtable[target_idx] == orig_val)`.
   - Reprotect page: `vm_protect` to RO.
8. **Step 8: Restoration and Invariant Verification:**
   - Verify live Darwin virtual memory protection is read-only via `vm_region_64`.
   - Verify table memory bit-for-bit matches `golden_zetas` (256 bytes).
   - Verify all 16,128 padding bytes are strictly zero.
   - If any verification fails, flag `RESTORATION_FAILED` and halt campaign immediately (`EXIT_RESTORATION_HALT`).
9. **Step 9: Post-Session Clean Baseline Decapsulation Check:**
   - Execute SUT `mlkem768_dec(ss_check, test_vector_ct, test_vector_sk)` on golden KAT vector.
   - Assert `ss_check == test_vector_ss`. If mismatch, halt campaign immediately.
10. **Step 10: Authoritative Record Emission:**
    - Emit structured record to trial ledger only if Steps 1–9 executed without unhandled errors.

### 2.3 Error Paths and Signal Termination Handling
- **Ordinary Error Paths:** If any assertion, `vm_protect` call, or readback fails, execution branches to structured cleanup (Step 7–9). If cleanup fails, execution halts closed with non-zero exit code.
- **Signal Interception (`SIGBUS`, `SIGSEGV`):**
  - Handlers write emergency alert to `STDERR` and call `_exit(128 + sig)`.
  - **Evidentiary Boundary:** A signal handler terminating via `_exit()` **cannot perform or verify in-process table restoration**.
  - **Operating System Protection:** On Darwin ARM64, anonymous COW virtual memory pages modified by a process are discarded by the kernel upon process teardown. However, the runner ledger **shall never record `RESTORED` if the process terminated via signal**; the trial must be logged as `SIGNAL_TERMINATION` with restoration status `UNVERIFIED_PROCESS_ABORTED`.

---

## 3. Ratified Design Requirements Traceability Matrix

| Ratified Requirement | Target Architecture Component | Verification Method & Implementation Gate |
| :--- | :--- | :--- |
| **Q1: 300 active twiddle $\times$ `CH_BIT`** | Manifest generator & Quota 1 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q2: 20 `CH_DUP`, 20 `CH_REORDER`** | Manifest generator & Quota 2 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q3: 15 each across 4 blocking classes** | Manifest generator & Quota 3 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q4: 5 per control cell ($2 \times 2$ grid)** | Manifest generator & Quota 4 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **$N = 420$ seeds, $1,680$ trial records** | Manifest master array ($420 \times 4$) | Gate 2 (Manifest Schema Review) |
| **Matched conditions ($C_{00}, C_{10}, C_{01}, C_{11}$)** | Runner session execution loop (Step 4–6) | Gate 4 (Runner Code Review) |
| **Table fault persists across retries** | State held across attempt loop ($a \in [0, 2]$) | Gate 4 (Runner Code Review) |
| **Channel persistence semantics** | `combined_campaign.c:160` logic port | Gate 4 (Runner Code Review) |
| **Channel-stratified primary contrasts** | Post-processing script (`analyze_results.py`) | Gate 5 (Statistical Pipeline Review) |
| **Exploratory equal $1/7$ weighting** | Post-processing script (`analyze_results.py`) | Gate 5 (Statistical Pipeline Review) |
| **Separate Protocol, Crypto, Reliability** | Schema definition in output ledger | Gate 2 (Schema Review) & Gate 4 (Runner Review) |

---

## 4. Deterministic Manifest Specification (`manifest.json`)

### 4.1 Canonical Schema and Data Dictionary
The manifest must be generated and frozen prior to campaign execution. Each scenario entry is a JSON object with strictly ordered keys `[PROPOSED / NOT YET TESTED]`:

```json
{
  "scenario_id": 1,
  "master_seed_uint64": "0x0000000000000001",
  "quota_stratum": "QUOTA_1_ADMITTED_CORRUPTED",
  "vector": {
    "vector_id": 1,
    "provenance": "DETERMINISTIC_SHAKE256_DERAND",
    "keygen_seed_hex": "4a7b...",
    "encaps_seed_hex": "b91c..."
  },
  "memory_fault": {
    "target_index": 45,
    "bit_mask_hex": "0x0001",
    "control_type": "ACTIVE_MUTATION",
    "persistence": "PERSISTENT_ACROSS_RETRIES"
  },
  "channel_fault": {
    "channel_class": "CH_BIT",
    "bit_position": 142,
    "bit_mask_hex": "0x04",
    "truncation_bytes": 0,
    "delay_ticks": 1,
    "persistence": "TRANSIENT"
  },
  "protocol": {
    "retry_max": 2,
    "deadline_ticks": 100,
    "matched_conditions": ["C00", "C10", "C01", "C11"]
  }
}
```

### 4.2 Canonical Serialization and Hashing
- **Canonical Serialization Rule:** Canonical JSON serialization requires:
  1. UTF-8 encoding without byte-order mark (BOM).
  2. Strict alphabetical sorting of all object keys.
  3. No unnecessary whitespace (compact mode: separators `,` and `:`).
  4. Lowercase hex formatting for all byte arrays (`0x` prefix omitted or standardized).
  5. Deterministic newline termination (`\n`) for JSONL formats.
- **Manifest Integrity Hash:** The complete serialized manifest is hashed with SHA-256. This digest is embedded in the preregistration document and hardcoded into `multi_fault_runner.c`. If the runtime manifest hash diverges, the runner aborts before preflight.

### 4.3 Validation and Quota Rejection Rules
The manifest generator must validate the following invariants before outputting:
1. Exactly 420 master seeds, with zero duplicate `master_seed_uint64` values.
2. Quota 1 contains exactly 300 entries (`CH_BIT`, $k \in [1, 127]$, mask $\neq 0$).
3. Quota 2 contains exactly 40 entries (20 `CH_DUP`, 20 `CH_REORDER`, $k \in [1, 127]$, mask $\neq 0$).
4. Quota 3 contains exactly 60 entries (15 each for TRUNC, LOSS, DELAY, INTERRUPT, $k \in [1, 127]$, mask $\neq 0$).
5. Quota 4 contains exactly 20 entries (5 dormant-clean, 5 dormant-bit, 5 sham-clean, 5 sham-bit).
6. Any out-of-bounds target index ($k < 0$ or $k \ge 128$) or unassigned quota rejects the manifest generation.

---

## 5. Vector Corpus and Independent Oracle Contract

### 5.1 On-Disk Vector Inventory vs. Future Generation
- **Static Official KAT (Vector 0):** Directly observed in [references/test_vectors/mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h) `[DIRECTLY OBSERVED]`.
- **Planned Local Vectors (Vectors 1–419):** Zero locally generated vectors exist on disk `[DIRECTLY OBSERVED]`. They must be generated at runtime via deterministic PRF draws `[PROPOSED / NOT YET TESTED]`.

### 5.2 Six-Point Preflight Verification Contract
Before any memory mutation occurs, an independent preflight tool (`validate_vectors`) must execute the following assertions for each vector $i \in [1, 419]$:

```
[ Step 1: Deterministic Keypair Generation ]
  seed64_i = SHAKE256("kemkp" || seed_i, 64)
  SUT:    mlkem768_keypair_derand(pk_sut, sk_sut, seed64_i)
  liboqs: OQS_KEM_ml_kem_768_keypair_derand(pk_oqs, sk_oqs, seed64_i)
  ASSERT(memcmp(pk_sut, pk_oqs, 1184) == 0)
  ASSERT(memcmp(sk_sut, sk_oqs, 2400) == 0)

[ Step 2: Deterministic Encapsulation ]
  seed32_i = SHAKE256("kemenc" || seed_i, 32)
  SUT:    mlkem768_enc_derand(ct_sut, ss_sut, pk_sut, seed32_i)
  liboqs: OQS_KEM_ml_kem_768_encaps_derand(ct_oqs, ss_oqs, pk_oqs, seed32_i)
  ASSERT(memcmp(ct_sut, ct_oqs, 1088) == 0)
  ASSERT(memcmp(ss_sut, ss_oqs, 32) == 0)

[ Step 3: Clean Decapsulation Baseline ]
  rc = mlkem768_dec(ss_dec, ct_sut, sk_sut)
  ASSERT(rc == 0)
  ASSERT(memcmp(ss_dec, ss_sut, 32) == 0)

[ Step 4: Standalone Rejection Oracle Derivation ]
  z_i = sk_sut + 2368  (last 32 bytes of 2400-byte sk)
  z_c = z_i || ct_sut  (32 bytes z + 1088 bytes ct = 1120 bytes)
  fips202_ref_shake256(krej_base, 32, z_c, 1120)
  ASSERT(memcmp(krej_base, ss_sut, 32) != 0)  (Rejection distinct from valid SS)

[ Step 5: Test Corruption Rejection Invariant ]
  ct_tamper = ct_sut; ct_tamper[0] ^= 0x01
  fips202_ref_shake256(krej_tamper, 32, z_i || ct_tamper, 1120)
  ASSERT(memcmp(krej_tamper, krej_base, 32) != 0)

[ Step 6: Memory Layout and Size Verification ]
  ASSERT(sizeof(pk) == 1184 && sizeof(sk) == 2400 && sizeof(ct) == 1088 && sizeof(ss) == 32)
```

If any assertion fails, preflight outputs `PREFLIGHT_FAIL: Vector i invalid` and exits with code 1.

### 5.3 Oracle Architecture and Provenance Scope
- **Source Separation:** The rejection oracle implementation resides in `tfib_experiments/phase11_oracle/fips202_ref.c` (an 86-line standalone C implementation of Keccak-f[1600] based on TweetFIPS-202) `[DIRECTLY OBSERVED]`.
- **Provenance Boundary:** The oracle is designated an **architecturally independent reference implementation**. It is **not** designated a legal "clean-room" implementation, as the repository lacks institutional firewall provenance documentation `[INFERRED]`.
- **Golden Secret Semantics under Wire Corruption:**
  - Sender holds $K_{\text{golden}}$ (encapsulation shared secret on clean $c$).
  - Receiver decapsulates wire bytes $\tilde{c}$, producing $ss_{\text{dec}}$.
  - Independent oracle derives $K_{\text{rej}}(\tilde{c}) = \text{SHAKE256}(z_i \parallel \tilde{c}, 32)$.
  - Protocol agreement fails because $K_{\text{golden}} \neq K_{\text{rej}}(\tilde{c})$.
  - Cryptographic SDC occurs **strictly when** $ss_{\text{dec}} \neq K_{\text{golden}} \land ss_{\text{dec}} \neq K_{\text{rej}}(\tilde{c})$. Normal rejection ($ss_{\text{dec}} == K_{\text{rej}}(\tilde{c})$) is **never classified as SDC** `[INFERRED]`.

---

## 6. Statistical Contract and Estimands

### 6.1 Matched Interaction Contrast Estimands
For each channel class $c \in \{\text{BIT}, \text{DUP}, \text{REORDER}, \text{TRUNC}, \text{LOSS}, \text{DELAY}, \text{INTERRUPT}\}$, the interaction contrast is:

$$\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$$

- **Primary Presentation:** **Channel-Stratified Contrasts**. Evaluated individually for each class $c$.
- **Exploratory Aggregate Contrast:**
  $$\hat{\Delta}_{\text{std}} = \frac{1}{7} \sum_{c \in \text{Active Classes}} \hat{\Delta}_c$$
  - Strictly **EXPLORATORY**; defines an artificial standardized metric with equal mechanism weighting ($1/7$), not an empirical space-link probability distribution `[INFERRED]`.
- **Stratum Replication Resolution:**
  - In Quota 1 (`CH_BIT`), $N_1 = 300$ master seeds provide high precision.
  - In Quota 2 (`CH_DUP`, `CH_REORDER`), $n = 20$ seeds per class.
  - In Quota 3 (blocking classes), $n = 15$ seeds per class.
  - In Quota 4 (controls), $n = 5$ seeds per cell.
  - *Limitation Documented:* Differential sample sizes result in differing confidence interval widths across strata. Bootstrap standard errors will naturally reflect these sample size differences; no unweighted cross-stratum pooling is permitted `[INFERRED]`.

### 6.2 Denominators and Funnel Tracking
Every assigned trial is tracked through explicit, separate denominators:
- $N_{\text{assigned}} = 420$ master seeds ($1,680$ trial records).
- $N_{\text{eligible}} \le 420$: seeds whose vectors pass preflight cross-checks.
- $N_{\text{attempted}} \le N_{\text{eligible}}$: sessions reaching execution start.
- $N_{\text{completed\_sessions}}$: sessions running to terminal exit without hardware trap.
- $n_{\text{completed\_decaps}}$: Attempt 1 decapsulations under $C_{11}$ active twiddle $\times$ `CH_BIT` returning status 0.
- $N_{\text{analysable\_quads}}$: matched quadruples available for paired interaction analysis.

### 6.3 Exact Clopper–Pearson Upper Bound Evaluation
For zero SDC events ($k = 0$) in $n$ eligible completed first-attempt decapsulations:

$$p_U(n) = 1 - (0.05)^{1/n}$$

- $n = 300 \implies p_U = \mathbf{0.993608\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`.
- $n = 299 \implies p_U = \mathbf{0.996915\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`.
- $n = 298 \implies p_U = \mathbf{1.000243\% \ge 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`.
- $n = 0 \implies \text{UNDEFINED}$ (`INCONCLUSIVE_NO_COMPLETED_TRIALS`, no numerical bound) `[PROPOSED / NOT YET TESTED]`.

---

## 7. Fault Isolation, Safety, and Record Formats

### 7.1 Research-Only Build Boundary
- In `algorithms/source_ref/mlkem/src/zetas.inc:17-48` and `poly.c:269-278`, all mutable accessors and relocated pages are enclosed within `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)` `[DIRECTLY OBSERVED]`.
- Production builds omit this flag; any attempt to link `multi_fault_runner` against production fails at link time with missing symbols.

### 7.2 Observable States and Authoritative Ledger Schema
Output records are written to a structured CSV ledger containing distinct status columns `[PROPOSED / NOT YET TESTED]`:

| Column Name | Allowed Discrete States / Formats | Meaning / Semantics |
| :--- | :--- | :--- |
| `master_seed_id` | Integer ($1..420$) | Stable identifier matching scenario manifest |
| `condition` | `C00`, `C10`, `C01`, `C11` | Matched four-condition identifier |
| `attempt_id` | Integer ($0..2$) | Protocol transmission attempt index |
| `quota_stratum` | `Q1_CORRUPTED`, `Q2_CLEAN`, `Q3_BLOCK`, `Q4_CTRL` | Experimental allocation stratum |
| `channel_class` | `CLEAN`, `BIT`, `DUP`, `REORDER`, `TRUNC`, `LOSS`, `DELAY`, `INTERRUPT` | Assigned transport impairment class |
| `execution_status` | `NOT_ATTEMPTED`, `ATTEMPTED_COMPLETED`, `SIGNAL_TERMINATION`, `PROTECT_ERROR`, `ORACLE_FAILURE` | Execution survival and operating system state |
| `protocol_outcome` | `KEY_ESTABLISHED`, `RECOVERED_ON_RETRY`, `PROTOCOL_ABORT`, `MALFORMED_FRAME`, `FRAME_LOST`, `TIMEOUT_EXHAUSTED` | Protocol key establishment outcome |
| `crypto_endpoint` | `VALID_GOLDEN`, `CANONICAL_REJECTION`, `CRYPTO_SDC`, `NOT_RUN_DELIVERY_BLOCKED` | Receiver decapsulation cryptographic classification |
| `restoration_status` | `RESTORED_AND_VERIFIED`, `RESTORATION_FAILED`, `NOT_APPLICABLE_CLEAN`, `UNVERIFIED_ABORT` | In-process memory restoration verification state |
| `output_ss_hex` | 64-character lowercase hex string | 32-byte shared secret returned by decapsulation |

### 7.3 Fail-Closed Campaign Exit Policy
If execution aborts prematurely ($trials\_completed < 1680$):
- Output header explicitly prints `PARTIAL TRIAL LEDGER (ABORTED RUN - %d/1680 RECORDED)`.
- Runner exits with non-zero status code (`EXIT_FAILURE = 1`).
- No final summary claims or complete-campaign markers may be generated.

---

## 8. Review Gates and Phased Implementation Roadmap

Implementation must proceed through six distinct, strictly sequential review gates `[PROPOSED / NOT YET TESTED]`:

```
[ Gate 1: Architecture Approval (Phase 18B - Current Proposal) ]
                         │
                         ▼
[ Gate 2: Manifest Generator & Canonical Schema Review (Phase 18C) ]
  - Review generate_manifest.py / manifest.json schema
  - Statically verify quotas: Q1 (300), Q2 (40), Q3 (60), Q4 (20)
  - Verify canonical SHA-256 serialization
                         │
                         ▼
[ Gate 3: Vector Preflight & Oracle Harness Review (Phase 18D) ]
  - Review validate_vectors.c linking liboqs v0.16.0
  - Review TweetFIPS-202 rejection derivation harness
  - Verify fail-closed preflight abort logic
                         │
                         ▼
[ Gate 4: Unified Runner C Source & Memory Review (Phase 18E) ]
  - Statically inspect multi_fault_runner.c
  - Audit vm_protect transitions, bounds checks, padding canaries
  - Verify signal interception and session retry persistence loop
                         │
                         ▼
[ Gate 5: Statistical Analysis Pipeline Review (Phase 18F) ]
  - Review analyze_multi_fault.py / bootstrap inference code
  - Verify Clopper-Pearson bound calculation and shortfall logic
  - Verify stratified reporting and exploratory 1/7 weighting
                         │
                         ▼
[ Gate 6: Human Operator Execution Authorization (Phase 19) ]
  - Human experimental operator reviews all audited deliverables
  - Explicit operator authorization required to compile & run
```

---

## 9. Known Limitations and Untested Claims

In strict accordance with audit integrity rules:
1. **Dynamic Vector Correctness is Untested:** The mathematical validity of Vectors 1–419 cannot be verified until Gate 3 review and preflight execution occur `[PROPOSED / NOT YET TESTED]`.
2. **Mach-O Page Attrition Rate is Untested:** Whether 1,680 consecutive `vm_protect` transitions on Darwin ARM64 will experience hardware traps cannot be verified without physical execution `[UNKNOWN / UNVERIFIED]`.
3. **Signal Handler Restoration Boundary:** If the process receives `SIGKILL` or an unhandled hardware trap during the microsecond RW window, in-process restoration code cannot run. Kernel process teardown discards anonymous copy-on-write modifications, but in-process verification remains unexecutable `[INFERRED]`.
4. **Differential Stratum Precision:** Secondary protocol contrast estimates for Quotas 2, 3, and 4 will have wider confidence intervals than Quota 1 due to smaller sample sizes ($n=15..20$ vs. $n=300$) `[INFERRED]`.

---

## 10. Repository State and Hash Verification

### 10.1 Independently Computed SHA-256 Digests `[DIRECTLY OBSERVED]`
Computed via `shasum -a 256` on actual on-disk file bytes:

| File Path | SHA-256 Digest | Status / Role |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_CHANGELOG.md` | `6c3a4ce7e3d4a69c83fd8606c79aaf1ba549f5a61bc871148bea4dba6b42e673` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md` | `faf155420c3dad1fe0085729943e2b899289165f8f38f3becb9b244a03b92340` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_CHANGELOG.md` | `b0fed1b4e5fdfa9821baf35300dbc97e140e929c19b38063cdc09bd1b23f768b` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |

### 10.2 Git Repository State
- Verified via `git status` `[DIRECTLY OBSERVED]`.
- Branch: `space-resilience-framework`.
- Pre-existing uncommitted changes in 10 tracked files were preserved untouched.
- Zero files staged, committed, pushed, cleaned, or reverted.

---

## 11. Final Status and Authorization Boundary

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Explicit Governance Boundary:
This implementation proposal provides the comprehensive technical specification required to review and implement the ratified Phase 17 multi-fault campaign.

**This document does NOT authorize compiling binaries, linking test harnesses, mutating virtual memory, generating vector corpora, or executing experimental trials.** Those actions are deferred to subsequent gates and require separate, explicit human operator authorization.
