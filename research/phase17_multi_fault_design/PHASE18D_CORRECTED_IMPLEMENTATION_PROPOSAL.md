# Phase 18D — Corrected Implementation Proposal and Architecture Specification

**Document:** `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md`  
**Date:** 2026-10-12  
**Target Proposal Superseded:** [PHASE18B_IMPLEMENTATION_PROPOSAL.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md)  
**Audit Findings Incorporated:** [PHASE18C_INDEPENDENT_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md)  
**Ratified Design Foundation:** [PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** CORRECTED IMPLEMENTATION PROPOSAL (Planning and Static Analysis Only — No Code or Experiments)  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified or created, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary & Final Verdict

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Proposal Overview:
This document supersedes Phase 18B by providing the formal, corrected implementation proposal and architecture specification for the ratified Phase 17 multi-fault experiment (*Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software Study*).

It directly addresses and resolves all four material findings (Amendments A-1 through A-4) identified in the independent audit ([PHASE18C_INDEPENDENT_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md)):
1. **Durable Write-Ahead Logging and Process Supervision (Amendment A-1):** Replaces the flawed Step 10 conditional emission rule with a two-phase write-ahead logging (WAL) protocol (`START_ENTRY` and `FINALIZE_ENTRY`) combined with an external process supervisor wrapper (`runner_supervisor.py`). Guarantees that hardware trap signals (`SIGBUS`/`SIGSEGV`) and early exits are recorded as `SIGNAL_TERMINATION` with `UNVERIFIED_PROCESS_ABORTED`, preserving complete-case accounting across all 1,680 trials.
2. **Dual-Layer Protocol Framing and Acceptance Contract (Amendment A-2):** Formally disentangles the outer 32-byte cryptographic MAC tag (`mactag` via SHAKE256) from the inner 16-bit payload checksum (`crc16`), grounding framing, encryption, and priority of error codes directly in [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c).
3. **Disambiguated Estimand Scope for Contrast $\Delta_c$ (Amendment A-3):** Formally restricts the matched interaction contrast $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$ strictly to the binary Protocol Key Agreement outcome ($Y_{\text{proto}}$). Cryptographic SDC ($Y_{\text{crypto}}$) is evaluated separately as a conditional rate on completed decapsulations via exact Clopper–Pearson upper bounds.
4. **Deterministic Manifest Structure and Retry Semantics (Amendment A-4):** Specifies a canonical manifest format storing 420 master scenario objects in `manifest.json`, formalizes deterministic expansion into the four matched conditions ($C_{00}, C_{10}, C_{01}, C_{11}$), and defines attempt-specific PRF parameter draws for retry impairments under persistent channels.

**No implementation code is written, compiled, or executed in this phase.**

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

## 2. Unified Runner and Process Supervisor Architecture

### 2.1 Subsystem Coordination Model
The experimental execution pipeline coordinates seven functional components via a dual-layer process architecture `[PROPOSED / NOT YET TESTED]`:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PROCESS SUPERVISOR WRAPPER                        │
│                         (runner_supervisor.py)                         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Spawns & monitors child process
                                    ▼
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
                     │  - Outer MAC / Inner CRC-16  │
                     │  - ML-KEM-768 Decapsulation  │
                     │  - Retry Loop (Attempts 0..2)│
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Durable Append-Only Ledger   │
                     │  - START_ENTRY (Write-Ahead) │
                     │  - FINALIZE_ENTRY (Terminal) │
                     │  - fsync() per record        │
                     └──────────────────────────────┘
```

### 2.2 Ten-Step Session Lifecycle Contract (with Write-Ahead Logging)
For every master seed $i \in [1, 420]$ and matched condition $C \in \{C_{00}, C_{10}, C_{01}, C_{11}\}$, the execution pipeline enforces the following sequential lifecycle `[PROPOSED / NOT YET TESTED]`:

1. **Step 1: Manifest Ingestion and Verification:**
   - Ingest `manifest.json`. Compute SHA-256 digest of canonical manifest bytes.
   - Assert manifest digest matches expected preregistration hash. If mismatch, halt immediately (`EXIT_MANIFEST_CORRUPT`).
2. **Step 2: Preflight Vector Corpus Validation:**
   - Before any memory protection modification or trial execution, execute the 6-point preflight cross-check against `liboqs v0.16.0` across all 419 local vectors.
   - Assert all vectors pass keypair, encapsulation, clean decapsulation, and rejection oracle baseline checks.
   - If any vector fails, halt immediately (`EXIT_PREFLIGHT_FAILED`) without modifying memory protections.
3. **Step 3: Baseline Memory State Snapshot:**
   - Resolve mutable table pointer via `mlkem_research_get_zetas_mutable_ptr()`.
   - Calculate 16KB page boundary: `page_addr = table_addr & ~(0x4000 - 1)`.
   - Query live Darwin virtual memory mapping via `vm_region_64`.
   - Assert page is strictly read-only (`VM_PROT_READ`), 16KB aligned, table matches `golden_zetas` (256 bytes), and all 16,128 padding bytes are zero.
4. **Step 4: Write-Ahead Pre-Execution Ledger Emission (`START_ENTRY`):**
   - **Resolution of Finding 1 (Amendment A-1):** Before touching memory protections or executing attempt loops, write a preliminary record to the append-only ledger:
     `{master_seed_id, condition, quota_stratum, channel_class, execution_status: "ATTEMPTED_STARTED", timestamp}`.
   - Immediately flush via `fflush()` and force disk synchronization via `fsync()`.
5. **Step 5: Persistent Table Mutation (Conditions $C_{10}$ and $C_{11}$):**
   - Execute `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE)`.
   - Write mutated value: `vtable[target_idx] = orig_val ^ bit_mask`.
   - Perform immediate volatile readback: `ASSERT(vtable[target_idx] == target_val)`.
   - Reprotect to read-only: `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ)`.
   - Verify page protection is read-only via `vm_region_64` **prior to decapsulation**.
6. **Step 6: Protocol Transmission & Retransmission Execution:**
   - For attempt $a = 0, 1, 2$ ($\text{RETRY\_MAX} = 2$):
     - Determine channel state: Active if $a = 0$ or `channel_persistence == PERSISTENT`.
     - Derive attempt-specific PRF channel parameter seed: `prf_bytes("chan", gseed, condid, a, pseed, 16)`.
     - Construct 18-byte command frame (including inner CRC-16), derive keystream, encrypt payload, compute 32-byte outer MAC tag.
     - Apply channel fault to wire buffer:
       - `CH_BIT`: inverts bit in ciphertext bytes (`wire[pos] ^= mask`, $pos < 1088$).
       - `CH_DUP`, `CH_REORDER`: sets transport metadata; wire ciphertext bytes remain clean.
       - `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_INTERRUPT`: delivery blocks (`decaps_ran = 0`), returns appropriate transport code (`K_MALFORMED`, `K_LOST`, `K_TIMEOUT`).
     - If wire delivered: invoke SUT `mlkem768_dec(ss_dec, ct_wire, sk)` under read-only table permissions (`decaps_ran = 1`).
     - Derive canonical rejection secret: $K_{\text{rej}} = \text{SHAKE256}(z_i \parallel ct_{\text{wire}}, 32)$ using exact received wire bytes.
     - **Acceptance Evaluation (Resolution of Finding 2):**
       - Step 6a: Evaluate outer MAC tag (`mactag(ss_dec, enc, 18)`). If mismatch, return `K_MISMATCH`.
       - Step 6b: If MAC matches, decrypt payload with keystream and evaluate `parse_frame()`. If inner CRC-16 or frame fields fail, return `K_MALFORMED`.
       - Step 6c: If both MAC and frame parse pass, attempt achieves $K_{\text{EST}}$ ($Y_{\text{proto}} = 1$); break retry loop.
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
10. **Step 10: Authoritative Terminal Record Emission (`FINALIZE_ENTRY`):**
    - Write terminal record to ledger:
      `{master_seed_id, condition, quota_stratum, channel_class, execution_status: "ATTEMPTED_COMPLETED", protocol_outcome, crypto_endpoint, restoration_status: "RESTORED_AND_VERIFIED", output_ss_hex, attempts_executed}`.
    - Immediately flush via `fflush()` and force disk synchronization via `fsync()`.

### 2.3 Failure Accounting, Signal Traps, and Process Supervision
- **Resolution of Finding 1 (Amendment A-1):**
  - **Ordinary Error Paths:** If `vm_protect` fails, table write fails, or baseline check fails, execution branches to structured error logging. An explicit terminal record is written (`execution_status = PROTECT_ERROR` or `restoration_status = RESTORATION_FAILED`) and synced before the runner process exits.
  - **Hardware Trap Signals (`SIGBUS`, `SIGSEGV`):**
    - Inside `multi_fault_runner.c`, the emergency signal handler writes an immediate diagnostic message to `STDERR` using raw `write()` and calls `_exit(128 + sig)`.
    - **Process Supervisor Role:** The parent process supervisor (`runner_supervisor.py`) intercepts the child process termination. When the supervisor detects child termination with exit code $128 + sig$:
      1. It reads the ledger and finds the unclosed `START_ENTRY` record.
      2. It appends an authoritative terminal record:
         - `execution_status`: `SIGNAL_TERMINATION`
         - `protocol_outcome`: `EXECUTION_ABORT`
         - `crypto_endpoint`: `NOT_EVALUATED_PROCESS_CRASHED`
         - `restoration_status`: `UNVERIFIED_PROCESS_ABORTED`
      3. **Evidentiary Standard Enforced:** The supervisor explicitly records `UNVERIFIED_PROCESS_ABORTED`. It **never claims restoration was verified**. Although kernel process destruction discards copy-on-write anonymous pages, in-process software verification was not executed.
  - **Campaign Completion Invariant:**
    - A campaign ledger is marked complete **if and only if** exactly 1,680 finalized trial records (420 complete quadruples) exist and an explicit cryptographic end-of-campaign sentinel record is written:
      `CAMPAIGN_SUMMARY: STATUS=COMPLETE: RECORD_COUNT=1680: LEDGER_SHA256=...`
    - Any partial or aborted run is stamped:
      `CAMPAIGN_SUMMARY: STATUS=PARTIAL_ABORTED: RECORD_COUNT=k/1680`.

---

## 3. Ratified Design Requirements Traceability Matrix

| Ratified Requirement | Implementation Component | Verification Method & Implementation Gate |
| :--- | :--- | :--- |
| **Q1: 300 active twiddle $\times$ `CH_BIT`** | Manifest generator & Quota 1 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q2: 20 `CH_DUP`, 20 `CH_REORDER`** | Manifest generator & Quota 2 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q3: 15 each across 4 blocking classes** | Manifest generator & Quota 3 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **Q4: 5 per control cell ($2 \times 2$ grid)** | Manifest generator & Quota 4 filter | Gate 2 (Manifest Schema Review) & Gate 4 (Runner Review) |
| **$N = 420$ master seeds, $1,680$ trial records** | Manifest master array ($420$ objects $\to 1680$ trials) | Gate 2 (Manifest Schema Review) |
| **Matched conditions ($C_{00}, C_{10}, C_{01}, C_{11}$)** | Runner session execution loop (Steps 4–6) | Gate 4 (Runner Code Review) |
| **Table fault persists across retries** | State held across attempt loop ($a \in [0, 2]$) | Gate 4 (Runner Code Review) |
| **Channel persistence semantics** | Attempt-indexed PRF draws ($a \in [0, 2]$) | Gate 4 (Runner Code Review) |
| **Dual Framing (MAC + CRC-16)** | Framing engine (`combined_campaign.c:39-67`) | Gate 4 (Runner Code Review) |
| **Channel-stratified primary contrasts** | Post-processing script (`analyze_results.py`) | Gate 5 (Statistical Pipeline Review) |
| **Exploratory equal $1/7$ weighting** | Post-processing script (`analyze_results.py`) | Gate 5 (Statistical Pipeline Review) |
| **Write-Ahead Logging & Crash Containment** | Two-phase ledger + supervisor wrapper | Gate 4 (Runner Review) |

---

## 4. Deterministic Manifest and Retry Semantics

### 4.1 Canonical Manifest Storage Architecture (Resolution of Finding 4)
- **Top-Level Storage Model:** `manifest.json` serializes an array of exactly **420 Master Scenario Objects** `[PROPOSED / NOT YET TESTED]`.
- **Matched Condition Deterministic Expansion Invariant:** The four matched conditions are expanded deterministically by the runner from the single master scenario object:
  - Condition $C_{00}$: `table_fault = INACTIVE`, `channel_fault = INACTIVE`.
  - Condition $C_{10}$: `table_fault = ACTIVE`, `channel_fault = INACTIVE`.
  - Condition $C_{01}$: `table_fault = INACTIVE`, `channel_fault = ACTIVE`.
  - Condition $C_{11}$: `table_fault = ACTIVE`, `channel_fault = ACTIVE`.
  This structure guarantees that all four conditions evaluate the **exact same keypair, ciphertext, and memory target parameters**.

### 4.2 Canonical JSON Schema
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
    "bit_position_base": 142,
    "bit_mask_hex": "0x04",
    "truncation_bytes": 0,
    "delay_ticks": 1,
    "persistence": "TRANSIENT"
  },
  "protocol": {
    "retry_max": 2,
    "deadline_ticks": 100
  }
}
```

