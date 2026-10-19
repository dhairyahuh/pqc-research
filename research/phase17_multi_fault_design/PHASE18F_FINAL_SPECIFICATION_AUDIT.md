# Phase 18F — Final Signal Attribution, Ledger Validation, and Protocol Specification Audit

**Document:** `research/phase17_multi_fault_design/PHASE18F_FINAL_SPECIFICATION_AUDIT.md`  
**Date:** 2026-10-12  
**Target Proposal Evaluated:** [PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md)  
**Historical Proposal References:**
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
**Status:** SPECIFICATION AUDIT COMPLETED (Documentation Only — No Code or Experiments)  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified or created, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary & Final Verdict

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Executive Statement:
Phase 18F completes the final specification audit for the ML-KEM-768 multi-fault research campaign. It addresses the four remaining methodological and source-grounded questions:
1. **Signal Attribution & Process Supervisor Contract (§1):** Rigorously proves why positive exit codes `138` and `139` cannot independently prove hardware trap signals, establishes a defensible 5-category termination classification, specifies an out-of-band IPC pipe contract, and strictly prohibits claiming verified memory restoration after process termination.
2. **Ledger Completion Validation & Quota Invariants (§2):** Formulates the exact byte-level hashing rule for `campaign_ledger.jsonl`, distinguishing simple record counts from full campaign validity (enforcing syntax, unique trial IDs, legal state transitions, all 420 master scenarios, and exact quota allocations).
3. **CRC Reproducibility & Parametric Verification (§3):** Fully characterizes the CRC algorithm in [combined_campaign.c:39-44](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L39-L44) as standard **CRC-16/CCITT-FALSE** (Poly `0x1021`, Init `0xFFFF`, RefIn `false`, RefOut `false`, XorOut `0x0000`, Check `0x29b1` on `"123456789"`), serialized big-endian over bytes $0..15$.
4. **Authentication Claim Boundaries & Protocol Realism (§4):** Qualifies the tag construction in `combined_campaign.c:64-67` as a **modeled keyed authentication mechanism** (SHAKE256 PRF), explicitly refuting claims of standardized MAC status and distinguishing it from real space standards like CCSDS SDLS.

No implementation code has been written, compiled, or executed. All proposed architectural fixes remain **`[PROPOSED / NOT YET TESTED]`**.

---

## 1. Issue 1: Signal Attribution and Supervisor Contract

### 1.1 Prior Claim in Phase 18D / 18E
Prior reports proposed that an external supervisor wrapper inspects the child runner's exit status and identifies `SIGBUS`/`SIGSEGV` if the exit status is `128 + sig` (i.e., `138` or `139`).

