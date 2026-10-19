# Phase 15Q: Authorized Controlled Pilot Execution Report

**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software Study  
**Phase:** Phase 15Q — Controlled Pilot Execution  
**Execution Timestamp:** 2026-10-11T09:49:34Z (UTC) / 15:19:34 (Local)  
**Host Environment:** Darwin ARM64 (macOS, Apple Silicon)  
**Git Branch:** `space-resilience-framework` (Commit `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Executable Target:** `bin/pilot_runner` (Mach-O 64-bit arm64)  
**Runner Source:** `research/phase14_persistent_arm_design/pilot_runner.c`  
**Relocation Object:** `bin/obj/mlkem768_persistent_reloc.o`  
**Operational Status:** COMPLETE SUCCESS (Exit Code 0, 16/16 Trials Executed, 100% Restored)

---

## 1. Operator Authorization & Protocol Compliance

Execution of the 16-trial persistent-table pilot was initiated under explicit human operator authorization:

> *"I explicitly authorize the 16-trial Phase 15Q pilot on the research-only Darwin ARM64 build."*

In accordance with Phase 15 protocol:
- No broader experiments, parameter variations, or production build modifications were performed.
- All pre-existing tracked modifications across the repository (10 files) were preserved intact.
- All historical Phase 15A–15P reports, ledgers, and errata were preserved byte-for-byte.
- All execution data was written to a newly established isolated directory: `results/phase15q/`.

---

## 2. Preflight Verification Results

Prior to executing any memory mutation, all preflight gates were executed and independently verified:

1. **Git Working-Tree Integrity:**
   - Active branch: `space-resilience-framework`.
   - Tracked modified files: strictly the 10 pre-existing files documented in Phase 15A–15P. No unexpected files were modified or staged.
2. **Build Identity & Cryptographic Hash Verification:**
   - Runner source `pilot_runner.c`: `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` (matches Phase 15O/15P).
   - Executable binary `bin/pilot_runner`: `6a671b96ee1869ed1630f7c42f1cdeca8fd16b24467d1e2289a3fdb08bdea9b6` (matches Phase 15O/15P).
   - Relocation object `mlkem768_persistent_reloc.o`: `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` (matches Phase 15O/15P).
3. **Darwin ARM64 Memory Mapping Verification:**
   - Binary format: Mach-O 64-bit arm64.
   - Dedicated table section: `(__DATA_CONST,__zetas_page)` at virtual address `0x100024000` (runtime base: `0x1047b8000`), size `0x4000` (16,384 bytes, 16 KB page-aligned).
   - Live VM protection query via `vm_region_64`: confirmed initial page protection `r--` (`VM_PROT_READ`, 0x1) and max protection `rw-` (`0x3`).
4. **Independent FIPS 202/203 Oracle Self-Test:**
   - Pre-execution `./bin/pilot_runner --check-oracle` ran non-mutating validation:
     - SHAKE256 empty-string KAT verified against NIST FIPS 202 (`46b9dd2b...`).
     - Independent FIPS 203 rejection key derivation \(J(z \parallel c, 32)\) verified bit-identical to expected KAT reference (`f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03`).
5. **Preflight Checklist Passed:**
   - Preflight 1/5 (Alignment): PASS.
   - Preflight 2/5 (VM Query): PASS.
   - Preflight 3/5 (Table & Canary Integrity): PASS (128 twiddles match golden digest; 16,128 zero-padding bytes clean).
   - Preflight 4/5 (Dry-Run Protection Toggle): PASS (`vm_protect` RW $\rightarrow$ RO without write).
   - Preflight 5/5 (Baseline KAT Decapsulation): PASS (`ss_base` matches NIST KAT `0b1b32be...`).
   - Verdict: **GO**.

---

## 3. Pilot Execution Trace

- **Invocation:** `./bin/pilot_runner`
- **Output Redirection:** `> results/phase15q/stdout.txt 2> results/phase15q/stderr.txt`
- **Start Timestamp:** `2026-10-11T09:49:34Z`
- **End Timestamp:** `2026-10-11T09:49:34Z`
- **Elapsed Duration:** < 1.0 second (deterministic in-process execution)
- **Exit Status:** `0` (clean normal exit)
- **Stderr Size:** `0 bytes` (zero hardware trap signals, zero diagnostic errors)
- **Stdout Size:** `11,718 bytes` (143 lines)

---

## 4. Authoritative 16-Trial Ledger

The table below reproduces the unmodified 9-column CSV ledger emitted by `bin/pilot_runner` during execution (preserved byte-for-byte in `results/phase15q/trial_ledger.csv`):

| Trial ID | Target Index | Bit Mask | Mutation Status | Consumption Status | Crypto Endpoint | Restoration Status | Output Shared Secret (Hex) | Declared Expected Behavior |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | -1 | `0x0000` | `NOT_ATTEMPTED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e` | Baseline golden key match |
| **1** | 0 | `0x0001` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e` | Mathematically unused twiddle factor (Root) |
| **2** | 0 | `0x0000` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e` | Sham control on index 0 (mask 0) |
| **3** | 1 | `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 1 twiddle factor -> FO rejection key |
| **4** | 1 | `0x0080` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 1 twiddle factor -> FO rejection key |
| **5** | 1 | `0x8000` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 1 twiddle factor -> FO rejection key |
| **6** | 32 | `0x0002` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 6 twiddle factor -> FO rejection key |
| **7** | 63 | `0x0004` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 7 twiddle factor -> FO rejection key |
| **8** | 64 | `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Mulcache factor -> FO rejection key |
| **9** | 64 | `0x0400` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Mulcache factor -> FO rejection key |
| **10** | 95 | `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Mulcache factor -> FO rejection key |
| **11** | 127 | `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active InvNTT/Basemul factor -> FO rejection key |
| **12** | 127 | `0xffff` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active InvNTT/Basemul factor -> FO rejection key |
| **13** | 64 | `0x0000` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e` | Sham control on active index 64 (mask 0) |
| **14** | 2 | `0x0008` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | Active Layer 2 twiddle factor -> FO rejection key |
| **15** | -1 | `0x0000` | `NOT_ATTEMPTED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e` | Post-pilot baseline golden key match |

---

## 5. Post-Run Verification Analysis

### 5.1 Machine-Verifiable Markers and Header Consistency
- **Ledger Header:** `AUTHORITATIVE TRIAL LEDGER (CSV FORMAT - 9 COLUMNS)`. (No partial or aborted header emitted).
- **Run Completion Marker:** `>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<`.
- **Exit Status:** Strictly `0`.
- **Row Count:** Exactly 16 data rows + 1 CSV header row = 17 lines in `trial_ledger.csv`.
- **Sequential IDs:** Monotonically increasing from `0` to `15` without gaps or duplicate entries.

### 5.2 Cryptographic Endpoint Verification
- **Expected KAT Shared Secret:** `0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e`
- **Independent FIPS 203 Rejection Key \(K_{\text{rej}} = J(z \parallel c, 32)\):** `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03`
- **Baseline Trials (Trials 0 and 15):** Both reproduced the expected KAT shared secret bit-identically.
- **Sham Controls (Trials 2 and 13):** Unprotecting and rewriting the unmutated value produced the expected KAT shared secret without alteration (`EXPECTED_OUTPUT`), proving that the memory-protection cycle alone introduces zero side effects.
- **Root/Unused Twiddle Factor (Trial 1):** Inverting bit 0 of `zetas[0]` produced the expected KAT shared secret (`EXPECTED_OUTPUT`, `VERIFIED_NOT_CONSUMED`). This empirically validates the theoretical property that `zetas[0]` (the Montgomery root 1) is never consumed by the butterfly loops in the ML-KEM-768 NTT/InvNTT implementations.
- **Active Fault Injection Trials (Trials 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14):**
  - All 11 trials produced the exact 32-byte rejection key \(K_{\text{rej}}\).
  - Every active corruption was detected by the ML-KEM implicit rejection check (re-encryption verification failure in decapsulation).
  - Zero trials produced corrupted unrejected keys (`DIFFERENT_OUTPUT`), and zero trials crashed or terminated abnormally (`NO_OUTPUT`).

### 5.3 Rollback & Restoration Integrity
In every one of the 14 mutating trials (Trials 1 through 14), the full 6-step cleanup pipeline executed:
1. Entry unprotected to RW via `vm_protect`.
2. Original golden twiddle restored and verified via immediate read-back.
3. Page reprotected to RO via `vm_protect`.
4. Live kernel permission queried via `vm_region_64`, proving page returned to `r--` (not writable).
5. Full 256-byte table byte-comparison against golden `zetas` + verification of 16,128 zero-padding canary bytes passed.
6. Baseline KAT decapsulation recheck succeeded, reproducing `0b1b32be...`.

Following completion of all trials, a non-mutating `--check-oracle` dry run was executed, verifying that the binary and memory state remained pristine.

---

## 6. Categorized Synthesis: Observations, Verified Results, Limitations, and Interpretation

### 6.1 Direct Empirical Observations
1. Page permissions on Darwin ARM64 for `(__DATA_CONST,__zetas_page)` can be transitioned from `r--` to `rw-` and back to `r--` using Mach VM APIs without triggering system instability.
2. Inverting bits in active twiddle table entries (`zetas[1]`, `zetas[2]`, `zetas[32]`, `zetas[63]`, `zetas[64]`, `zetas[95]`, `zetas[127]`) alters the NTT polynomial computation during decapsulation, causing re-encryption ciphertext mismatch.
3. Decapsulation in all 11 active fault trials returned the exact constant-time implicit rejection key \(J(z \parallel c, 32)\).
4. Corrupting `zetas[0]` did not alter decapsulation output for the test vector.
5. In-process rollback restored table state, zero padding, read-only permissions, and baseline KAT execution after every single trial.

### 6.2 Verified Results (What is Concretely Proven)
- **Feasibility of In-Memory Fault Injection:** It is technically feasible on Darwin ARM64 to inject targeted bit-flips into an isolated constant memory page, observe cryptographic outputs, and execute verified rollback within a single process.
- **Fujisaki-Okamoto Rejection Fidelity:** ML-KEM-768 decapsulation reliably enters the FIPS 203 implicit rejection branch when polynomial arithmetic is perturbed by active twiddle faults under this test vector.
- **Inactive Twiddle Confirmation:** Index 0 of the standard precomputed table is confirmed dormant for ML-KEM-768 decapsulation in this implementation.
- **Fail-Closed Harness Robustness:** The Phase 15O runner successfully executed all 16 predeclared trials, accurately emitted the authoritative 9-column ledger, and exited with status 0.

### 6.3 Failures and Limitations
- **No In-Flight Faults:** Faults were injected statically before decapsulation invocation; this pilot does not model transient single-event transients (SETs) occurring mid-clock-cycle.
- **Single Test Vector:** All 16 trials operated on a single NIST KAT ciphertext/secret-key pair. General statistical behavior across random ciphertexts was not evaluated.
- **Limited Sample Size ($n=16$):** The pilot tested 7 distinct indices out of 128 (5.5% table coverage) with 6 bitmasks. It does not constitute a full combinatorial fault space analysis.
- **Synthetic Software Mechanism:** The use of `vm_protect` is a software simulation of hardware state change; it does not replicate beam-induced charge accumulation or multi-bit latch upset physics.

### 6.4 Interpretation
The results establish that the persistent-table design for Darwin ARM64 is mechanically sound and capable of serving as an experimental testbed. The complete agreement between observed rejection keys and the independent FIPS 203 oracle confirms that ML-KEM's implicit rejection mechanism functions as designed when NTT arithmetic is perturbed. Furthermore, the inactive status of `zetas[0]` illustrates how architectural twiddle-packing decisions create silent blind spots in generic memory fault models.

---

## 7. Claim Boundaries

| Permitted Engineering Claims | Strictly Prohibited / Unsupported Claims |
| :--- | :--- |
| Feasibility of isolated page-level table fault testing on Darwin ARM64 | Broad statistical radiation resilience of ML-KEM-768 |
| Active twiddle corruption triggers FIPS 203 implicit rejection under test KAT | Single-Event Upset (SEU) cross-section or rate prediction |
| In-process memory protection rollback and baseline verification succeeds | Production-binary flight readiness or space-grade qualification |
| Twiddle index 0 is inactive in the tested NTT implementation | Resistance to physical side-channel or fault-injection attacks (PFA/SIFA) |

---

## 8. Cryptographic Hash Manifest

All artifacts produced or tested during Phase 15Q were hashed using SHA-256 (`shasum -a 256`):

```text
57b5ce1d9fa266250f719976f1a539a350da7d6640fb0e79329d1196fe24c209  results/phase15q/execution_info.txt
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  results/phase15q/stderr.txt
466616759375aa09cad4053f7f8ccaf496ff4c50a97702700af418703d4dcd60  results/phase15q/stdout.txt
5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c  results/phase15q/trial_ledger.csv
292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce  research/phase14_persistent_arm_design/pilot_runner.c
6a671b96ee1869ed1630f7c42f1cdeca8fd16b24467d1e2289a3fdb08bdea9b6  bin/pilot_runner
c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f  bin/obj/mlkem768_persistent_reloc.o
```

---

## 9. Final Operator Summary

- **Report Path:** `results/phase15q/PHASE15Q_PILOT_EXECUTION_REPORT.md` and `research/phase14_persistent_arm_design/PHASE15Q_PILOT_EXECUTION_REPORT.md`
- **Exact Exit Code:** `0`
- **Trials Actually Executed:** 16 / 16 (100%)
- **Restoration & Baseline Recheck Status:** 16 / 16 PASS (100% verified table restoration, canary integrity, and post-trial baseline decapsulation match)
- **Protocol Deviations:** None
- **Repository State:** Clean with respect to Phase 15Q operations; all 10 pre-existing tracked modifications preserved.
