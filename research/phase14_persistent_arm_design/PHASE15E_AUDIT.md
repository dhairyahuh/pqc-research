# Phase 15E — Independent Read-Only Audit of Phase 15D

**Auditor:** Independent Skeptical Cryptographic Implementation Auditor  
**Audit Target:** Repository state following Phase 15D (`pilot_runner.c`, `PHASE15D_REPORT.md`, `PHASE15D_CHANGELOG.md`, `pilot_runner.c.phase15b_bak`, historical artifacts)  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Mode:** Strictly Read-Only Audit (Zero compilation, zero execution, zero modification of repository code or git state)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## Executive Summary

This independent read-only audit evaluated the actual repository artifacts produced during Phase 15D. In accordance with audit standards, `PHASE15D_REPORT.md` was treated as an unverified claim document rather than evidence. The audit directly inspected the source code of `pilot_runner.c`, the backup artifact `pilot_runner.c.phase15b_bak`, reference vector definitions in `references/test_vectors/mlkem_expected_kat.h`, historical Phase 15A/B/C documentation, and filesystem SHA-256 digests.

### Key Audit Conclusions:
1. **Oracle Independence & FIPS 203 Conformance (PASS):** The newly introduced Keccak-f[1600] / SHAKE256 implementation in `pilot_runner.c` is fully self-contained, standard-conformant, and shares zero code with `mlkem-native`. The dynamic rejection key derivation strictly follows NIST FIPS 203 Algorithm 17: $\bar{K} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$ using 1120 bytes of concatenated input ($32 + 1088$). The four-way endpoint classifier correctly distinguishes $K_{golden}$, $K_{rej}$, unexpected outputs (`DIFFERENT_OUTPUT`), and decapsulation failures (`NO_OUTPUT`).
2. **Process Safety & Transactional Cleanup (PASS WITH OBSERVATION):** The runner enforces a single structured 6-step cleanup sequence (restore entry $\rightarrow$ readback check $\rightarrow$ reprotect RO $\rightarrow$ live `vm_region_64` query $\rightarrow$ full table & canary verification $\rightarrow$ baseline KAT recheck). If any cleanup step fails, the runner terminates immediately, preventing trials on a corrupted table. The async-signal-safe trap handler (`SIGBUS`, `SIGSEGV`) terminates via `_exit(128 + sig)`, tearing down the address space cleanly.
3. **Bounds Checking & Ledger Schema (PASS WITH MINOR OBSERVATION):** Upper bounds checking (`target_idx >= 128`) fails closed. However, any negative target index is unconditionally treated as an unmutated baseline trial without asserting `target_idx == -1`. Furthermore, the runner's stdout CSV emits 8 columns, while the historical `PHASE15B_TRIAL_LEDGER.csv` contained 9 columns (omitting `expected_behavior`).
4. **Provenance & Hash Reconciliation (FAIL ON 2 ARTIFACT HASHES):** Independent recomputation revealed that `PHASE15D_REPORT.md` (Section 5) recorded incorrect SHA-256 hashes for historical artifacts `PHASE15B_REPORT.md` and `PHASE15B_TRIAL_LEDGER.csv`. All other hashes matched.

---

## Audit A — Independent Rejection-Key Oracle

### A.1 Input Traceability & Concatenation Order
Inspection of `pilot_runner.c` (lines 304–323) demonstrates:
```c
const uint8_t *test_z = test_vector_sk + MLKEM768_SK_BYTES - MLKEM768_Z_BYTES;
size_t z_len = MLKEM768_Z_BYTES; /* 32 bytes */
size_t ct_len = MLKEM768_CT_BYTES; /* 1088 bytes */
size_t z_c_len = z_len + ct_len; /* 1120 bytes */

uint8_t *z_c_buf = malloc(z_c_len);
memcpy(z_c_buf, test_z, z_len);
memcpy(z_c_buf + z_len, test_vector_ct, ct_len);
```
* **Input Sourcing:** Secret seed $z$ is extracted from the terminal 32 bytes of `test_vector_sk[2400]` (offset 2368 to 2399). This matches FIPS 203 Section 6.3 decapsulation key layout: $dk = (dk_{PKE} \parallel ek_{PKE} \parallel H(ek_{PKE}) \parallel z)$.
* **Ciphertext:** Ciphertext $c$ is taken directly from `test_vector_ct[1088]`.
* **Concatenation Order:** Concatenation order is strictly $z$ followed by $c$, forming an exact 1120-byte input buffer. This conforms to FIPS 203 Algorithm 17, Step 5: $\bar{K} \leftarrow J(z \parallel c, 32)$.

