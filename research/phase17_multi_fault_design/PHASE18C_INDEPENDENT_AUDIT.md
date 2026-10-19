# Phase 18C — Independent Audit of the Phase 18B Implementation Proposal

**Document:** `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md`  
**Date:** 2026-10-12  
**Target Specification:** [PHASE18B_IMPLEMENTATION_PROPOSAL.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md)  
**Historical Ratification Reference:** [PHASE17H_OPERATOR_RATIFICATION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md)  
**Readiness Audit Reference:** [PHASE18A_READINESS_AUDIT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md)  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Execution Guard:** Strictly read-only audit. No source code or build configuration modified; no binaries compiled or linked; no virtual memory mutated; no trials executed; no git commits, pushes, or resets performed. All pre-existing working-tree changes preserved.

---

## Executive Verdict & Final Status

# Executive Verdict: **CONDITIONAL**
# Concluding Status: **CONDITIONAL — AMENDMENTS REQUIRED**

### Executive Statement:
This independent audit evaluated the formal implementation proposal ([PHASE18B_IMPLEMENTATION_PROPOSAL.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md)) against the actual repository source code and the ratified Phase 17H experiment design.

The proposal demonstrates strong conceptual grounding, correctly formalizing the 6-point preflight vector contract, the compile-time isolated storage boundary (`MLKEM_RESEARCH_RELOCATE_ZETAS`), and the Clopper–Pearson mathematical thresholds. However, four material defects were identified:
1. **Flawed Ledger Record Emission Rule (High Severity):** Step 10 specifies emitting ledger records only after Steps 1–9 succeed. If a trial encounters an unhandled error, protection failure, or hardware trap signal (`SIGBUS`/`SIGSEGV`), execution terminates via `_exit()`, and the trial record is never written to the ledger, violating complete-case accounting across all 1,680 trials.
2. **Underspecified Protocol Authentication & Acceptance Semantics (Medium Severity):** The proposal mentions "CRC-16 framing" and "MAC verifies" without explicitly documenting the actual dual-layer cryptographic construction observed in [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c) (`mactag` via SHAKE256 vs. inner `crc16` check).
3. **Ambiguity in Scope of Interaction Contrast $\Delta_c$ (Medium Severity):** Section 6.1 defines $\Delta_c = p_{11}(c) - p_{10}(c) - p_{01}(c) + p_{00}(c)$ without explicitly stating that this estimand applies strictly to the Protocol Key Agreement endpoint ($Y_{\text{proto}}$) and is mathematically invalid for Cryptographic SDC ($Y_{\text{crypto}}$).
4. **Manifest Schema Ambiguity Across Retries and Conditions (Medium Severity):** The JSON schema provides a single master scenario object with static channel parameters, but omits how retry parameters ($a \in [1, 2]$) are derived under persistent channels and whether the manifest file is an array of 420 master objects or 1,680 trial records.

Because these issues must be resolved before proceeding to code review or harness construction, Phase 18B is rated **CONDITIONAL — AMENDMENTS REQUIRED**.

---

## 1. Scope, Authorization, and Anti-Hallucination Protocol

### 1.1 Authorization Boundary
This audit operated under strict read-only constraints:
- Inspected active source files, build scripts, headers, and historical markdown documentation.
- Executed read-only pattern searches and file hash calculations.
- Independently recomputed statistical bounds and mathematical derivations.
- Created only two documentation files: `PHASE18C_INDEPENDENT_AUDIT.md` and `PHASE18C_CHANGELOG.md`.
- Did not edit existing source files, compile or link binaries, mutate virtual memory, generate or validate vectors, or alter Git state.

### 1.2 Mandatory Evidence Taxonomy
In strict accordance with the **Mandatory Research Integrity and Anti-Hallucination Protocol**, every factual statement in this document is labeled with its evidentiary basis:
- `[DIRECTLY OBSERVED]`: Confirmed by direct inspection of active source lines, local files, or command outputs in this session.
- `[INDEPENDENTLY RECOMPUTED]`: Derived via independent mathematical or computational calculation from stated inputs.
- `[REPORTED BY A PRIOR PHASE]`: Documented in historical project artifacts, verified for context but not dynamically executed.
- `[INFERRED]`: Deductively derived from verified facts with the deduction chain explicitly stated.
- `[PROPOSED / NOT YET TESTED]`: Proposed design parameters or software contracts awaiting implementation or dynamic execution.
- `[UNKNOWN / UNVERIFIED]`: Gaps, missing data, or unverified claims requiring human operator clarification or future testing.