### 4.3 Attempt-Indexed Channel Parameter Derivation (Resolution of Finding 4)
Grounded directly in [combined_campaign.c:160-163](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L160-L163) `[DIRECTLY OBSERVED]`:
- For each transmission attempt $a \in [0, \text{RETRY\_MAX}]$:
  $$\text{ch\_active} = \text{ch\_on} \land (\text{ch\_persist} \lor a == 0)$$
- **Transient Channel Mode (`persistence == TRANSIENT`):**
  - Attempt 0 ($a=0$): Channel fault is ACTIVE. Impairment parameters derived via:
    `prf_bytes("chan", gseed, (uint64_t)condid, 0, pseed, 16)`.
  - Attempt 1 ($a=1$): Channel fault is INACTIVE (`ch_active = 0`). Frame transmitted cleanly.
  - Attempt 2 ($a=2$): Channel fault is INACTIVE (`ch_active = 0`). Frame transmitted cleanly.
- **Persistent Channel Mode (`persistence == PERSISTENT`):**
  - Attempt 0 ($a=0$): Channel fault is ACTIVE with seed from attempt 0 (`prf_bytes(..., a=0)`).
  - Attempt 1 ($a=1$): Channel fault is ACTIVE with seed from attempt 1 (`prf_bytes(..., a=1)`).
  - Attempt 2 ($a=2$): Channel fault is ACTIVE with seed from attempt 2 (`prf_bytes(..., a=2)`).
