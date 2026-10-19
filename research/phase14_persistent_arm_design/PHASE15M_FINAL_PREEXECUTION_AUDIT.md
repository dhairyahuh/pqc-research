# Phase 15M — Final Pre-Execution Audit

**Auditor:** Independent Skeptical Cryptographic Systems Auditor & Safety Reviewer  
**Audit Target:** `research/phase14_persistent_arm_design/PHASE15L_FINAL_DECISION.md`, `research/phase14_persistent_arm_design/pilot_runner.c`, `bin/pilot_runner`, and relocatable build artifacts  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Audit Mode:** Strictly Read-Only Audit (Zero compilation, zero execution, zero memory mutation, zero page-protection changes)  
**Date:** 2026-10-11  
**Deliverable Path:** `research/phase14_persistent_arm_design/PHASE15M_FINAL_PREEXECUTION_AUDIT.md`  

---

## Executive Summary

This final pre-execution audit independently verified the code, build artifacts, safety paths, and governance documentation of Phase 15L. Rather than relying on previous phase reports, this audit directly inspected the actual C source code (`pilot_runner.c`), disassembled symbol layout and binary strings (`bin/pilot_runner`), and recomputed all cryptographic digests on disk.

### Audit Verdict by Area:
1. **Abnormal-Signal & Cleanup Path Handling:** **PASS**
2. **Restoration Gating & Verification Invariants:** **PASS**
3. **FIPS 203 Rejection Oracle & Output Classifier:** **PASS**
4. **Preflight & Post-Run Identification & Detection:** **PASS**
5. **Methodological Scope & Claim Boundaries:** **PASS**

### Overall Governance Recommendation:
# **READY FOR EXPLICIT HUMAN AUTHORIZATION**

*Notice: This audit verifies technical code readiness and evidence consistency. The auditor does not authorize execution. Live trials require explicit, deliberate human authorization.*

---

## 1. Audit Area 1: Abnormal-Signal, Cleanup, and Aborted-Run Handling

**Verdict:** **PASS**

### 1.1 Code Inspection of Abnormal Signal Handling
- **Source Reference:** `pilot_runner.c`, lines 196–203 & 275–280.
- **Signal Installation:**
  ```c
  struct sigaction sa;
  memset(&sa, 0, sizeof(sa));
  sa.sa_handler = handle_trap_signal;
  sigaction(SIGBUS, &sa, NULL);
  sigaction(SIGSEGV, &sa, NULL);
  ```
- **Handler Implementation:**
  ```c
  static volatile sig_atomic_t g_signal_received = 0;
  static void handle_trap_signal(int sig) {
      g_signal_received = sig;
      const char msg[] = "\n!!! CRITICAL TRAP SIGNAL INTERCEPTED IN RUNNER !!!\n";
      write(STDERR_FILENO, msg, sizeof(msg) - 1);
      _exit(128 + sig);
  }
  ```
- **Auditor Verification:**
  1. The handler uses strictly async-signal-safe primitives: `write()` and `_exit()`.
  2. The handler executes **zero in-process cleanup**. This is standard-conformant C systems practice; calling non-reentrant routines (`vm_protect`, `printf`, `malloc`, crypto decapsulation) during a faulted state can cause deadlocks or recursive memory traps.
  3. Immediate invocation of `_exit(128 + sig)` forces the Darwin Mach kernel to terminate the process and reclaim the private user-space virtual address space. Because the table exists purely in process-private memory (`__DATA_CONST`), process destruction safely eliminates all corrupted state at the OS kernel boundary.
  4. The summary 9-column CSV ledger (lines 682–703) is printed only at the normal conclusion of `main()`. If a signal interrupts execution, the CSV summary is **never printed**.
  5. An abnormally terminated run **never** claims `RESTORED_AND_BASELINE_RECHECK_PASSED`.

### 1.2 Cleanup Control Flow
- **Source Reference:** `pilot_runner.c`, lines 565–645.
- All non-fatal in-trial failures (post-mutation read-back mismatch at line 514, reprotection failure at line 524, decapsulation runtime error, FO rejection, or altered secret) bypass decapsulation (if prior to Step 5) and route directly into the 6-step cleanup pipeline to restore the table.
- Any failure during Cleanup Steps 1–6 sets `restoration_status = "RESTORATION_FAILED"` and invokes `break;` (lines 641–643), terminating the trial loop immediately.

---