---

## 2. Evidence Inventory and Repository State

### 2.1 Git Repository Working Tree `[DIRECTLY OBSERVED]`
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
- **Staging / Commit State:** Zero files staged, committed, pushed, or discarded.

### 2.2 Recomputed Material File Digests `[DIRECTLY OBSERVED]`
Computed via `shasum -a 256` from actual on-disk file bytes:

| File Path | SHA-256 Digest | Role / Status |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Audit Target `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md` | `818d5cbf89f9582d2659c95ed12c450e6f54d5419dff13d3172f47fdbda1ab56` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18A_READINESS_AUDIT.md` | `faf155420c3dad1fe0085729943e2b899289165f8f38f3becb9b244a03b92340` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architectural Source `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architectural Source `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architectural Source `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architectural Source `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architectural Source `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architectural Source `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Test Vector Baseline `[DIRECTLY OBSERVED]` |

---

## 3. Detailed Audit Findings Ranked by Severity

### Finding 1: Flawed Ledger Record Emission Rule and Crash Attrition Loss
- **Severity:** **HIGH**
- **Affected Section in Phase 18B:** §2.2 (Step 10), §2.3, §7.2, §7.3
- **Direct Source Evidence:**
  - `PHASE18B_IMPLEMENTATION_PROPOSAL.md:132-133`: *"Step 10: Authoritative Record Emission: Emit structured record to trial ledger only if Steps 1–9 executed without unhandled errors."* `[DIRECTLY OBSERVED]`
  - `PHASE18B_IMPLEMENTATION_PROPOSAL.md:140`: *"...the trial must be logged as SIGNAL_TERMINATION with restoration status UNVERIFIED_PROCESS_ABORTED."* `[DIRECTLY OBSERVED]`
  - `pilot_runner.c:198-203`: Signal handler calls `_exit(128 + sig)` immediately upon intercepting `SIGBUS` or `SIGSEGV` `[DIRECTLY OBSERVED]`.
- **Analysis:**
  There is a direct contradiction in Phase 18B. If the runner only writes a record to the ledger at Step 10 conditional on Steps 1–9 completing without unhandled errors, then:
  1. Any trial encountering a protection error in Step 5, a crash trap in Step 6, or a restoration failure in Step 7/8 will **never reach Step 10**.
  2. If the signal handler calls `_exit()`, standard C library I/O buffers are discarded without flushing, and execution terminates abruptly.
  3. Consequently, failed trials will simply be omitted from the output ledger, violating the intention-to-treat accounting requirement that all 1,680 trials appear in the ledger.
- **Required Remediation:**
  The runner logging architecture must adopt an **append-only write-ahead protocol**:
  - Before starting Step 4/5, write a preliminary trial entry (`execution_status = ATTEMPTED_STARTED`) and flush to disk via `fflush()` and `fsync()`.
  - On ordinary error paths (e.g., `vm_protect` failure, restoration failure), write an explicit terminal record (`PROTECT_ERROR` or `RESTORATION_FAILED`) before terminating.
  - For hardware traps, either:
    - An external supervisor / coordinator script wraps the runner execution, detecting exit code `128 + sig` and logging `SIGNAL_TERMINATION` / `UNVERIFIED_PROCESS_ABORTED` to the authoritative ledger, or
    - An emergency async-signal-safe `write()` call writes a raw record directly to a dedicated crash log file descriptor before calling `_exit()`.

---

### Finding 2: Underspecified Protocol Authentication & Framing Semantics
- **Severity:** **MEDIUM**
- **Affected Section in Phase 18B:** §2.2 (Step 6), §3, §7.2
- **Direct Source Evidence:**
  - `combined_campaign.c:39-58`: Implements 18-byte command frame with magic `"SPAC"`, sequence number, command codes, and an inner 16-bit CRC-16 check (`crc16(f, 16)`) `[DIRECTLY OBSERVED]`.
  - `combined_campaign.c:64-67`: Implements `mactag(ss, enc, FRAME, tag)` using `fips202_ref_shake256` with domain separator `0x02`, producing a 32-byte MAC tag `[DIRECTLY OBSERVED]`.
  - `combined_campaign.c:124-128`: Evaluates MAC first; if MAC mismatches, returns `K_MISMATCH`. Only if MAC matches does it decrypt with keystream and evaluate `parse_frame()`; if frame check fails, returns `K_MALFORMED`. Only if both pass does it return `K_EST` `[DIRECTLY OBSERVED]`.
- **Analysis:**
  Phase 18B states in Step 6: *"Construct frame: payload, CRC-16, keystream encryption, MAC tag"* and *"Evaluate MAC tag. If valid and frame parses, session succeeds ($Y_{\text{proto}} = 1$)"*.
  While the conceptual flow is correct, the proposal lacks exact cryptographic and framing interface contracts:
  1. It does not state whether CRC-16 is used for authentication or error detection. CRC-16 is **strictly an error detection checksum** within the command frame, not a cryptographic authenticator.
  2. It does not formally define the `mactag` function: $Tag = \text{SHAKE256}(0x02 \parallel ss \parallel enc, 32)$.
  3. It does not specify the priority of return codes: `K_MISMATCH` takes precedence over frame parsing because frame decryption cannot be trusted if the MAC fails.
- **Required Remediation:**
  Phase 18B must formally document:
  - Outer Cryptographic Authentication: 32-byte MAC tag verified against receiver's decapsulated shared secret.
  - Inner Transport Integrity: 16-bit CRC-16-CCITT ($x^{16} + x^{12} + x^5 + 1$, initial `0xFFFF`) verified on decrypted command payload.
  - Exact acceptance condition: $K_{\text{EST}} \iff (\text{MAC matches}) \land (\text{CRC matches}) \land (\text{Magic } == \text{"SPAC"}) \land (seq \in [wmin, wmax])$.

---

### Finding 3: Ambiguity in the Scope of the Interaction Contrast $\Delta_c$
- **Severity:** **MEDIUM**
- **Affected Section in Phase 18B:** §6.1, §6.2
- **Direct Source Evidence:**
  - `PHASE17H_OPERATOR_RATIFICATION.md:48`: *"1. Primary Protocol Contrast: Evaluated strictly as channel-stratified interaction contrasts $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$ for each channel class $c$."* `[DIRECTLY OBSERVED]`
  - `PHASE18B_IMPLEMENTATION_PROPOSAL.md:281-284`: Defines $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$ without explicitly qualifying the binary outcome variable $Y$ `[DIRECTLY OBSERVED]`.
- **Analysis:**
  In Phase 18B §6.1, $\hat{\Delta}_c$ is stated with abstract probabilities $\hat{p}$. If a reader attempts to apply $\hat{\Delta}_c$ to Cryptographic SDC ($Y_{\text{crypto}}$), the mathematical construct collapses:
  - In conditions $C_{00}$ (clean table, clean wire) and $C_{01}$ (clean table, corrupted wire), clean ML-KEM-768 decapsulation mathematically guarantees zero SDCs ($p_{00} = 0$, $p_{01} = 0$).
  - In blocking channel classes (LOSS, TRUNC, DELAY, INTERRUPT), decapsulation never executes, making $Y_{\text{crypto}}$ undefined.
  - Furthermore, SDC is evaluated as a conditional rate ($k / n_{\text{completed}}$), not an unconditional Bernoulli probability across all assigned trials.
- **Required Remediation:**
  Phase 18B must explicitly state:
  - $\hat{\Delta}_c$ is defined **strictly and exclusively** for the binary **Protocol Key Agreement Endpoint ($Y_{\text{proto}} \in \{0, 1\}$)**.
  - Cryptographic SDC ($Y_{\text{crypto}}$) is evaluated **strictly as a conditional rate** on completed first-attempt decapsulations under $C_{11}$ (and $C_{10}$) via exact Clopper–Pearson upper bounds.

---

### Finding 4: Manifest Schema Ambiguities Across Retries and Conditions
- **Severity:** **MEDIUM**
- **Affected Section in Phase 18B:** §4.1, §4.3
- **Direct Source Evidence:**
  - `PHASE18B_IMPLEMENTATION_PROPOSAL.md:167-197`: Manifest example illustrates a single JSON scenario object with flat channel parameters: `"bit_position": 142, "bit_mask_hex": "0x04", "truncation_bytes": 0, "delay_ticks": 1, "persistence": "TRANSIENT"` `[DIRECTLY OBSERVED]`.
  - `combined_campaign.c:163`: Dynamically derives attempt-specific channel parameters using `prf_bytes("chan", gseed, (uint64_t)condid, (uint64_t)a, pseed, 16)` `[DIRECTLY OBSERVED]`.
- **Analysis:**
  Phase 18B §4.1 specifies a scenario JSON entry, but leaves two critical implementation details ambiguous:
  1. **Top-Level Manifest Structure:** Is `manifest.json` an array of 420 master scenario objects (where each object implicitly expands to 4 matched trials), or an array of 1,680 explicit trial objects?
  2. **Retry Channel Parameters:** If a channel fault is configured as `PERSISTENT`, does Attempt 1 and Attempt 2 reuse the exact same bit position/mask as Attempt 0, or are distinct pseudorandom parameters drawn per attempt index $a \in [0, 2]$? In `combined_campaign.c:163`, PRF draws are keyed on $(gseed, condid, a)$, varying parameters across attempts.
- **Required Remediation:**
  The manifest specification must explicitly resolve:
  - Whether `manifest.json` serializes 420 master seeds with deterministic condition expansion rules, or 1,680 fully expanded trial entries.
  - Exactly how retry channel impairment parameters are derived for attempts $a \in [1, 2]$ when `persistence == PERSISTENT`.

---

### Finding 5: Vector Corpus and Oracle Provenance Scope
- **Severity:** **LOW / INFORMATIONAL (CONFIRMED ACCURATE)**
- **Affected Section in Phase 18B:** §5.1, §5.2, §5.3
- **Direct Source Evidence:**
  - `references/test_vectors/mlkem_expected_kat.h`: Contains exactly 1 static official KAT vector (Vector 0) `[DIRECTLY OBSERVED]`. Zero local vectors (Vectors 1–419) exist on disk `[DIRECTLY OBSERVED]`.
  - `independent_oracle.c:70`: Directly computes $z$ offset as $sk + (2400 - 32) = sk + 2368$ `[DIRECTLY OBSERVED]`.
  - `independent_oracle.c:72-77`: Rejection formula $J(z \parallel \tilde{c}, 32) = \text{SHAKE256}(z \parallel \tilde{c}, 32)$ concatenates 32 bytes of $z$ with 1088 bytes of received ciphertext $\tilde{c}$ (total 1120 bytes) `[DIRECTLY OBSERVED]`.
  - `combined_campaign.c:122`: Passes wire ciphertext `ct2` into `independent_oracle_compute_rejection(ss_rej, sk, ct2)` `[DIRECTLY OBSERVED]`.
- **Audit Conclusion:**
  Phase 18B accurately captures vector inventory and oracle mechanics. The distinction between an **architecturally independent reference implementation** and a formal legal "clean-room" implementation is scientifically rigorous and fully justified.

---

### Finding 6: Memory Lifecycle and Restoration Safety
- **Severity:** **LOW / INFORMATIONAL (CONFIRMED ACCURATE WITH STEP 10 FIX)**
- **Affected Section in Phase 18B:** §2.2, §2.3, §7.1
- **Direct Source Evidence:**
  - `pilot_runner.c:292-315, 482-506`: Verifies `vm_protect` transitions between `VM_PROT_READ` and `VM_PROT_READ | VM_PROT_WRITE` `[DIRECTLY OBSERVED]`.
  - `pilot_runner.c:166-189`: Verifies 16,128 bytes of padding canaries are zero `[DIRECTLY OBSERVED]`.
  - `algorithms/source_ref/mlkem/src/zetas.inc:17-48`: Relocated table is isolated behind `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)` `[DIRECTLY OBSERVED]`.
- **Audit Conclusion:**
  The 10-step memory lifecycle correctly models memory protection transitions and canary checks. With the logging remediation in Finding 1, the lifecycle guarantees fault containment and prevents misleading restoration reporting.

---

## 4. Source-Grounded Corrected Definitions & Exact Formulas

### 4.1 Protocol Key Agreement Endpoint ($Y_{\text{proto}}$)
For master seed $i$ and condition $C \in \{C_{00}, C_{10}, C_{01}, C_{11}\}$:

$$Y_{\text{proto}} = \begin{cases} 
1 & \text{if } \exists a \in [0, \text{RETRY\_MAX}] : \text{AttemptOutcome}(a) == K_{\text{EST}} \\ 
0 & \text{otherwise (PROTOCOL\_ABORT, MALFORMED, LOST, TIMEOUT, or EXECUTION\_ABORT)}
\end{cases}$$

Where an attempt achieves $K_{\text{EST}}$ if and only if:
1. `decaps_ran == 1` and `mlkem768_dec` completes without signal termination.
2. $\text{mactag}(ss_{\text{dec}}, enc, 18) == tag_{\text{received}}$ (32-byte SHAKE256 MAC match).
3. $\text{parse\_frame}(pt, wmin, wmax) == 0$, which verifies:
   - Magic header $== \text{"SPAC"}$ (4 bytes).
   - Sequence number $seq \in [wmin, wmax]$.
   - Command byte $== 1$, Subcommand byte $== 0x10$.
   - CRC-16-CCITT checksum over first 16 bytes matches payload bytes 16–17.

### 4.2 Matched Interaction Contrast ($\hat{\Delta}_c$)
Defined **strictly and exclusively** for $Y_{\text{proto}}$:

$$\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c) = \frac{1}{n_c} \sum_{i=1}^{n_c} \left( Y_{\text{proto}, i}(C_{11}) - Y_{\text{proto}, i}(C_{10}) - Y_{\text{proto}, i}(C_{01}) + Y_{\text{proto}, i}(C_{00}) \right)$$

- Evaluated independently for each active channel class $c \in \{\text{BIT}, \text{DUP}, \text{REORDER}, \text{TRUNC}, \text{LOSS}, \text{DELAY}, \text{INTERRUPT}\}$.
- Complete-case pairing is required: master seeds experiencing execution aborts in any of the four conditions are excluded from the primary contrast as sensitivity, with Intention-To-Test ($Y=0$ on abort) reported as primary.

### 4.3 Exact Clopper–Pearson Upper Bound Recomputation `[INDEPENDENTLY RECOMPUTED]`
For $k = 0$ observed SDC events in $n$ completed first-attempt decapsulations:

$$p_U(n) = 1 - (0.05)^{1/n}$$

Recomputed to 12 decimal places via Python `math.pow` and IEEE-754 double precision:
- **$n = 300$:** $p_U(300) = 1 - 0.05^{1/300} = 0.009936081944 \implies \mathbf{0.993608\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 299$:** $p_U(299) = 1 - 0.05^{1/299} = 0.009969146793 \implies \mathbf{0.996915\% < 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 298$:** $p_U(298) = 1 - 0.05^{1/298} = 0.010002432438 \implies \mathbf{1.000243\% \ge 1.0\%}$ `[INDEPENDENTLY RECOMPUTED]`
- **$n = 0$:** Evaluates to $1 - 0.05^{1/0}$ (division by zero); formally defined as **`INCONCLUSIVE_NO_COMPLETED_TRIALS`**, reporting no numerical bound `[INDEPENDENTLY RECOMPUTED]`.

---

## 5. Source-to-Proposal Traceability Matrix

| Feature / Behavior | Status in Repository | Active Source File & Line Reference | Notes & Reusability |
| :--- | :---: | :--- | :--- |
| **Mach-O `vm_protect` RW/RO** | Exists | `pilot_runner.c:292-315, 482-506` | Demonstrates page unprotect, twiddle write, reprotect. Reusable primitive. |
| **Padding Canaries (16,128 B)** | Exists | `pilot_runner.c:166-189` | Asserts padding bytes in 16KB page remain zero. Reusable primitive. |
| **Relocated `__zetas_page`** | Exists | `zetas.inc:17-48`, `poly.c:269-278` | Guarded by `MLKEM_RESEARCH_RELOCATE_ZETAS`. Reusable compile-time isolation. |
| **Signal Interception (`SIGBUS`)** | Exists | `pilot_runner.c:198-203, 275-285` | Intercepts trap, calls `_exit(128+sig)`. Requires wrapper/logging fix. |
| **Channel Fault Injection (7 Cls)** | Exists | `combined_campaign.c:98-109` | Implements bit corruption, drop, reorder, delay, truncation. Reusable. |
| **Dual Framing (MAC + CRC-16)** | Exists | `combined_campaign.c:39-67, 124-128` | Implements 32B `mactag` and 16B payload CRC-16. Reusable. |
| **Retry Transmission Loop** | Exists | `combined_campaign.c:158-170` | Evaluates $a \in [0, 2]$. Reusable logic, needs Mach-O binding. |
| **TweetFIPS Rejection Oracle** | Exists | `independent_oracle.c:59-79`, `fips202_ref.c:1-86` | Computes $J(z \parallel \tilde{c}, 32)$ using standalone reference. Reusable. |
| **Deterministic Manifest Gen** | **Missing** | *Non-existent on disk* | Must be created in Phase 18C/18D (`generate_manifest.py`). |
| **Preflight Vector Harness** | **Missing** | *Non-existent on disk* | Must be created in Phase 18D (`validate_vectors.c`). |
| **Unified Multi-Fault Runner** | **Missing** | *Non-existent on disk* | Must be created in Phase 18E (`multi_fault_runner.c`). |

---

## 6. Required Amendments to Phase 18B Before Implementation Review

To advance from `CONDITIONAL` to `READY FOR SEPARATE IMPLEMENTATION REVIEW`, the Phase 18B proposal must incorporate the following specific amendments:

1. **Amendment A-1 (Write-Ahead Logging Architecture):**
   - Replace the Step 10 conditional emission rule with a write-ahead / immediate-flush logging protocol.
   - Require that session initialization writes a record with `execution_status = ATTEMPTED_STARTED`, which is updated or finalized upon terminal session exit.
   - Specify that the runner is executed under a process supervisor wrapper that intercepts abnormal child termination (`exit_code >= 128`) and logs `SIGNAL_TERMINATION` with `UNVERIFIED_PROCESS_ABORTED`.

2. **Amendment A-2 (Explicit Dual-Layer Protocol Specification):**
   - Formally document the separation between outer cryptographic authentication (`mactag`) and inner payload integrity (`crc16`).
   - Specify the exact mathematical formula for `mactag` and `keystream` using `fips202_ref_shake256`.
   - Specify the priority order of attempt error codes (`K_MISMATCH` > `K_MALFORMED`).

3. **Amendment A-3 (Interaction Contrast Qualification):**
   - Explicitly qualify $\hat{\Delta}_c$ in §6.1 as applying **strictly and exclusively** to the binary Protocol Key Agreement outcome ($Y_{\text{proto}} \in \{0, 1\}$).
   - Re-affirm that Cryptographic SDC ($Y_{\text{crypto}}$) is evaluated as a conditional rate on completed decapsulations via Clopper–Pearson upper bounds.

4. **Amendment A-4 (Manifest Schema Disambiguation):**
   - Clarify whether `manifest.json` contains 420 master scenario objects or 1,680 individual trial records.
   - Specify the exact deterministic PRF derivation for retry attempt channel parameters under persistent channels.

---

## 7. Explicit Statement of What Remains Untested

In strict adherence to the Anti-Hallucination Protocol:
1. **Dynamic Vector Correctness (Vectors 1–419):** Untested. No locally generated vectors exist on disk; mathematical agreement between SUT and `liboqs` cannot be verified until preflight harness execution `[PROPOSED / NOT YET TESTED]`.
2. **Mach-O Attrition Rate Across 1,680 Transitions:** Untested. The empirical frequency of Darwin ARM64 `vm_protect` hardware traps across 1,680 consecutive transitions is unknown `[UNKNOWN / UNVERIFIED]`.
3. **Multi-Attempt Memory Persistence:** Untested. Holding a mutated Mach-O page across an attempt loop ($a \in [0, 2]$) while simultaneously injecting channel faults has never been dynamically executed in this codebase `[PROPOSED / NOT YET TESTED]`.
4. **Crash-Resilient Ledger Recovery:** Untested. Process crash logging has not been dynamically verified under actual hardware trap signals `[PROPOSED / NOT YET TESTED]`.

---

## 8. SHA-256 Digest Verification `[DIRECTLY OBSERVED]`

| File Path | SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Audit Target Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_CHANGELOG.md` | `818d5cbf89f9582d2659c95ed12c450e6f54d5419dff13d3172f47fdbda1ab56` | Historical Verified `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | *(Computed post-write)* | **Phase 18C Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | *(Computed post-write)* | **Phase 18C Deliverable** `[DIRECTLY OBSERVED]` |

---

## 9. Final Conclusion and Authorization Statement

# **CONDITIONAL — AMENDMENTS REQUIRED**

### Formal Boundary:
Phase 18C completes an independent, strictly read-only audit of the Phase 18B implementation proposal. 

**Advancing to implementation review requires incorporating Amendments A-1 through A-4 into the Phase 18B proposal.** Compiling binaries, linking test harnesses, mutating memory, generating vectors, or executing experimental trials remains strictly **UNAUTHORIZED** and requires explicit human operator authorization.