- **Persistent Memory Table Fault:** In conditions $C_{10}$ and $C_{11}$, the table mutation remains **continuously active across all attempts $a \in [0, 2]$**, regardless of channel persistence mode!

---

## 5. Vector Corpus, Dual-Layer Framing, and Independent Oracle Contract

### 5.1 On-Disk Vector Inventory vs. Runtime Generation
- **Static Official KAT (Vector 0):** Directly observed in [references/test_vectors/mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h) `[DIRECTLY OBSERVED]`.
- **Planned Local Vectors (Vectors 1–419):** Zero locally generated vectors exist on disk `[DIRECTLY OBSERVED]`. Must be derived deterministically at preflight runtime `[PROPOSED / NOT YET TESTED]`.

### 5.2 Dual-Layer Transport and Framing Specification (Resolution of Finding 2)
Grounded in `combined_campaign.c:39-67` `[DIRECTLY OBSERVED]`:
1. **Plaintext Command Frame (18 bytes):**
   - Bytes 0..3: Magic header `"SPAC"`.
   - Bytes 4..5: Big-endian sequence number `seq`.
   - Byte 6: Command code `0x01`.
   - Byte 7: Subcommand code `0x10` (`ADCS POINT_NADIR`).
   - Bytes 8..11: Big-endian integer parameter 1 (`45`).
   - Bytes 12..15: Big-endian integer parameter 2 (`60000`).
   - Bytes 16..17: Big-endian CRC-16-CCITT computed over bytes 0..15.