### A.2 Standalone FIPS 202 SHAKE256 Implementation
`pilot_runner.c` (lines 52–182) implements an in-source Keccak-f[1600] / SHAKE256 engine:
* **Rate:** Defined as `const size_t rate = 136;` (136 bytes = 1088 bits). For SHAKE256, capacity is 512 bits; rate is $1600 - 512 = 1088$ bits. Conforms to FIPS 202 Table 4.
* **Byte Order:** 64-bit lanes are reconstructed and stored using standard little-endian byte indexing (`st_bytes[w * 8 + b] << (b * 8)`).
* **Round Function:** Standard 24 rounds of $\iota \circ \chi \circ \pi \circ \rho \circ \theta$ with official round constants `keccakf_rndc[24]`, rotation offsets `keccakf_rotc[24]`, and lane indices `keccakf_piln[24]`.
* **Domain Separation & Padding:** Multi-block absorption XORs incoming data into state. Padding applies `st_bytes[pos] ^= 0x1F;` and `st_bytes[rate - 1] ^= 0x80;`. If `pos == rate - 1`, the byte becomes $0x1F \oplus 0x80 = 0x9F$. This strictly adheres to FIPS 202 Section B.2 `pad10*1` with SHAKE domain separator `1111_2`.
* **Squeezing:** Handles arbitrary output lengths, squeezing 32 bytes into the output buffer.
* **Independence:** Zero header inclusions from `algorithms/source_ref/mlkem`, zero calls to `mlk_shake256`, and zero shared object code. The oracle is 100% independent of the cryptographic target.

### A.3 Known-Answer Values & Self-Tests
1. **NIST FIPS 202 Empty String KAT:**
   Line 185: `nist_shake256_empty_kat[32]` matches official NIST CAVP:
   `46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f`
   Preflight line 295 executes `independent_shake256("", 0, ...)` and asserts equality.
2. **Rejection Key KAT:**
   Line 191: `expected_krej_kat[32]` contains `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03`. Preflight lines 304–335 dynamically derive $J(z \parallel c, 32)$ and assert bit-for-bit equality against `expected_krej_kat`.
   *Audit Note:* The value `f0f0e158...` was verified independently in Python during Phase 15C using standard library `hashlib.shake_256(z + ct).digest(32)`.

### A.4 Classifier Branch Audit
Inspection of `oracle_classify_endpoint()` (lines 250–271):
- `!oracle_available` $\rightarrow$ `"UNKNOWN"`
- `dec_rc != 0` $\rightarrow$ `"NO_OUTPUT"`
- `memcmp(ss_out, golden_ss, 32) == 0` $\rightarrow$ `"EXPECTED_OUTPUT"`
- `memcmp(ss_out, krej, 32) == 0` $\rightarrow$ `"REJECTION"`
- `memcmp(ss_out, ...) != 0` $\rightarrow$ `"DIFFERENT_OUTPUT"`

**Finding (PASS):** Every comparison branch is disjoint and mutually exclusive. An unexpected output (e.g. SDC or arithmetic distortion) is labelled `"DIFFERENT_OUTPUT"`, eliminating the false rejection classification present in Phase 15B.

---

## Audit B — Cleanup and Process Safety

### B.1 Trace of Post-Mutation Execution Paths
The mutation and cleanup lifecycle was traced through all possible branch conditions (lines 483–645):