## 2. Audit Area 2: Restoration Gating & Verification Invariants

**Verdict:** **PASS**

### 2.1 Inspection of All Restoration Status Assignments
An exhaustive search across `pilot_runner.c` confirms that `"RESTORED_AND_BASELINE_RECHECK_PASSED"` is assigned at exactly two locations:

1. **Mutation & Sham Trials (Line 638):**
   ```c
   if (cleanup_passed && ss_recheck_ok) {
       records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
   ```
   This assignment is strictly gated on:
   - **Step 1 Unprotect:** `vm_protect(RW)` returns `KERN_SUCCESS` (lines 569–576).
   - **Step 2 Value Restore & Read-Back:** Volatile write `vtable[idx] = orig_val;` followed by `restored_val == orig_val` assertion (lines 579–587).
   - **Step 3 Reprotect:** `vm_protect(RO)` returns `KERN_SUCCESS` (lines 589–596).
   - **Step 4 Kernel Permission Verification:** `vm_region_64` live query verifies `(v_info.protection & VM_PROT_READ) && !(v_info.protection & VM_PROT_WRITE)` (lines 598–611).
   - **Step 5 Full Canaries:** Full 256-byte table comparison `memcmp(table_ptr, golden_zetas, 256) == 0` AND zero-byte scan of all 16,128 padding bytes (lines 613–623).
   - **Step 6 Baseline KAT Decapsulation:** `mlkem768_dec` on pristine test vector produces `recheck_rc == 0` and `memcmp(ss_recheck, test_vector_ss, 32) == 0`, asserting `ss_recheck_ok = 1` (lines 626–635).
2. **Baseline Trials (Line 660, strictly `target_idx == -1`):**
   ```c
   int table_ok = (memcmp(table_ptr, golden_zetas, sizeof(golden_zetas)) == 0);
   if (table_ok && strcmp(records[t].crypto_endpoint, "EXPECTED_OUTPUT") == 0) {
       records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
   } else {
       records[t].restoration_status = "RESTORATION_FAILED";
   }
   ```
   Requires pristine 256-byte table memory and golden shared secret reproduction.
3. **Invalid-Target Fails-Closed (Lines 475 & 674):**
   Assigns `NOT_RUN_INVALID_TARGET`, with `mutation_status = "REJECTED"`, `consumption_status = "VERIFIED_NOT_CONSUMED"`, and `crypto_endpoint = "NOT_RUN"`.
4. **Pre-Trial Unprotect Failure (Line 499):**
   Assigns `"UNKNOWN"` and breaks out of the trial loop.

**Auditor Determination:**  
Under zero code path can a trial claim restoration or baseline success without passing all necessary read-back, reprotection, canary, and decapsulation recheck gates.

---

## 3. Audit Area 3: FIPS 203 Rejection Oracle & Output Classifier

**Verdict:** **PASS**

### 3.1 Mathematical Specification & Conformance
In NIST FIPS 203 Section 6.3 (Algorithm 17, `ML-KEM.Decaps_internal`), line 10 defines implicit rejection:
$$K = J(z \parallel c, 32)$$
where $J(x, 32) = \text{SHAKE256}(x, 32)$.

- **Input Derivation (`pilot_runner.c`, lines 305–324):**
  - $z$: Decapsulation secret key seed (last 32 bytes of $sk$, offset `2400 - 32 = 2368`).
  - $c$: Ciphertext (1088 bytes).
  - Total concatenated buffer length: $32 + 1088 = 1120$ bytes.
  - Squeezed output: 32 bytes via `independent_shake256()`.
- **Preflight Verification (`pilot_runner.c`, lines 294–336):**
  - Standalone SHAKE256 self-test verified against NIST empty-string KAT `46b9dd2b...`.
  - Derived rejection key matches golden test vector KAT `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` bit-for-bit.

### 3.2 Endpoint Classification Logic
- **Source Reference:** `pilot_runner.c`, lines 251–272 (`oracle_classify_endpoint`):
  ```c
  if (!oracle_available) return "UNKNOWN";
  if (dec_rc != 0) return "NO_OUTPUT";
  if (memcmp(ss_out, golden_ss, 32) == 0) return "EXPECTED_OUTPUT";
  if (memcmp(ss_out, krej, 32) == 0) return "REJECTION";
  return "DIFFERENT_OUTPUT";
  ```