2. **CRC-16-CCITT Internal Error Detection:**
   - Polynomial: $x^{16} + x^{12} + x^5 + 1$ (`0x1021`), initial `0xFFFF`.
   - Purpose: Verifies plaintext integrity after decryption. **Does NOT provide cryptographic authentication.**
3. **Keystream Encryption:**
   - $ks = \text{SHAKE256}(0x01 \parallel ss, 18)$.
   - Encrypted payload: $enc[i] = frame[i] \oplus ks[i]$ for $i \in [0, 17]$.
4. **Outer Cryptographic MAC Tag (32 bytes):**
   - $Tag = \text{SHAKE256}(0x02 \parallel ss \parallel enc, 32)$ (input: 1 byte domain separator + 32 bytes shared secret + 18 bytes ciphertext payload = 51 bytes).
   - Purpose: Cryptographic authentication of payload keyed by shared secret.
5. **Receiver Acceptance Priority:**
   - Step 1: Compute receiver tag $tag_c = \text{mactag}(ss_{\text{dec}}, enc, 18)$. Compare $tag_c == tag_{\text{received}}$. If mismatch $\implies$ returns `K_MISMATCH` (`PROTOCOL_ABORT`). Frame is NOT parsed; payload discarded immediately.
   - Step 2: If MAC matches, decrypt payload with keystream.
   - Step 3: Parse frame via `parse_frame()`. If magic, sequence window, command codes, or CRC-16 fail $\implies$ returns `K_MALFORMED`.
   - Step 4: If both MAC and frame parse pass $\implies$ returns `K_EST` ($Y_{\text{proto}} = 1$).

