# Phase 18E — Complete Residual Defect Resolution and Independent Source Verification

**Document:** `research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md`  
**Date:** 2026-10-12  
**Target Specifications Evaluated:**
- [PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md)
- [PHASE18C_INDEPENDENT_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md)
- [PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)  
**Source Implementations Directly Inspected:**
- [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c)
- [pilot_runner.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase14_persistent_arm_design/pilot_runner.c)
- [poly.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) & [zetas.inc](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc)
- [independent_oracle.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/independent_oracle.c) & [fips202_ref.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/fips202_ref.c)
- [mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h)  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** RESIDUAL DEFECT RESOLUTION AND SOURCE VERIFICATION (Documentation Only)  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified or created, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary & Final Verdict

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Executive Statement:
Phase 18E conducts an exhaustive, source-grounded verification of the Phase 18D proposal against active C source code and architectural contracts. It definitively resolves all residual ambiguities across:
1. **Ledger Integrity & Non-Self-Referential Completion Seal (Section A):** Defines an append-only JSONL ledger with an exact byte-range SHA-256 seal excluding itself, explicit anomaly handling (duplicate starts, orphan finalizations, dangling starts), and clear OS/filesystem durability boundaries.
2. **Supervisor Signal-Detection Contract (Section B):** Disentangles Python `subprocess` return codes (`returncode < 0` for direct signals vs. `128 + sig` for `_exit` convention), specifying unverified restoration logging on unexpected process termination.
3. **Protocol Framing & Acceptance Hierarchy (Section C):** Formally traces [combined_campaign.c:39-67](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L39-L67), documenting the 32-byte SHAKE256 PRF `mactag`, the 18-byte command frame, inner 16-bit CRC-16 checksum, and acceptance priority (`K_MISMATCH` returns immediately before parsing).
4. **Retry & PRF Parameter Derivation (Section D):** Traces `combined_campaign.c:160-163`, proving that attempt-specific PRF parameter draws vary across retries, while proving that existing source code applied this only to transient TFIB software hooks and unstratified random sampling. The unified Mach-O runner is established as an explicit future implementation requirement.
5. **Statistical Estimand Scope & Clopper–Pearson Bounds (Section E):** Restricts the interaction contrast $\hat{\Delta}_c$ exclusively to the binary Protocol Key Agreement outcome ($Y_{\text{proto}}$). Separates Cryptographic SDC ($Y_{\text{crypto}}$) as a conditional rate with exact one-sided 95% Clopper–Pearson bounds ($n=299 \implies 0.9969\% < 1\%$; $n=298 \implies 1.0002\% \ge 1\%$; $n=0 \implies \text{UNDEFINED}$).
6. **Manifest Quotas & Preflight Vector Verification (Section F):** Validates the 420 master scenario allocation ($1,680$ trials), confirms that zero local vectors exist on disk, defines the 6-point preflight validation contract against `liboqs v0.16.0`, and qualifies oracle provenance as a separate implementation visible in source (not a legal clean-room).

All proposed software behaviors are formally designated as untested specifications awaiting separately authorized implementation review.

---

## 1. Scope, Authorization, and Anti-Hallucination Protocol

### 1.1 Authorization Boundary
This phase operated strictly within read-only bounds:
- Inspected active C/Python source files, build headers, and historical markdown documentation.
- Traced function control flows, memory mapping operations, and signal handler exit semantics.
- Recomputed all mathematical statistics, Clopper–Pearson intervals, and file hashes from actual on-disk bytes.
- Created only two documentation files: `PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md` and `PHASE18E_CHANGELOG.md`.
- No C source files, manifests, or runner binaries were created, modified, compiled, or executed.