- **Auditor Determination:**  
  The classifier is exhaustive, deterministic, and correctly distinguishes valid decryption (`EXPECTED_OUTPUT`), standard FO implicit rejection (`REJECTION`), altered secrets (`DIFFERENT_OUTPUT`), and runtime aborts (`NO_OUTPUT`).

---

## 4. Audit Area 4: Preflight & Post-Run Identification & Detection

**Verdict:** **PASS**

### 4.1 Build Identification & Verification
Direct inspection of `bin/pilot_runner` using Mach-O inspection tools verifies:
1. `_mlk_zetas_page` is mapped in section `(__DATA_CONST,__zetas_page)` at virtual address `0x100024000` with 16 KB page alignment.
2. Linkage to research entry points `_mlkem_research_get_zetas_mutable_ptr` and `_mlkem_research_get_zetas_table` from `mlkem768_persistent_reloc.o`.
3. Literal status strings `"NOT_RUN_INVALID_TARGET"`, `"RESTORED_AND_BASELINE_RECHECK_PASSED"`, and `"RESTORATION_FAILED"` are present in the `__cstring` section.
4. Preflight 1 (lines 346–361) and Preflight 2 (lines 363–402) dynamically verify address alignment and kernel permissions at process startup.

### 4.2 Detection of Failed or Incomplete Execution
- **Preflight Failures:** Process exits with code `1` before executing Trial 0.
- **In-Flight Signal:** Process exits with code `138` or `139`; summary CSV is never emitted.
- **Cleanup Failure:** Emits `"CRITICAL EMERGENCY"`, sets `RESTORATION_FAILED`, and halts loop.
- **Normal Completion:** Exit code is `0`; prints complete 16-row CSV ledger; Trial 15 passes clean baseline decapsulation.
- **Post-Run Requirement:** Operator executes external multi-vector KAT suite `./bin/test_fips_kats_research`.

---

## 5. Audit Area 5: Methodological Scope & Claim Boundaries

**Verdict:** **PASS**

### 5.1 Real Scope of the 16-Trial Pilot
The pilot covers 16 deterministic boundary conditions:
- Baseline controls: Trials 0 and 15 (`target_idx = -1`).
- Sham controls: Trials 2 and 13 (`bit_mask = 0x0000`).
- Active twiddle layers: Root index 0, forward layer 1 index 1 (LSB, mid, MSB flips), layer 6 index 32, layer 7 index 63, mulcache index 64, mid-mulcache index 95, and invNTT index 127.

### 5.2 Supported Conclusions vs Prohibited Overclaims
- **Supported Conclusions:**
  1. Feasibility of dynamic `vm_protect` memory manipulation on Darwin ARM64.
  2. Proof that tested twiddle constants are loaded from memory rather than folded into immediate constants.
  3. Verification that twiddle corruption propagates through NTT into FO implicit rejection.
  4. In-place transactional cleanup restores bit-identical baseline state.
- **Prohibited Overclaims (Mandatory Guardrails in `CLAIM_BOUNDARIES.md`):**
  1. Zero claims of physical radiation tolerance, single-event upset (SEU) resilience, or space qualification.
  2. Zero statistical claims regarding general SDC rates across the 2,048-bit parameter space.
  3. Zero claims regarding unmodified production binaries (where `mlk_zetas` is immutable in `__TEXT,__const`).

---

## 6. Cryptographic Hash Provenance Ledger

All digests were independently recomputed on disk using `shasum -a 256` and cross-referenced:

| Artifact Path | Previously Reported Hash | Independently Recomputed Hash | Status |
|:---|:---|:---|:---:|
| `pilot_runner.c` | `39f7e831...` (Phase 15H/15I) | `39f7e83140e1a8ebceb3e2fc091382cad918fff8eb381b73db551bbbcab4b871` | **MATCH (PASS)** |
| `bin/pilot_runner` | `d9da42c3...` (Phase 15H/15I) | `d9da42c33cf45816800e0591cfbc0c0700bb6033883f601aa6f7b834cedd716e` | **MATCH (PASS)** |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf...` (Phase 15A–15I) | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | **MATCH (PASS)** |
| `pilot_runner.c.phase15b_bak` | `bbddee21...` (Phase 15D–15I) | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | **MATCH (PASS)** |
| `PHASE15B_REPORT.md` | `0a530225...` (Phase 15F Errata) | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | **MATCH (PASS)** |
| `PHASE15B_TRIAL_LEDGER.csv` | `5cf48fb9...` (Phase 15F Errata) | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | **MATCH (PASS)** |
| `PHASE15F_ERRATA.md` | `d305ae17...` (Phase 15F) | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | **MATCH (PASS)** |
| `PHASE15H_REPORT.md` | `b6198a74...` (Phase 15I) | `b6198a740908a67d106426f104af295edd3ec0b8535b238ee71adf506678b6e1` | **MATCH (PASS)** |
| `PHASE15H_CHANGELOG.md` | `cc3a278f...` (Phase 15I) | `cc3a278f3488e505ef2c90888bc20898637321fdd2008b830b8d2970b41da35a` | **MATCH (PASS)** |
| `PHASE15I_AUDIT.md` | `7541750b...` (Phase 15I) | `7541750b210c9ff01c76b23a6c31606d0b57979f57b46e667f1d87cc70b6f669` | **MATCH (PASS)** |
| `PHASE15I_FINDINGS_MATRIX.md` | `8d39f7cf...` (Phase 15I) | `8d39f7cf342ab08fadb42b1f3f75b4837f05e05dde7fce292af6570778d1fde4` | **MATCH (PASS)** |
| `PHASE15J_READINESS_REVIEW.md` | `f256a29b...` (Phase 15J) | `f256a29b4fc5aedc1a383c44cc9b9c9131dc374e382b6cbb987e82adc58f7548` | **MATCH (PASS)** |
| `PHASE15J_GO_NO_GO_MATRIX.md` | `e9185406...` (Phase 15J) | `e9185406d7becd36bc9f176425f215270834e5084deacc6d54613e61f4f6b7b6` | **MATCH (PASS)** |
| `PHASE15K_SAFETY_AUDIT.md` | `c1c57189...` (Phase 15K) | `c1c57189cd6f1556eab4518c5ed192de67360f31e545a788d766a7329156b2e9` | **MATCH (PASS)** |
| `PHASE15K_FINDINGS_MATRIX.md` | `e184ae5c...` (Phase 15K) | `e184ae5ce76600702763cd4333ea12fcf150432f328c9413f85bfc72ed39dd30` | **MATCH (PASS)** |
| `PHASE15L_FINAL_DECISION.md` | `20958cfd...` (Phase 15L) | `20958cfd6e136b86d3a7b6c8359baa41c20ef7d18e8a68df3170bca614e21cf8` | **MATCH (PASS)** |

---

## 7. Unresolved Operational Risks and Explicit Abort Criteria

### 7.1 Residual Architectural Risks (Non-Blocking)
1. **Mixed Stream Output on `stdout`:** The runner intersperses trial diagnostic headers with the final 9-column CSV ledger. Automated ingestion parsers must filter by the header row or regex `^[0-9]+,[0-9\-]+,0x[0-9a-fA-F]{4},`.
2. **Unquoted String Columns:** The `expected_behavior` field does not enclose strings in quotes (`%s`). Safe for current 16 hardcoded descriptions; fragile if expanded to free text with commas.
3. **External Post-Run KAT Requirement:** The full NIST FIPS 203 KAT suite (`./bin/test_fips_kats_research`) is not invoked internally and must be executed by the operator following pilot execution.

### 7.2 Explicit Abort Criteria (Immediate Process Termination)
The pilot run must be declared failed and aborted immediately if:
1. Any Preflight check (1–5) exits with a non-zero code.
2. Any `vm_protect` call returns a code other than `KERN_SUCCESS` (`0`).
3. Memory write read-back mismatch occurs during mutation or restoration.
4. Any non-zero byte is detected in the 16,128-byte page padding canary.
5. Live `vm_region_64` query indicates write permissions remain active post-cleanup.
6. Restored table memory differs from golden zetas.
7. Post-trial decapsulation recheck produces a shared secret differing from `test_vector_ss`.
8. Interception of any hardware signal (`SIGBUS` or `SIGSEGV`), invoking `_exit(128 + sig)`.

---

## Final Review Verdict

# **READY FOR EXPLICIT HUMAN AUTHORIZATION**

**Final Auditor Summary:**  
All five audit areas are verified **PASS**. The source code, compiled binary, and relocatable objects strictly adhere to fail-closed memory protection, transactional rollback, orthogonal ledger status reporting, and independent cryptographic oracle verification. All historical artifacts and working-tree changes remain intact.

*Notice: This pre-execution audit is strictly read-only. It does not authorize or execute live trials or Phase 16.*