```text
[vm_protect(RW)]
  ├── Failed (kr != 0) ──> Record REJECTED/NOT_RUN ──> Break loop (No write occurred)
  └── Succeeded (page_is_rw = 1)
        │
        [Volatile Write vtable[idx] = target_val]
        [Volatile Readback Check]
        │
        [vm_protect(RO)]
          ├── Succeeded (page_is_rw = 0)
          └── Failed (kr != 0) ──> (page_is_rw remains 1; skips decapsulation)
                │
                [Decapsulation mlkem768_dec] (executed ONLY IF page_is_rw == 0 && mutation_applied)
                │
                └──> UNCONDITIONAL ENTRY TO MANDATORY CLEANUP BLOCK (Lines 562–645)
                       │
                       ├── Step 1: vm_protect(RW) if page currently RO
                       ├── Step 2: vtable[idx] = orig_val; verify readback
                       ├── Step 3: vm_protect(RO)
                       ├── Step 4: Live vm_region_64 query (verify VM_PROT_READ && !VM_PROT_WRITE)
                       ├── Step 5: memcmp full table (256B) & check 16,128 canary bytes == 0
                       └── Step 6: Post-trial baseline KAT decapsulation recheck
```

### B.2 Evaluation of Safety Properties
* **Restoration of Original Entry:** Guaranteed. Lines 580–586 restore `orig_val` and verify via volatile readback.
* **Reprotection to Read-Only:** Guaranteed. Lines 590–611 call `vm_protect(RO)` and independently query the kernel via `vm_region_64`. If `v_info.protection & VM_PROT_WRITE` is detected, cleanup fails.
* **Canary & Table Verification:** Guaranteed. Lines 614–623 verify all 128 twiddle entries against `golden_zetas` and all 16,128 canary bytes.
* **Conditional Baseline Recheck:** Guaranteed. Line 627 checks `if (cleanup_passed)`. Baseline decapsulation is attempted **only** after steps 1–5 have passed.
* **Fail-Stop on Cleanup Failure:** Guaranteed. Line 641 sets `records[t].restoration_status = "RESTORATION_FAILED"` and executes `break;`. The runner halts immediately, preventing subsequent trials on a corrupted table.
* **Signal Handling:**
  Lines 198–203:
  ```c
  static void handle_trap_signal(int sig) {
      g_signal_received = sig;
      const char msg[] = "\n!!! CRITICAL TRAP SIGNAL INTERCEPTED IN RUNNER !!!\n";
      write(STDERR_FILENO, msg, sizeof(msg) - 1);
      _exit(128 + sig);
  }
  ```
  `write()` and `_exit()` are POSIX async-signal-safe. The signal handler does not perform unsafe memory allocations or longjmps. Process termination via `_exit()` safely destroys the Mach-O virtual address space.
  *Observation:* In the event of a fatal signal, in-process cleanup is not executed because the kernel tears down the entire address space. Downstream tooling must recognize exit status codes $128 + \text{SIGBUS} = 138$ and $128 + \text{SIGSEGV} = 139$ as abort conditions.

---

## Audit C — Bounds and Trial Ledger

### C.1 Target Bounds Checks
Inspection of lines 468–477:
```c
if (pilot_specs[t].target_idx >= 0) {
    if (pilot_specs[t].target_idx >= 128) {
        fprintf(stderr, "BOUNDS CHECK FAIL: target_idx %d >= 128 in trial %d. Failing closed.\n",
                pilot_specs[t].target_idx, t);
        records[t].mutation_status = "REJECTED";
        records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
        records[t].crypto_endpoint = "NOT_RUN";
        records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
        continue;
    }
}
```
* **Upper Bounds:** Enforces `target_idx < 128` and fails closed before calculating memory addresses or modifying protections.
* **Integer Arithmetic:** Target mutation uses well-defined wrapping: `target_val = (int16_t)((uint16_t)orig_val ^ mask);` (line 488).
* **Negative Sentinel Observation:** The check `pilot_specs[t].target_idx >= 0` guards the mutation block. If `target_idx < 0`, execution branches to the baseline check (line 647). Any negative index (e.g. -2) would currently be treated as an unmutated baseline trial rather than rejected as an invalid sentinel. Recommendation: assert `target_idx == -1` for baseline trials.

### C.2 Trial Ledger Schema Reconciliation
Comparison between `pilot_runner.c` stdout and historical Phase 15B artifacts:
* **Phase 15D Runner stdout (line 678):**
  `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss` (8 columns).