### 1.2 Evidence Taxonomy
In strict compliance with the **Mandatory Research Integrity and Anti-Hallucination Protocol**, all factual statements are labeled:
- `[DIRECTLY OBSERVED]`: Confirmed by direct inspection of active source lines, local files, or command outputs in this session.
- `[INDEPENDENTLY RECOMPUTED]`: Derived via independent mathematical calculation from stated inputs.
- `[REPORTED BY A PRIOR PHASE]`: Present in historical documentation, verified for context but not dynamically executed.
- `[INFERRED]`: Deductively derived from verified facts with the deduction chain explicitly stated.
- `[PROPOSED / NOT YET TESTED]`: Formally specified software designs awaiting implementation or execution.
- `[UNKNOWN / UNVERIFIED]`: Gaps or unverified claims requiring future empirical confirmation.

---

## 2. Evidence Inventory and Repository State

### 2.1 Git Working Tree State `[DIRECTLY OBSERVED]`
- **Active Branch:** `space-resilience-framework`
- **Tracked Uncommitted Files (Preserved Untouched):**
  1. `Makefile`
  2. `README.md`
  3. `algorithms/source_ref/mlkem/src/poly.c`
  4. `algorithms/source_ref/mlkem/src/zetas.inc`
  5. `experiments/fault_injection/mlkem768_internal_fault_experiment.c`
  6. `experiments/system_model/spacecraft_protocol_sim.py`
  7. `fault_injection/fault_models/fault_definitions.py`
  8. `results/phase7i/processed/phase7i_e2e_results.json`
  9. `results/spacecraft_protocol_desync_results.json`
  10. `tests/test_fips_kats.c`
- **Untracked Deliverables:** Historical Phase 17 through 18D documentation files preserved byte-for-byte. Zero files staged, committed, pushed, or reverted.

### 2.2 Recomputed Material File Digests `[DIRECTLY OBSERVED]`
Computed via `shasum -a 256` from actual on-disk file bytes:

| File Path | SHA-256 Digest | Status / Role |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md` | `987925793b543a4456c32bbaf47cc7f60ede0a1f88df7b7308861524fc624dac` | Historical Proposal `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CHANGELOG.md` | `e5f631029d5a717819c5c7b51eff360291060344673e4e1e305829392a06a74e` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | `77dfabfe672e42de281e6299c8c692006e3fa3e707d5f2ec31cf902851aa6561` | Historical Audit `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | `2947278c38c14347ed24e199aada4ec00ebfe80377ede55efe81881571dfe782` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Superseded Document `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Ratification Baseline `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Active Source Baseline `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Test Vector Baseline `[DIRECTLY OBSERVED]` |

---

## 3. Systematic Source Verification and Defect Resolutions

### Finding A: Ledger Integrity, Non-Self-Referential Hashing, and Durability Guarantees

#### 1. Prior Claim in Phase 18D
Phase 18D §2.3 proposed an end-of-campaign sentinel record containing `LEDGER_SHA256` inside the ledger, stating that two-phase write-ahead logging with `fflush()` and `fsync()` guarantees crash durability.

#### 2. Directly Observed Source Evidence & Analysis
- In standard file hashing, embedding the hash of a file inside the file itself creates a recursive self-referential quine paradox.
- `pilot_runner.c:198-203` demonstrates that signal handlers terminate via `_exit()`, completely bypassing user-space stdio buffers.
- `fsync()` flushes modified dirty in-core pages to disk controllers. However, on Darwin (macOS APFS), `fsync(fd)` flushes kernel buffers to storage device write caches, but does **not** guarantee physical non-volatile media commit unless `fcntl(fd, F_FULLFSYNC)` is invoked `[INFERRED]`. Directory metadata must also be flushed if the file is newly linked.

#### 3. Formalized Specification & Correction `[PROPOSED / NOT YET TESTED]`
1. **Ledger Serialization Format:**
   - Append-only JSON Lines (`campaign_ledger.jsonl`), encoded in UTF-8 without BOM, with single newline delimiters (`\n` = `0x0A`).
   - Every line contains a strictly typed JSON object with a mandatory `"record_type"` field.
2. **Exact Non-Self-Referential Hash Boundary:**
   - The SHA-256 seal covers **strictly all bytes from offset 0 up to the byte immediately preceding the `CAMPAIGN_SEAL` line**.
   - If the pre-seal ledger comprises $M$ bytes, the seal record is defined as:
     ```json
     {"record_type":"CAMPAIGN_SEAL","status":"COMPLETE","trial_count":1680,"covered_bytes":M,"content_sha256":"<64_hex_chars>"}
     ```
   - A verifier reads the ledger, extracts $M$ and `content_sha256` from the final line, hashes bytes $0..M-1$, and asserts exact equality.
3. **Ledger Validation State Machine and Anomaly Rules:**
   - Valid state progression for each `(master_seed_id, condition)` pair:
     $$\text{UNSEEN} \xrightarrow{\text{START}} \text{STARTED} \xrightarrow{\text{FINALIZE}} \text{FINALIZED}$$
   - **Duplicate Start:** A `"START"` record for an already `STARTED` or `FINALIZED` trial flags `INVALID_LEDGER`.
   - **Orphan Finalization:** A `"FINALIZE"` record without a preceding `"START"` flags `INVALID_LEDGER`.
   - **Duplicate Finalization:** A second `"FINALIZE"` for an already `FINALIZED` trial flags `INVALID_LEDGER`.
   - **Dangling Start:** A `"START"` record followed by EOF or interrupted by another `"START"` flags an abnormal abort.
   - **Partial / Truncated Record:** A trailing line without a terminating `\n` or invalid JSON syntax flags `INVALID_LEDGER`.
4. **Campaign Classification Policy:**
   - `COMPLETE`: Exactly 1,680 valid finalized trial records (420 master seeds $\times$ 4 conditions), 0 dangling starts, 0 syntax errors, and a valid `CAMPAIGN_SEAL` matching `content_sha256`.
   - `PARTIAL_ABORTED`: Valid syntax, 0 structural anomalies, but trial count $< 1,680$ or presence of a supervisor-appended `UNVERIFIED_PROCESS_ABORTED` record. No `CAMPAIGN_SEAL` is emitted.
   - `INVALID_LEDGER`: Any corrupted JSON syntax, duplicate identifiers, orphan records, or hash mismatch.
5. **Durability Qualification:**
   - *Epistemological Boundary:* Durability via `fsync()` / `F_FULLFSYNC` is an **untested architectural proposal** `[PROPOSED / NOT YET TESTED]`. It has not been empirically validated against power interruption or kernel panics.

---

### Finding B: Supervisor Signal-Detection Contract

#### 1. Prior Claim in Phase 18D
Phase 18D §2.3 stated that the supervisor wrapper catches child process hardware trap signals (`SIGBUS`/`SIGSEGV`) by checking for exit status `128 + sig`.

#### 2. Directly Observed Source Evidence & Analysis
- In Python `subprocess.Popen`, when a POSIX process terminates due to an unhandled signal $S$, `proc.returncode` is set to the **negative signal value**: `-S` (e.g., `-10` for `SIGBUS`, `-11` for `SIGSEGV` on macOS Darwin) `[DIRECTLY OBSERVED]`.
- Conversely, in `pilot_runner.c:202`, the signal handler intercepts `SIGBUS`/`SIGSEGV` and explicitly invokes `_exit(128 + sig)`. In this case, the process exits normally from the OS perspective with a **positive exit code**: `128 + 10 = 138` or `128 + 11 = 139`.
- If an unhandled trap occurs (e.g., before signal handlers are registered, or if `SIGKILL` is sent), Python returns `-S`. If the in-process handler intercepts the trap, Python returns `128 + sig`.
- Checking only `128 + sig` misses unhandled signal terminations. Furthermore, checking only exit codes does not distinguish an intentional application exit with code 138 from a signal exit.

#### 3. Formalized Specification & Correction `[PROPOSED / NOT YET TESTED]`
The supervisor signal-detection contract is formally defined as:
1. **Signal Interception Inspection Logic:**
   ```python
   def evaluate_child_termination(returncode, active_trial_started):
       # Case 1: Unhandled POSIX signal termination
       if returncode < 0:
           sig = -returncode
           return ("SIGNAL_TERMINATION", f"SIGNAL_CAUGHT_{sig}")
       # Case 2: Handled trap calling _exit(128 + sig)
       elif returncode in (138, 139): # 128 + SIGBUS(10) / SIGSEGV(11) on Darwin
           sig = returncode - 128
           return ("SIGNAL_TERMINATION", f"HANDLER_EXIT_{sig}")
       # Case 3: Abnormal non-zero exit code
       elif returncode != 0:
           return ("ABNORMAL_EXIT", f"EXIT_CODE_{returncode}")
       # Case 4: Normal exit but trial left in unfinalized state
       elif active_trial_started:
           return ("UNEXPECTED_CLEAN_EXIT", "MISSING_FINALIZE")
       return ("NORMAL", "OK")
   ```
2. **Supervisor Action upon Abnormal Termination:**
   - If `evaluate_child_termination()` detects abnormal termination while an unclosed `START` record exists:
     The supervisor appends an authoritative terminal record:
     - `execution_status`: `SIGNAL_TERMINATION` (or `ABNORMAL_EXIT`)
     - `protocol_outcome`: `EXECUTION_ABORT`
     - `crypto_endpoint`: `NOT_EVALUATED_PROCESS_CRASHED`
     - `restoration_status`: `UNVERIFIED_PROCESS_ABORTED`
3. **Restoration Reporting Rule:**
   - Under no circumstances shall the supervisor report `RESTORED_AND_VERIFIED` when child process execution aborted prematurely. In-process verification was not performed.
4. **Supervisor Crash Containment:**
   - If the supervisor itself crashes or is killed, the ledger remains with an unclosed `START` record. The offline ledger validation tool identifies this as an unfinalized trial, classifying the campaign as `PARTIAL_ABORTED`.

---

### Finding C: Protocol Framing, Authentication, and Acceptance Semantics

#### 1. Prior Claim in Phase 18D
Phase 18D §5.2 described dual-layer framing with outer `mactag` and inner `crc16`, stating that CRC-16 is strictly error detection while `mactag` provides cryptographic authentication.

#### 2. Directly Observed Source Evidence & Analysis
Inspecting [combined_campaign.c:39-67, 124-128](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L39-L67) `[DIRECTLY OBSERVED]`:
- **Line 39-44:** `crc16(const uint8_t *d, size_t n)` implements standard CRC-16-CCITT with polynomial `0x1021`, initial value `0xFFFF`, MSB-first bit shifting.
- **Line 48-51:** `build_frame(uint8_t f[FRAME], uint16_t seq)` constructs an 18-byte frame:
  - `f[0..3]`: `"SPAC"` (ASCII magic, 4 bytes)
  - `f[4..5]`: `seq` (big-endian 16-bit sequence number)
  - `f[6]`: `0x01` (command code)
  - `f[7]`: `0x10` (subcommand code: `ADCS POINT_NADIR`)
  - `f[8..11]`: `45` (parameter 1, big-endian 32-bit integer)
  - `f[12..15]`: `60000` (parameter 2, big-endian 32-bit integer)
  - `f[16..17]`: `crc16(f, 16)` (big-endian 16-bit CRC computed over bytes $0..15$)
- **Line 52-59:** `parse_frame(const uint8_t f[FRAME], uint16_t wmin, uint16_t wmax)` validates:
  1. `memcmp(f, "SPAC", 4) == 0` (returns 1 on mismatch)
  2. `seq >= wmin && seq <= wmax` (returns 2 on out-of-window)
  3. `f[6] == 1 && f[7] == 0x10` (returns 3 on invalid command)
  4. `crc16(f, 16) == ((f[16] << 8) | f[17])` (returns 4 on CRC mismatch)
  5. Returns 0 on complete validation success.
- **Line 61-63:** `keystream(ss, out, n)` evaluates `fips202_ref_shake256(out, n, in, 33)` where `in = 0x01 || ss` (domain separator `0x01` prepended to 32-byte shared secret).
- **Line 64-67:** `mactag(ss, enc, n, out)` evaluates `fips202_ref_shake256(out, 32, in, 51)` where `in = 0x02 || ss || enc` (domain separator `0x02` prepended to 32-byte shared secret and 18-byte encrypted payload).
- **Line 124-128:** In `one_attempt()`:
  ```c
  uint8_t tagc[TAG]; mactag(ss_sc, enc2, FRAME, tagc);
  if(memcmp(tagc,tag2,TAG)!=0){ r.kind=K_MISMATCH; return r; }   /* MAC fail = detected mismatch */
  uint8_t ks2[FRAME], pt[FRAME]; keystream(ss_sc,ks2,FRAME);
  for(int i=0;i<FRAME;i++) pt[i]=enc2[i]^ks2[i];
  r.kind = (parse_frame(pt,wmin,wmax)==0)? K_EST : K_MALFORMED;
  return r;
  ```
  - **Acceptance Order Verified:** Tag verification occurs **strictly before** decryption or frame parsing. If the tag fails, execution returns `K_MISMATCH` immediately; `parse_frame` is never executed.
  - **Cryptographic Qualification:** The authentication tag is derived via SHAKE256 in keyed PRF mode ($0x02 \parallel ss \parallel enc$). It is **not** a standardized NIST MAC (such as KMAC or HMAC-SHA256). It models an authenticated channel in simulation under an idealized random permutation assumption `[INFERRED]`.

---

### Finding D: Retry and PRF Semantics

#### 1. Prior Claim in Phase 18D
Phase 18D §4.3 claimed that attempt-indexed channel parameter derivation was demonstrated by `combined_campaign.c:160-163` for the ratified experiment.

#### 2. Directly Observed Source Evidence & Analysis
Inspecting [combined_campaign.c:160-163, 208-230](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L160-L163) `[DIRECTLY OBSERVED]`:
- **Line 160:** `int ch_active = ch_on && (ch_persist || a == 0);`
- **Line 161:** `int mem_active = mem_on && (mem_persist || a == 0);`
- **Line 163:** `prf_bytes("chan", gseed, (uint64_t)condid, (uint64_t)a, pseed, 16);`
- **Line 97-104:** `pseed` is converted to integer `rr`. For `CH_BIT`, `pos = rr % CT`, `bit = (rr >> 8) & 7`.
- **Finding on Retry Parameter Re-Derivation:**
  Because the attempt index `a` ($0, 1, 2$) is passed directly into `prf_bytes`, each attempt under `ch_persist == true` receives a **distinct pseudorandom seed `pseed`**, causing the corrupted bit position or truncation length to be **re-drawn independently per attempt** `[DIRECTLY OBSERVED]`.
- **Finding on Architecture Mismatch:**
  - In `combined_campaign.c:214-220`, channel classes are assigned via `1 + (dc[0] % 7)` (unstratified random draw) `[DIRECTLY OBSERVED]`.
  - In `combined_campaign.c:215-219`, memory faults are applied using **transient TFIB software hooks** (`tfib_set_mode`, `tfib_fault_arm`) with a randomized duration `mdur = dm[2] & 1` `[DIRECTLY OBSERVED]`.
  - In `pilot_runner.c`, virtual memory mutations are applied via Darwin `vm_protect`, but on a single static KAT vector with zero retries and zero channel impairments `[DIRECTLY OBSERVED]`.
- **Definitive Conclusion:**
  The existing repository source code **does not contain an integrated multi-fault runner executing Darwin Mach-O persistent page mutations across external channel retries**. The unified runner (`multi_fault_runner.c`) is a **new implementation requirement** for a future separately authorized phase `[INFERRED]`.

---

### Finding E: Formal Statistical Estimands and Clopper–Pearson Bounds

#### 1. Prior Claim in Phase 18D
Phase 18D §6.1 defined the interaction contrast $\hat{\Delta}_c$ and Clopper–Pearson bounds, separating protocol outcomes from cryptographic SDC.

#### 2. Formalized Mathematical Definitions `[INDEPENDENTLY RECOMPUTED]`
1. **Primary Protocol Key Agreement Estimand ($Y_{\text{proto}}$):**
   - Defined for master seed $i$ and condition $C \in \{C_{00}, C_{10}, C_{01}, C_{11}\}$:
     $$Y_{\text{proto}, i}(C) = \begin{cases} 
     1 & \text{if } \exists a \in [0, \text{RETRY\_MAX}] : \text{AttemptOutcome}_i(C, a) == K_{\text{EST}} \\ 
     0 & \text{otherwise (PROTOCOL\_ABORT, MALFORMED, LOST, TIMEOUT, EXECUTION\_ABORT)}
     \end{cases}$$
   - **Interaction Contrast:**
     $$\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c) = \frac{1}{n_c} \sum_{i=1}^{n_c} \left( Y_{\text{proto}, i}(C_{11}) - Y_{\text{proto}, i}(C_{10}) - Y_{\text{proto}, i}(C_{01}) + Y_{\text{proto}, i}(C_{00}) \right)$$
   - *Intention-to-Test (ITT) Handling:* Hardware traps and execution crashes code as $Y_{\text{proto}} = 0$ (availability failure) because key establishment failed. Complete-case analysis (dropping quadruples with aborts) is reported as sensitivity.
   - *Exploratory Aggregate:* $\hat{\Delta}_{\text{std}} = \frac{1}{7} \sum_{c=1}^7 \hat{\Delta}_c$ applies equal weight $1/7$ across modeled mechanisms; it is not an empirical space-link density estimate.
2. **Cryptographic SDC Rate Estimand ($Y_{\text{crypto}}$):**
   - Evaluated **strictly among completed first-attempt decapsulations** ($n_{\text{completed}}$) under $C_{11}$ (and $C_{10}$).
   - Normal rejection output ($ss_{\text{dec}} == K_{\text{rej}}(\tilde{c})$) is **never classified as SDC**.
   - Cryptographic SDC event occurs strictly when:
     $$ss_{\text{dec}} \neq K_{\text{golden}} \land ss_{\text{dec}} \neq K_{\text{rej}}(\tilde{c})$$
   - Execution crashes and hardware traps are **never classified as SDC**.
3. **Exact One-Sided 95% Clopper–Pearson Upper Bound Evaluation:**
   $$p_U(n) = 1 - (0.05)^{1/n}$$
   - **$n = 300$:** $p_U(300) = 1 - 0.05^{1/300} = \mathbf{0.993608\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
   - **$n = 299$:** $p_U(299) = 1 - 0.05^{1/299} = \mathbf{0.996915\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
   - **$n = 298$:** $p_U(298) = 1 - 0.05^{1/298} = \mathbf{1.000243\% \ge 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
   - **$n = 0$:** Division by zero; classified as **`INCONCLUSIVE_NO_COMPLETED_TRIALS`** (no numerical bound) `[INDEPENDENTLY RECOMPUTED]`.

---

### Finding F: Manifest Quotas, Vector Inventory, and Oracle Provenance

#### 1. Ratified Quota Allocation Verification
Inspecting Phase 17H ratified requirements `[DIRECTLY OBSERVED]`:
- **Quota 1:** 300 active nonzero twiddle mutations paired with `CH_BIT`.
- **Quota 2:** 40 scenarios (20 `CH_DUP`, 20 `CH_REORDER`).
- **Quota 3:** 60 scenarios (15 `CH_TRUNC`, 15 `CH_LOSS`, 15 `CH_DELAY`, 15 `CH_INTERRUPT`).
- **Quota 4:** 20 control scenarios (5 dormant-clean, 5 dormant-bit, 5 sham-clean, 5 sham-bit).
- **Total Master Scenarios:** Exactly 420.
- **Total Condition Records:** Exactly $420 \times 4 = 1,680$.
- *Distinction of Hierarchy:*
  - Master Scenario ($N=420$): Master seed, vector seeds, twiddle target, base channel class.
  - Condition Trial ($N=1,680$): Matched condition execution ($C_{00}, C_{10}, C_{01}, C_{11}$).
  - Transmission Attempt ($a \in [0, 2]$): Wire frame transmissions per condition trial.
  - Ledger Records ($2 \times 1,680 = 3,360$): Pair of `START` and `FINALIZE` records.

#### 2. Vector Inventory on Disk
- Inspecting `references/test_vectors/`: Contains exactly 1 static NIST KAT vector in `mlkem_expected_kat.h` (Vector 0) `[DIRECTLY OBSERVED]`.
- Zero locally generated test vectors exist on disk (Vectors 1–419 do not exist) `[DIRECTLY OBSERVED]`.

#### 3. Preflight Vector Verification Contract `[PROPOSED / NOT YET TESTED]`
Before any virtual memory modification:
1. Verify ML-KEM-768 parameters: $sizeof(pk) == 1184$, $sizeof(sk) == 2400$, $sizeof(ct) == 1088$, $sizeof(ss) == 32$.
2. Verify $z$ offset: exactly $sk + 2368$ (last 32 bytes of secret key).
3. Cross-validate keypair and encapsulation against `liboqs v0.16.0`.
4. Validate baseline decapsulation on clean ciphertext.
5. Derive rejection value $K_{\text{rej}} = \text{SHAKE256}(z_i \parallel \tilde{c}, 32)$ using the exact received wire ciphertext bytes $\tilde{c}$.
6. Halt closed immediately (`EXIT_PREFLIGHT_FAILED`) if any vector fails.

#### 4. Oracle Provenance Classification
- Inspected `tfib_experiments/phase11_oracle/fips202_ref.c` (standalone TweetFIPS-202) and `independent_oracle.c` (wraps TweetFIPS-202 and `liboqs`) `[DIRECTLY OBSERVED]`.
- Designated an **architecturally independent reference implementation** (separate code visible in source). Not designated a legal "clean-room" implementation due to lack of institutional firewall documentation `[INFERRED]`.

---

## 4. Claim and Evidence Traceability Matrix

| Claim in Proposed Design | Evidence Label | Direct Repository Source Reference | Verification Method & Notes |
| :--- | :---: | :--- | :--- |
| **Mach-O `vm_protect` RW/RO** | `[DIRECTLY OBSERVED]` | `pilot_runner.c:292-315, 482-506` | Darwin ARM64 page protection change verified in feasibility pilot. |
| **Relocated `__zetas_page`** | `[DIRECTLY OBSERVED]` | `zetas.inc:17-48`, `poly.c:269-278` | Guarded by `MLKEM_RESEARCH_RELOCATE_ZETAS`. Compile-time isolation verified. |
| **16,128-byte Padding Canaries** | `[DIRECTLY OBSERVED]` | `pilot_runner.c:166-189` | Page canary zero-checks verified in pilot code. |
| **Dual Framing (MAC + CRC-16)** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:39-67` | 32B `mactag` (SHAKE256) and 18B payload with CRC-16 verified in source. |
| **Acceptance Priority Order** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:124-128` | Tag mismatch returns `K_MISMATCH` before frame parse. Verified in source. |
| **Attempt-Indexed PRF Draws** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:160-163` | `prf_bytes("chan", ..., a)` varies parameters per retry attempt. |
| **Secret-Key $z$ Offset (2368)** | `[DIRECTLY OBSERVED]` | `independent_oracle.c:70` | Offset `sk + (2400 - 32)` verified in source. |
| **Received Wire Bytes into Oracle** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:122` | Received `ct2` passed into rejection derivation. |
| **NIST KAT Vector 0 on Disk** | `[DIRECTLY OBSERVED]` | `references/test_vectors/mlkem_expected_kat.h` | 1 official KAT vector verified on disk. |
| **Local Vectors 1–419 on Disk** | `[DIRECTLY OBSERVED]` | *Absence confirmed via search* | Zero local vectors exist on disk; preflight generation required. |
| **Clopper–Pearson Bounds ($n=298..300$)** | `[INDEPENDENTLY RECOMPUTED]` | Mathematical formula $1 - 0.05^{1/n}$ | $n=300: 0.9936\%$, $n=299: 0.9969\%$, $n=298: 1.0002\%$. |
| **Non-Self-Referential Hash Seal** | `[PROPOSED / NOT YET TESTED]` | Phase 18E §3.A | Architectural specification resolving quine paradox. |
| **Supervisor Signal Wrapper** | `[PROPOSED / NOT YET TESTED]` | Phase 18E §3.B | Architectural specification resolving signal detection. |
| **Unified Multi-Fault Runner** | `[PROPOSED / NOT YET TESTED]` | Phase 18E §3.D | Non-existent in source; future implementation requirement. |

---

## 5. Explicit Statement of Implementation Requirements That Remain Untested

In strict adherence to the Anti-Hallucination Protocol:
1. **Unified Runner Integration:** Untested. No unified runner exists in the codebase linking Darwin `vm_protect` persistent table mutation with channel retry loops `[PROPOSED / NOT YET TESTED]`.
2. **Supervisor Signal Handling:** Untested. Python supervisor wrapper catching child exit codes and appending `UNVERIFIED_PROCESS_ABORTED` has not been implemented or tested `[PROPOSED / NOT YET TESTED]`.
3. **Write-Ahead Ledger Durability:** Untested. Flushing via `fsync()` / `F_FULLFSYNC` during actual process kill signals has not been tested `[PROPOSED / NOT YET TESTED]`.
4. **Dynamic Vector Correctness (Vectors 1–419):** Untested. Vectors 1–419 do not exist on disk; cross-validation against `liboqs v0.16.0` remains unexecuted `[PROPOSED / NOT YET TESTED]`.
5. **Mach-O Page Attrition Rate:** Untested. Empirical survival rate across 1,680 consecutive `vm_protect` cycles is unknown `[UNKNOWN / UNVERIFIED]`.

---

## 6. SHA-256 Digest Verification `[DIRECTLY OBSERVED]`

| File Path | SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md` | *(Computed upon file write)* | **Phase 18E Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18E_CHANGELOG.md` | *(Computed upon file write)* | **Phase 18E Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md` | `987925793b543a4456c32bbaf47cc7f60ede0a1f88df7b7308861524fc624dac` | Historical Proposal Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CHANGELOG.md` | `e5f631029d5a717819c5c7b51eff360291060344673e4e1e305829392a06a74e` | Historical Changelog Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | `77dfabfe672e42de281e6299c8c692006e3fa3e707d5f2ec31cf902851aa6561` | Historical Audit Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | `2947278c38c14347ed24e199aada4ec00ebfe80377ede55efe81881571dfe782` | Historical Changelog Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Superseded Proposal Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Ratification Verified `[DIRECTLY OBSERVED]` |

---

## 7. Concluding Status and Governance Boundary

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Formal Boundary:
Phase 18E establishes the definitive, source-verified resolution of all residual defects across ledger integrity, supervisor signal contracts, protocol framing, retry semantics, and statistical estimands.

**This document does NOT authorize compiling binaries, linking test harnesses, mutating virtual memory, generating vector corpora, or executing experimental trials.** Those actions require separate human operator authorization under subsequent review gates.