### 5.3 Independent Rejection Oracle Mechanics
Grounded in `independent_oracle.c:59-79` and `fips202_ref.c:1-86` `[DIRECTLY OBSERVED]`:
- **Secret Key $z$ Offset:** Exactly 2368 ($sk + (2400 - 32)$), extracting the last 32 bytes of the 2,400-byte secret key.
- **Wire Ciphertext Input Invariant:** The rejection derivation MUST use the exact received wire ciphertext bytes $\tilde{c}$ (`wire[0..1087]`):
  $$K_{\text{rej}}(\tilde{c}) = \text{SHAKE256}(z_i \parallel \tilde{c}, 32)$$
- **Oracle Provenance Scope:** Designated an **architecturally independent reference implementation** (clean-code implementation based on TweetFIPS-202). Not designated a legal "clean-room" implementation due to absence of institutional firewall documentation `[INFERRED]`.
- **Golden Secret vs. Rejection Semantics:**
  - Sender expected secret: $K_{\text{golden}}$ (clean encapsulation).
  - Receiver wire decapsulation output: $ss_{\text{dec}}$.
  - Protocol agreement: $ss_{\text{dec}} == K_{\text{golden}}$.
  - Normal rejection under wire corruption: $ss_{\text{dec}} == K_{\text{rej}}(\tilde{c})$. **NEVER classified as SDC.**
  - Cryptographic SDC: $ss_{\text{dec}} \neq K_{\text{golden}} \land ss_{\text{dec}} \neq K_{\text{rej}}(\tilde{c})$.

---

## 6. Statistical Contract and Estimands

### 6.1 Matched Interaction Contrast Estimands (Resolution of Finding 3)
The matched interaction contrast is defined **strictly and exclusively for the binary Protocol Key Agreement outcome ($Y_{\text{proto}} \in \{0, 1\}$)** `[INFERRED]`:

$$\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c) = \frac{1}{n_c} \sum_{i=1}^{n_c} \left( Y_{\text{proto}, i}(C_{11}) - Y_{\text{proto}, i}(C_{10}) - Y_{\text{proto}, i}(C_{01}) + Y_{\text{proto}, i}(C_{00}) \right)$$

- **Primary Stratified Analysis:** Evaluated separately for each channel class $c \in \{\text{BIT}, \text{DUP}, \text{REORDER}, \text{TRUNC}, \text{LOSS}, \text{DELAY}, \text{INTERRUPT}\}$.
- **Exploratory Aggregate Contrast:**
  $$\hat{\Delta}_{\text{std}} = \frac{1}{7} \sum_{c=1}^7 \hat{\Delta}_c$$
  - Formally designated strictly **EXPLORATORY**; defines an artificial standardized metric with equal mechanism weighting ($1/7$), not an empirical space-link probability distribution `[INFERRED]`.