* **Historical `PHASE15B_TRIAL_LEDGER.csv`:**
  `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior` (9 columns).
* **Audit Finding:** The runner prints 8 columns, omitting `expected_behavior`. The 8 printed columns match the formal outcome taxonomy, but automated parsers expecting the 9-column Phase 15B schema must be aware of this difference.

---

## Audit D — Provenance, Scope, and Hash Verification

### D.1 Independent SHA-256 Hash Reconciliation
Every relevant artifact was independently hashed using `shasum -a 256` and compared against the values reported in `PHASE15D_REPORT.md` (Section 5):

| File Path | Reported Hash in Phase 15D Report | Independently Computed Hash | Status |
|:---|:---|:---|:---:|
| `research/phase14_persistent_arm_design/pilot_runner.c` | `064e7b1f4f3ca19dc6d901a3a2885f9b306c71a3810d0f8ee70b152ee49d62cb` | `064e7b1f4f3ca19dc6d901a3a2885f9b306c71a3810d0f8ee70b152ee49d62cb` | **MATCH (PASS)** |
| `research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | **MATCH (PASS)** |
| `bin/pilot_runner` | `db8c5f5823d0c7ce886ea8a88bb30afa2c891783f4d5f2ecaee3cc611a9d8298` | `db8c5f5823d0c7ce886ea8a88bb30afa2c891783f4d5f2ecaee3cc611a9d8298` | **MATCH (PASS)** |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | **MATCH (PASS)** |
| `bin/test_fips_kats_research` | `01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf` | `01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf` | **MATCH (PASS)** |
| `research/phase14_persistent_arm_design/PHASE15A_REPORT.md` | `c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981` | `c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981` | **MATCH (PASS)** |
| `research/phase14_persistent_arm_design/PHASE15B_REPORT.md` | `c6bba92f0254c50c53d06ebef4fc9b17743d57b3bf97bf875185d34ffab3573c` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | **MISMATCH (FAIL)** |
| `research/phase14_persistent_arm_design/PHASE15B_TRIAL_LEDGER.csv` | `7973715d2a33ebfe11bb3bbca6ee3a7cfbeafc04516ff8be7d9ae17351ff5606` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | **MISMATCH (FAIL)** |

**Critical Hash Finding:** The author of `PHASE15D_REPORT.md` recorded incorrect SHA-256 digests for `PHASE15B_REPORT.md` and `PHASE15B_TRIAL_LEDGER.csv`. The actual files on disk have digests `0a530225...` and `5cf48fb9...`. This documentation defect must be formally noted and corrected in project records.

### D.2 Claim Demarcation & Untested Behaviors
`PHASE15D_REPORT.md` correctly identified 5 untested behaviors in Section 6 (no live fault trials, no live memory mutation, no signal trap injection, no forced emergency cleanup abort, and no multi-vector sweeps).

**Auditor Epistemological Clarification:**
1. **Compilation** proves only language conformance and static linkability; it does **not** prove runtime virtual memory isolation under stress.
2. **Oracle self-test (`--check-oracle`)** proves that the independent SHAKE256 implementation computes the correct test vector digest; it does **not** prove that decapsulation will always produce that digest under unobserved hardware faults.
3. **KAT suite pass** proves that the unmutated research build retains standard conformance; it does **not** validate post-fault recovery properties.

---

## Final Recommendation

## **CONDITIONAL — SPECIFIC FINDINGS MUST BE RESOLVED**

### Remediation Requirements Before Live Pilot Approval:
1. **Hash Ledger Correction:** Correct the erroneous SHA-256 digests for `PHASE15B_REPORT.md` (`0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (`5cf48fb9...`) in Phase 15D documentation.
2. **Sentinel Index Validation:** Strengthen negative index checking in `pilot_runner.c` to explicitly enforce `target_idx == -1` for baseline runs, failing closed on any other negative index (e.g. `target_idx < -1`).
3. **CSV Schema Alignment:** Acknowledge or align the 8-column stdout CSV with downstream ingestion pipelines expecting the historical 9-column format.

*Mandatory Stop Condition: Phase 16 planning and live pilot execution remain unauthorized until a separate authorization gate reviews this audit.*