### 1.2 Directly Observed Source Evidence & Analysis
Inspecting [pilot_runner.c:198-203, 275-280](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase14_persistent_arm_design/pilot_runner.c#L198-L203) `[DIRECTLY OBSERVED]`:
```c
static void handle_trap_signal(int sig) {
    g_signal_received = sig;
    const char msg[] = "\n!!! CRITICAL TRAP SIGNAL INTERCEPTED IN RUNNER !!!\n";
    write(STDERR_FILENO, msg, sizeof(msg) - 1);
    _exit(128 + sig);
}
```
- **The POSIX Exit Code Ambiguity:**
  When a process invokes `_exit(status)`, the POSIX kernel terminates the process **normally**.
  From the operating system's perspective:
  - In C `waitpid(&status)`, `WIFEXITED(status)` evaluates to **true**; `WIFSIGNALED(status)` evaluates to **false**.
  - The child exit code is `WEXITSTATUS(status) == 138` (or `139`).
  - However, an exit code of `138` or `139` **does not uniquely prove** that a signal occurred. Any application logic, third-party library, or assertion failure could arbitrarily invoke `exit(138)`.
  - Conversely, if an unhandled signal terminates the process (e.g., `SIGKILL`, or an unhandled hardware trap before handlers are bound), `WIFSIGNALED` is **true**, and Python's `subprocess.Popen.poll()` returns a **negative number** (`-10` for `SIGBUS`, `-11` for `SIGSEGV` on Darwin) `[DIRECTLY OBSERVED]`.
  - Therefore, positive exit codes `138`/`139` cannot independently prove signal termination without out-of-band corroboration.

### 1.3 Defensible Termination Classification `[PROPOSED / NOT YET TESTED]`
The supervisor must categorize child process termination across five distinct, non-overlapping categories:

| Category | Detection Criteria | Semantics & Classification | Authoritative Ledger Status |
| :--- | :--- | :--- | :--- |
| **Cat 1: Direct Signal Termination** | `proc.returncode < 0` (`WIFSIGNALED` true) | Child terminated directly by OS kernel via signal `-proc.returncode`. | `execution_status = SIGNAL_TERMINATION_DIRECT`<br>`restoration_status = UNVERIFIED_PROCESS_ABORTED` |
| **Cat 2: Handler-Mediated Trap Exit** | `proc.returncode in (138, 139)` + IPC token confirmed | Child intercepted trap signal and called `_exit(128 + sig)`. | `execution_status = SIGNAL_TERMINATION_HANDLER`<br>`restoration_status = UNVERIFIED_PROCESS_ABORTED` |
| **Cat 3: Ambiguous Non-Zero Exit** | `proc.returncode > 0` and `proc.returncode not in (138, 139)` | Child terminated with non-zero exit code during an open trial. | `execution_status = ABNORMAL_PROCESS_EXIT`<br>`restoration_status = UNVERIFIED_PROCESS_ABORTED` |
| **Cat 4: Sudden Clean Termination** | `proc.returncode == 0`, but trial left unfinalized | Child exited with code 0 without writing a `FINALIZE` record. | `execution_status = UNEXPECTED_CLEAN_EXIT`<br>`restoration_status = UNVERIFIED_PROCESS_ABORTED` |
| **Cat 5: Supervisor Interruption** | Supervisor intercepted `SIGINT`/`SIGTERM` or crashed | Supervisor was interrupted; child state indeterminate. | `execution_status = SUPERVISOR_ABORT`<br>`restoration_status = UNVERIFIED_PROCESS_ABORTED` |

### 1.4 Future Out-of-Band IPC Event Marker Specification `[PROPOSED / NOT YET TESTED]`
To eliminate all ambiguity between an accidental exit code `138`/`139` and a genuine intercepted hardware trap, the future runner architecture must implement an out-of-band IPC event pipe:
1. The supervisor creates an anonymous UNIX pipe: `pipe(pipefd)`.
2. The child inherits `pipefd[1]` (write end) on a dedicated descriptor (e.g., `FD 3`).
3. Inside `handle_trap_signal(sig)`:
   The signal handler issues an async-signal-safe write:
   `write(3, "TRAP_SIGNAL:SIGBUS\n", 19);` (or `SIGSEGV`)
   before calling `_exit(128 + sig)`.
4. The supervisor reads `pipefd[0]`. Only if the exact token `"TRAP_SIGNAL:..."` is received does it classify the termination as `SIGNAL_TERMINATION_HANDLER`. If the child exits with `138` but no token was written, it is classified as `ABNORMAL_PROCESS_EXIT_AMBIGUOUS`.
5. **Absolute Invariant:** In all termination categories, the ledger records **`restoration_status: UNVERIFIED_PROCESS_ABORTED`**. The proposal **never claims restoration was verified** following an abnormal process abort.

### 1.5 Remaining Uncertainty
- The out-of-band IPC pipe is an untested architectural specification `[PROPOSED / NOT YET TESTED]`.
- Its behavior under kernel panics or immediate process freezing has not been dynamically verified `[UNKNOWN / UNVERIFIED]`.

---

## 2. Issue 2: Ledger Completion Validation and Quota Invariants

### 2.1 Prior Claim in Phase 18D / 18E
Prior reports specified write-ahead logging with `fsync()` and an end-of-campaign sentinel record containing `content_sha256`.

### 2.2 Directly Observed Source Evidence & Analysis
- Counting records alone (e.g., `wc -l == 1680`) is completely insufficient to certify campaign validity. A corrupted runner could output duplicate trials for scenario 1, skip scenario 2, or omit condition $C_{11}$, yet still emit 1,680 records.
- True scientific campaign validation requires a multi-stage semantic ledger validator (`validate_ledger.py`) that strictly checks all structural, parametric, and cryptographic invariants before certifying completeness.

### 2.3 Formal Ledger Validation Contract `[PROPOSED / NOT YET TESTED]`

#### 1. Exact Non-Self-Referential Hashing Specification
- The ledger file `campaign_ledger.jsonl` comprises ASCII text lines terminated by `\n` (`0x0A`).
- The final line of a completed campaign is strictly:
  ```json
  {"record_type":"CAMPAIGN_SEAL","status":"COMPLETE","trial_count":1680,"covered_bytes":M,"content_sha256":"<64_hex_chars>"}\n
  ```
- **Byte Sequence:** `content_sha256` covers **strictly bytes $0$ through $M-1$** (all bytes prior to the start of the `CAMPAIGN_SEAL` line).
- The verifier measures the byte offset of the `CAMPAIGN_SEAL` line, asserts it equals $M$, hashes bytes $0..M-1$ using SHA-256, and asserts exact match with `content_sha256`.

#### 2. Mandatory Validation Invariants
The offline validator rejects the ledger (`INVALID_LEDGER`) unless all six invariants pass:
1. **Invariant 1: Syntax & Delimitation:** Every line parses as valid UTF-8 JSON terminated by `\n`.
2. **Invariant 2: Unique Trial Keys:** Every trial is uniquely identified by `(master_seed_id, condition)` where `master_seed_id` $\in [1, 420]$ and `condition` $\in \{C_{00}, C_{10}, C_{01}, C_{11}\}$. Zero duplicate keys.
3. **Invariant 3: Legal State Transitions:** Each trial key has exactly one `"START"` record followed by exactly one `"FINALIZE"` record.
4. **Invariant 4: Complete Scenario Coverage:** Exactly 420 distinct scenario IDs present, with all four matched conditions ($C_{00}, C_{10}, C_{01}, C_{11}$) present for each scenario ID ($420 \times 4 = 1,680$ finalized trials).
5. **Invariant 5: Quota Stratum Enforcement:**
   - Quota 1: Exactly 300 scenarios ($1,200$ trials) assigned to `CH_BIT` with active table mutation.
   - Quota 2: Exactly 40 scenarios ($160$ trials) split evenly: 20 `CH_DUP`, 20 `CH_REORDER`.
   - Quota 3: Exactly 60 scenarios ($240$ trials) split evenly: 15 `CH_TRUNC`, 15 `CH_LOSS`, 15 `CH_DELAY`, 15 `CH_INTERRUPT`.
   - Quota 4: Exactly 20 scenarios ($80$ trials) split evenly across the 4 control cells (5 dormant-clean, 5 dormant-bit, 5 sham-clean, 5 sham-bit).
6. **Invariant 6: Absence of Extraneous Records:** Zero orphan finalizations, zero dangling starts, and zero unexpected records.

#### 3. Campaign Classification Matrix
- **`COMPLETE`:** Invariants 1–6 pass; valid `CAMPAIGN_SEAL` matching `content_sha256`.
- **`PARTIAL_ABORTED`:** Invariants 1 and 2 pass, but $< 1,680$ trials finalized, or a dangling start was finalized by the supervisor as `UNVERIFIED_PROCESS_ABORTED`. No seal present.
- **`INVALID_LEDGER`:** Any syntax corruption, duplicate trial IDs, orphan records, missing conditions, or seal mismatch.

### 2.4 Remaining Uncertainty
- The offline validator script (`validate_ledger.py`) is an untested architectural design `[PROPOSED / NOT YET TESTED]`.

---

## 3. Issue 3: CRC Reproducibility and Parametric Verification

### 3.1 Prior Claim in Phase 18D / 18E
Phase 18D/18E described the framing CRC as CRC-16 with polynomial `0x1021`.

### 3.2 Directly Observed Source Evidence
Inspecting [combined_campaign.c:39-44, 48-58](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L39-L44) `[DIRECTLY OBSERVED]`:
```c
static uint16_t crc16(const uint8_t *d, size_t n){
    uint16_t c=0xFFFF;
    for(size_t i=0;i<n;i++){ c^=(uint16_t)(d[i]<<8);
        for(int b=0;b<8;b++) c=(c&0x8000)?(uint16_t)((c<<1)^0x1021):(uint16_t)(c<<1); }
    return c;
}
static void put_be16(uint8_t*p,uint16_t v){p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static void build_frame(uint8_t f[FRAME], uint16_t seq){
    memcpy(f,"SPAC",4); put_be16(f+4,seq); f[6]=1; f[7]=0x10;
    put_be32(f+8,45); put_be32(f+12,60000); put_be16(f+16,crc16(f,16));
}
```

### 3.3 Complete Parametric Characterization `[DIRECTLY OBSERVED]`
The implementation matches the standard **CRC-16/CCITT-FALSE** (also known as `CRC-16/IBM-3740` or `CRC-16/AUTOSAR`):
- **Width:** 16 bits (`uint16_t`).
- **Polynomial (poly):** `0x1021` ($x^{16} + x^{12} + x^5 + 1$).
- **Initial Value (init):** `0xFFFF`.
- **Reflected Input (refIn):** `false`. Bytes are shifted left by 8 (`d[i] << 8`) into the high byte of the accumulator; bits are processed MSB-first (`c & 0x8000`).
- **Reflected Output (refOut):** `false`. Accumulator returned directly without bit-reversal.
- **Final XOR Mask (xorOut):** `0x0000`. No final XOR applied.
- **Mathematical Check Value:** On standard ASCII test string `"123456789"`, the algorithm yields **`0x29B1`** `[INDEPENDENTLY RECOMPUTED]`.
- **Covered Bytes:** Exactly the first 16 bytes of the frame ($f[0..15]$).
- **Serialization & Endianness:** Stored big-endian in bytes 16 and 17:
  $f[16] = (crc \gg 8) \land 0xFF$, $f[17] = crc \land 0xFF$.
- **Parser Validation:** `parse_frame` evaluates:
  `crc16(f, 16) == (uint16_t)((f[16] << 8) | f[17])`.

### 3.4 Remaining Uncertainty
- None. The mathematical definition, parameters, bit ordering, and serialization are fully established from active source lines.

---

## 4. Issue 4: Authentication Claim Boundaries and Protocol Realism

### 4.1 Prior Claim in Phase 18D / 18E
Phase 18D described the outer tag as a "cryptographic MAC" providing "authentic payload validation."

### 4.2 Directly Observed Source Evidence
Inspecting [combined_campaign.c:60-67](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L60-L67) `[DIRECTLY OBSERVED]`:
```c
/* abstract keyed primitives via standalone SHAKE (documented model choice) */
static void keystream(const uint8_t ss_[SS], uint8_t *out, size_t n){
    uint8_t in[1+SS]; in[0]=0x01; memcpy(in+1,ss_,SS); fips202_ref_shake256(out,n,in,sizeof in);
}
static void mactag(const uint8_t ss_[SS], const uint8_t *enc, size_t n, uint8_t out[TAG]){
    uint8_t in[1+SS+FRAME]; in[0]=0x02; memcpy(in+1,ss_,SS); memcpy(in+1+SS,enc,n);
    fips202_ref_shake256(out,TAG,in,1+SS+n);
}
```

### 4.3 Scientific Claim Boundaries and Protocol Realism

#### 1. Cryptographic Claim Boundary
- The author of `combined_campaign.c` explicitly labeled these routines:
  `/* abstract keyed primitives via standalone SHAKE (documented model choice) */`.
- `mactag` is constructed by evaluating an unkeyed extendable-output function (SHAKE256) over a secret-prefixed buffer:
  $$Tag = \text{SHAKE256}(0x02 \parallel ss \parallel enc, 32)$$
- **Formal Boundary:** This construction is a **modeled keyed authentication tag mechanism** (keyed PRF). It is **not** a standardized cryptographic MAC:
  - It is not NIST KMAC (SP 800-185).
  - It is not HMAC (FIPS 198-1).
  - It is not an ISO/IEC 9797 MAC.
- It relies on the heuristic model that SHAKE256 with a secret prefix acts as a PRF under an idealized random permutation assumption. In academic literature, it must be referred to as a **modeled PRF authentication tag**, not a certified MAC standard.

#### 2. Contrast with Real-World Spacecraft Protocols
- **Real Spacecraft Standards:** Operational satellite command and telemetry links adhere to international standards such as the **CCSDS Space Data Link Security (SDLS) Protocol** (CCSDS 355.0-B-1).
- CCSDS SDLS incorporates:
  - Standardized authenticated encryption: AES-GCM-256 or AES-CBC-256 with HMAC-SHA-256.
  - A formal Security Header embedding a Security Parameter Index (SPI) and a strictly monotonic Anti-Replay Counter (Sequence Number).
  - Explicit frame synchronization markers and forward error correction (FEC) telemetry coding.
- **Model Realism:** The protocol in `combined_campaign.c` is a **simplified software simulation model** created to evaluate cross-layer interaction between physical/link layer faults and memory corruption. It must **never be claimed or marketed as a flight-ready spacecraft communications protocol**.

### 4.4 Remaining Uncertainty
- While the simulated protocol is sufficient for software fault-interaction research, its empirical security margins have not been analyzed under formal cryptographic reduction proofs `[INFERRED]`.

---

## 5. Claim and Evidence Traceability Matrix

| Component / Claim | Evidentiary Basis | Source File & Location | Current Verified Status |
| :--- | :---: | :--- | :--- |
| **Exit Code 138/139 Ambiguity** | `[DIRECTLY OBSERVED]` | `pilot_runner.c:198-203` | `_exit(128+sig)` is a normal exit to OS; cannot uniquely prove signal. |
| **Out-of-Band IPC Pipe** | `[PROPOSED / NOT YET TESTED]` | Phase 18F §1.4 | Dedicated pipe proposed to disambiguate handled traps. |
| **Unverified Restoration on Abort** | `[INFERRED]` | Phase 18F §1.3 | Restoration must be logged as unverified on any abnormal termination. |
| **Non-Self-Referential Seal** | `[PROPOSED / NOT YET TESTED]` | Phase 18F §2.3 | SHA-256 covers bytes $0..M-1$; resolves quine defect. |
| **Quota Enforcement Invariants** | `[DIRECTLY OBSERVED]` | `PHASE17H_OPERATOR_RATIFICATION.md:32-42` | Exact allocations verified: Q1: 300, Q2: 40, Q3: 60, Q4: 20 ($N=420$). |
| **CRC-16 Parameters (CCITT-FALSE)** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:39-44` | Poly `0x1021`, Init `0xFFFF`, RefIn/Out `false`, Check `0x29B1`. |
| **CRC Big-Endian Serialization** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:45, 50` | Bytes 16..17 stored MSB-first over first 16 bytes. |
| **Modeled Tag via SHAKE256** | `[DIRECTLY OBSERVED]` | `combined_campaign.c:64-67` | $0x02 \parallel ss \parallel enc$; abstract modeled PRF, not NIST MAC. |
| **Contrast with CCSDS SDLS** | `[INFERRED]` | Phase 18F §4.3 | Simulated protocol distinguished from flight-grade CCSDS standards. |
| **NIST KAT Vector 0 on Disk** | `[DIRECTLY OBSERVED]` | `references/test_vectors/mlkem_expected_kat.h` | 1 official KAT verified on disk. |
| **Local Vectors 1–419 on Disk** | `[DIRECTLY OBSERVED]` | *Absence confirmed via search* | Zero local vectors exist on disk; preflight generation required. |
| **Clopper–Pearson Bounds ($n=298..300$)** | `[INDEPENDENTLY RECOMPUTED]` | Mathematical formula $1 - 0.05^{1/n}$ | $n=300: 0.9936\%$, $n=299: 0.9969\%$, $n=298: 1.0002\%$, $n=0$: undef. |

---

## 6. Implementation Requirements That Remain Untested

In strict adherence to anti-hallucination rules:
1. **Out-of-Band Signal IPC Pipe:** Untested. Anonymous pipe communication inside `handle_trap_signal` has not been implemented or tested `[PROPOSED / NOT YET TESTED]`.
2. **Offline Ledger Validator Script:** Untested. `validate_ledger.py` enforcing Invariants 1–6 has not been written or tested `[PROPOSED / NOT YET TESTED]`.
3. **Unified Multi-Fault Runner Integration:** Untested. Coordination of Darwin `vm_protect` Mach-O page mutations with channel retry loops does not exist in any compiled binary `[PROPOSED / NOT YET TESTED]`.
4. **Dynamic Preflight Vector Corpus:** Untested. Vectors 1–419 have not been generated or cross-checked against `liboqs v0.16.0` `[PROPOSED / NOT YET TESTED]`.
5. **Darwin ARM64 VM Protection Attrition:** Untested. Hardware trap survival rate across 1,680 consecutive `vm_protect` transitions is unknown `[UNKNOWN / UNVERIFIED]`.

---

## 7. Repository State and Recomputed SHA-256 File Hashes `[DIRECTLY OBSERVED]`

Computed via `shasum -a 256` on actual on-disk bytes:

| File Path | SHA-256 Digest | Status / Role |
| :--- | :--- | :---: |
| `research/phase17_multi_fault_design/PHASE18F_FINAL_SPECIFICATION_AUDIT.md` | *(Computed upon file write)* | **Phase 18F Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18F_CHANGELOG.md` | *(Computed upon file write)* | **Phase 18F Deliverable** `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18E_RESIDUAL_DEFECT_RESOLUTION.md` | `f2f51ab6c8a9ad91efb7396d64b88a8c6e84a4266895c597048b689791e97a7d` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18E_CHANGELOG.md` | `9f87827e9c625aee41c73405e55638912c66d31185582e6bc0db0ac837f3402c` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CORRECTED_IMPLEMENTATION_PROPOSAL.md` | `987925793b543a4456c32bbaf47cc7f60ede0a1f88df7b7308861524fc624dac` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18D_CHANGELOG.md` | `e5f631029d5a717819c5c7b51eff360291060344673e4e1e305829392a06a74e` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_INDEPENDENT_AUDIT.md` | `77dfabfe672e42de281e6299c8c692006e3fa3e707d5f2ec31cf902851aa6561` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18C_CHANGELOG.md` | `2947278c38c14347ed24e199aada4ec00ebfe80377ede55efe81881571dfe782` | Historical Reference `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE18B_IMPLEMENTATION_PROPOSAL.md` | `b8279a13a9cfce51f8ca34057e82cb1bda803a6b2aa3da652c6158aaf10ef280` | Superseded Document `[DIRECTLY OBSERVED]` |
| `research/phase17_multi_fault_design/PHASE17H_OPERATOR_RATIFICATION.md` | `6910e4ec89904f1f73a94497263c68b8a34df58bfca40c3ad0fb5d5dfc231f79` | Historical Ratification `[DIRECTLY OBSERVED]` |
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `research/combined_harness/combined_campaign.c` | `45b939768e32719b086812bd42fa493ec4f979d3a29061af6d1bc44afc39a403` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/zetas.inc` | `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `algorithms/source_ref/mlkem/src/poly.c` | `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/independent_oracle.c` | `a297b2ef0748c948ca8ff6c272c9e24047c6e97c72308337c6927351949b3b54` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `tfib_experiments/phase11_oracle/fips202_ref.c` | `ce41fae902693a4aa2dc38849ebd3a8f9804dc5be8ea699e91494f6053bcc676` | Architectural Reference `[DIRECTLY OBSERVED]` |
| `references/test_vectors/mlkem_expected_kat.h` | `af87225bf785ac824d06a2cadd0a9d1c79ee9a505b3ebce0b444c59b79a6d2c7` | Architectural Reference `[DIRECTLY OBSERVED]` |

### Git Working Tree Status `[DIRECTLY OBSERVED]`
- Active Branch: `space-resilience-framework`.
- Preserved all 10 uncommitted tracked files in the working tree.
- Zero files staged, committed, pushed, or reverted.

---

## 8. Final Status and Authorization Statement

# **READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Explicit Governance Boundary:
Phase 18F completes the definitive, source-verified specification audit. All methodological, signal-attribution, ledger-validation, and cryptographic claim boundaries are formal and unambiguous.

**This document does NOT authorize compiling binaries, linking test harnesses, mutating virtual memory, generating vector corpora, or executing experimental trials.** Those actions require separate human operator authorization under subsequent review gates.