- **Stratum Sample Size Disparity:** Quota 1 ($N=300$) achieves high statistical precision; Quotas 2, 3, 4 ($n=15..20$) have wider bootstrap confidence intervals. Cross-stratum pooling is strictly prohibited `[INFERRED]`.

### 6.2 Cryptographic SDC Rate Endpoint ($Y_{\text{crypto}}$)
- Evaluated **strictly conditional on completed first-attempt decapsulations** ($n_{\text{completed}}$) under $C_{11}$ (and $C_{10}$).
- Not evaluable under blocking channel classes where decapsulation does not execute.
- Evaluated via the exact one-sided 95% Clopper–Pearson upper bound:

$$p_U(n) = 1 - (0.05)^{1/n}$$

- **$n = 300$:** $p_U(300) = \mathbf{0.993608\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 299$:** $p_U(299) = \mathbf{0.996915\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 298$:** $p_U(298) = \mathbf{1.000243\% \ge 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 0$:** Division by zero; classified as **`INCONCLUSIVE_NO_COMPLETED_TRIALS`** (no numerical bound) `[INDEPENDENTLY RECOMPUTED]`.

### 6.3 Outcome Non-Conflation and Denominators
- **Protocol Failure ($Y_{\text{proto}} = 0$):** In Intention-to-Test (ITT), process crashes and timeouts are coded as failure ($0$) because key establishment failed.
- **Cryptographic SDC ($Y_{\text{crypto}} = 1$):** Evaluated strictly among completed decapsulations ($n_{\text{completed}}$). **Process crashes are NEVER coded as SDC.**
- **Execution Reliability ($Y_{\text{exec}}$):** Hardware traps (`SIGBUS`/`SIGSEGV`), protection errors, and canary corruptions are tracked in a dedicated reliability table.
- **Denominator Funnel:**
  $N_{\text{assigned}} (420) \to N_{\text{eligible}} \to N_{\text{attempted}} \to N_{\text{completed\_sessions}} \to n_{\text{completed\_decaps}} \to N_{\text{analysable\_quads}}$.

---

## 7. Audit Traceability Matrix (Mapping Phase 18C Findings)

| Phase 18C Audit Finding | Required Remediation | Corrected Section in Phase 18D | Resolution Details |
| :--- | :--- | :--- | :--- |
| **Finding 1 (Severity: HIGH)**<br>Step 10 emission rule drops crashed trials. | Replace conditional emission with durable write-ahead logging (WAL) and supervisor wrapper. | **Section 2.2 (Step 4 & 10)**<br>**Section 2.3** | Added `START_ENTRY` with `fsync()`, supervisor wrapper intercepting exit codes, and explicit `UNVERIFIED_PROCESS_ABORTED` recording. |
| **Finding 2 (Severity: MEDIUM)**<br>Underspecified protocol authentication contract. | Formalize dual-layer framing: 32B `mactag` (crypto auth) vs. inner CRC-16 (transport integrity). | **Section 2.2 (Step 6)**<br>**Section 5.2** | Grounded framing in `combined_campaign.c:39-67`; specified SHAKE256 formulas and acceptance priority order. |
| **Finding 3 (Severity: MEDIUM)**<br>Ambiguity in scope of interaction contrast $\Delta_c$. | Explicitly restrict $\Delta_c$ to binary Protocol Key Agreement ($Y_{\text{proto}}$). | **Section 6.1**<br>**Section 6.2** | Restricted $\Delta_c$ strictly to $Y_{\text{proto}}$; separated conditional SDC Clopper–Pearson evaluation. |
| **Finding 4 (Severity: MEDIUM)**<br>Manifest schema ambiguous across retries and conditions. | Specify 420 master scenario objects in `manifest.json` and attempt-indexed PRF draws. | **Section 4.1**<br>**Section 4.3** | Defined 420 master objects with deterministic expansion; formalized attempt PRF draws ($a \in [0, 2]$). |

---

## 8. Known Limitations and Untested Claims

In strict compliance with anti-hallucination standards:
1. **Dynamic Vector Correctness (Vectors 1–419) is Untested:** The mathematical validity of Vectors 1–419 cannot be verified until Gate 3 preflight execution against `liboqs v0.16.0` `[PROPOSED / NOT YET TESTED]`.
2. **Mach-O Page Attrition Rate is Untested:** The empirical frequency of Darwin ARM64 `vm_protect` hardware traps across 1,680 consecutive transitions is unknown `[UNKNOWN / UNVERIFIED]`.
3. **Crash Recovery Logging Resilience is Untested:** While the supervisor architecture is specified, dynamic handling of actual hardware trap signals has not been executed `[PROPOSED / NOT YET TESTED]`.
4. **Differential Stratum Precision:** Secondary protocol contrast estimates for Quotas 2, 3, and 4 will have wider confidence intervals than Quota 1 due to smaller sample sizes ($n=15..20$ vs. $n=300$) `[INFERRED]`.

---

## 9. Phased Implementation Roadmap and Review Gates

```
[ Gate 1: Corrected Architecture Approval (Phase 18D - Current Document) ]
                               │
                               ▼
[ Gate 2: Manifest Generator & Canonical Schema Review (Phase 18E) ]
  - Review generate_manifest.py / manifest.json schema (420 master objects)
  - Statically verify quotas: Q1 (300), Q2 (40), Q3 (60), Q4 (20)
  - Verify canonical SHA-256 serialization and attempt PRF rules
                               │
                               ▼
[ Gate 3: Vector Preflight & Oracle Harness Review (Phase 18F) ]
  - Review validate_vectors.c linking liboqs v0.16.0
  - Review TweetFIPS-202 rejection derivation harness (wire bytes input)
  - Verify fail-closed preflight abort logic
                               │
                               ▼
[ Gate 4: Unified Runner & Supervisor Code Review (Phase 18G) ]
  - Statically inspect multi_fault_runner.c and runner_supervisor.py
  - Audit vm_protect transitions, bounds checks, padding canaries
  - Verify write-ahead logging (fsync), retry persistence, signal wrapper
                               │
                               ▼
[ Gate 5: Statistical Analysis Pipeline Review (Phase 18H) ]
  - Review analyze_multi_fault.py / bootstrap inference code
  - Verify Clopper-Pearson bound calculation ($n=298, 299, 300$)
  - Verify stratified reporting and exploratory 1/7 weighting
                               │
                               ▼
[ Gate 6: Human Operator Execution Authorization (Phase 19) ]
  - Human experimental operator reviews all audited deliverables
  - Explicit operator authorization required to compile & run
```

---

## 10. Repository State and Hash Verifications

### 10.1 Independently Computed SHA-256 Digests `[DIRECTLY OBSERVED]`
Computed via `shasum -a 256` on actual on-disk file bytes:

| File Path | SHA-256 Digest | Status / Role |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md` | *(Computed upon file write)* | **Phase 18D Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CHANGELOG.md` | *(Computed upon file write)* | **Phase 18D Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | `77dfabfe672e42de281e6299c8c692006e3fa3e707d5f2ec31cf902851aa6561` | Historical Audit Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | `2947278c38c14347ed24e199aada4ec00ebfe80377ede55efe81881571dfe782` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Superseded Document `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md` | `818d5cbf89f9582d2659c95ed12c450e6f54d5419dff13d3172f47fdbda1ab56` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md` | `faf155420c3dad1fe0085729943e2b899289165f8f38f3becb9b244a03b92340` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Architectural Reference `[DIRECTLY OBSERVED]` |

### 10.2 Git Repository Working Tree `[DIRECTLY OBSERVED]`
- Active Branch: `space-resilience-framework`.
- Preserved all 10 uncommitted tracked files in the working tree.
- Zero files staged, committed, pushed, or reverted.

---

## 11. Final Status and Authorization Boundary

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Explicit Governance Boundary:
Phase 18D delivers the comprehensive, corrected implementation proposal and architecture specification, fully addressing all Phase 18C audit findings.

**This document does NOT authorize compiling binaries, linking test harnesses, mutating virtual memory, generating vector corpora, or executing experimental trials.** Those actions are deferred to subsequent review gates and require separate, explicit human operator authorization.
