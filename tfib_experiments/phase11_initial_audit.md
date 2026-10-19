# Phase 11 Initial Audit: Repository State, Artifact Inspection, and Baseline Defect Analysis

**Document:** Phase 0 Deliverable — Independent Technical Audit & Pre-Modification Baseline  
**Auditor:** Skeptical Cryptographic Software Verification Researcher & Experimental Auditor  
**Date:** October 2026  
**Target Repository:** `dhairyahuh/pqc-research`  
**Host Architecture:** Apple Silicon ARM64 (Apple M3 Pro, 11-core), macOS Darwin 25.1.0, Apple Clang 17.0.0 (`-O3`)  

---

## 1. Repository & Git Status Inspection

### 1.1 Branch & Working Tree
- **Active Branch:** `space-resilience-framework`
- **Head Commit:** `55dd937` (*docs(phase17): systematic prior-art review, novelty gap analysis, and research manuscript draft*)
- **Upstream Tracking:** `origin/space-resilience-framework` (local tree is 1 commit ahead of origin `ca38dec`)
- **Working Tree State:** Dirty. Contains modified repository tracking files and 39 untracked artifact directories/files from Phases 1–18.
- **Rule Adherence:** No code or test files will be committed or pushed in this phase. Existing data files in `chatgpt/` and root directories are preserved unchanged.

---

## 2. Inventory and Inspection of Existing TFIB Artifacts

The audit inspected the artifacts in [`chatgpt/`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/) and the corresponding root experiment files:

| Artifact Path | Verified File Status | Key Observations & Contents |
| :--- | :--- | :--- |
| [`chatgpt/tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_trial_level_results.csv) | 901 lines (78 KB) | 900 individual trial records across 18 test suites (50 trials/suite). Records `stage`, `butterfly`, `bit`, `persistent`, `trigger_count`, `mismatch_count`, `recovery_count`, `oracle_valid_match`, `oracle_rejection_match`, `final_status`, and `oracle_classification`. |
| [`chatgpt/tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_benchmark_raw.csv) | 40,001 lines (1.3 MB) | 40,000 raw latency samples (10,000 per condition): `BASELINE FAULT_FREE`, `TFIB_REF FAULT_FREE`, `TFIB_META FAULT_FREE`, and `TFIB_REF ACTIVE_RECOVERY`. |
| [`chatgpt/tfib_validity_audit_runner.c`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_validity_audit_runner.c) | 235 lines (9.6 KB) | Test harness executing 18 fault suites against `mlkem768_inst.o` and `libtfib.a`. |
| [`chatgpt/tfib_benchmark_audit.c`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_benchmark_audit.c) | 196 lines (8.2 KB) | High-precision timing harness using macOS `mach_absolute_time()`. |
| [`chatgpt/tfib_reproduced_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_reproduced_results.csv) | 19 lines (1.4 KB) | Aggregated outcome matrix summarizing detection rates, recovery counts, fail-stops, FO catches, and SDC counts. |
| [`chatgpt/README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/README.md) | 71 lines (3.5 KB) | Schema reference documentation for external auditors. |

---

## 3. Production Code Path vs. Experiment Harness Comparison

A line-by-line comparison was conducted between the production implementation (`algorithms/source_ref/mlkem/`), the TFIB countermeasure implementation (`tfib_implementation/`), and the audit runner (`chatgpt/tfib_validity_audit_runner.c`).

### 3.1 Production Implementation Structure
- **Production NTT Butterfly:** [`algorithms/source_ref/mlkem/src/poly.c:380-415`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L380-L415) (`mlk_ntt_butterfly_block`).
- **Production InvNTT Butterfly:** [`algorithms/source_ref/mlkem/src/poly.c:545-590`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L545-L590) (`mlk_invntt_layer`).
- **Decapsulation State Machine:** [`algorithms/source_ref/mlkem/src/kem.c:403-530`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L403-L530) (`mlk_kem_dec_monitored`).
- **Compiled Object Under Test:** `bin/obj/mlkem768_inst.o` (compiled with `-O3 -DMLK_MULTILEVEL_BUILD_NO_SHARED`).

### 3.2 Countermeasure Architecture (`tfib_implementation/`)
- `tfib_core.c`: Implements the production monitor hooks:
  - `native_ntt_monitor_butterfly()`
  - `native_invntt_monitor_butterfly()`
  - `hook_mid_ntt_pre_butterfly()`
  - `hook_mid_invntt_pre_butterfly()`
  - `ntt_native_monitor_get_persistent_count()`
- `tfib_ref.c` (Strategy 1): Maintains `const int16_t tfib_zetas_ref[128]` for twiddle validation and in-place recovery.
- `tfib_meta.c` (Strategy 2): Evaluates `tfib_zetas_tag[128]` via an affine hash function.

---

## 4. Critical Defect & Divergence Findings

### Finding 1: Oracle Circularity (Self-Referential Validation)
In [`chatgpt/tfib_validity_audit_runner.c:21-31, 64-66`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_validity_audit_runner.c#L21-L31):
```c
int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
...
mlkem768_keypair(pk, sk);
mlkem768_enc(ct, ss_expected, pk);
compute_expected_rejection_key(ss_rej_expected, sk, ct);
```
- The "expected valid shared secret" `ss_expected` is generated by calling `mlkem768_enc` from `bin/obj/mlkem768_inst.o`—the **exact same compiled binary** being audited!
- The "expected rejection key" `ss_rej_expected` is computed using `mlkem768_shake256`, which is also linked directly from `bin/obj/mlkem768_inst.o`.
- **Defect Impact:** This is not an independent oracle; it is an internal self-consistency check. If `mlkem768_enc` or `mlkem768_shake256` in `mlkem768_inst.o` possesses an arithmetic flaw, memory leak, or correlated fault, the expected value silently mirrors the bug.

### Finding 2: Non-Cryptographic Randomness in Test Harness
In [`chatgpt/tfib_validity_audit_runner.c:16-19`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_validity_audit_runner.c#L16-L19):
```c
int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)rand();
    return 0;
}
```
- The test harness supplies randomness to ML-KEM-768 key generation and encapsulation by calling standard C library `rand()`.
- `rand()` is a linear congruential generator (LCG) with weak distributional entropy. While deterministic given `srand()`, it violates FIPS 203 assumptions regarding uniformly distributed random coins $d, z, m \in \{0,1\}^{256}$.
- **Defect Impact:** Potential clustering of polynomial coefficients and unrepresentative LWE error distributions.

### Finding 3: Test-Harness Coupling Inside Countermeasure Logic (Test-Only Code in Production Path)
Inspection of `tfib_meta.c` and `tfib_ref.c` revealed that the countermeasure routines directly read test-harness global variables:

1. **In `tfib_meta.c:94` and `tfib_meta.c:160`:**
   ```c
   /* In-place rollback */
   *r_j = u_saved;
   *r_j_len = v_saved;

   /* If operational twiddle is corrupted, metadata cannot repair it (no reference table) -> safe fail-stop */
   if (g_tfib_fault.locus == TFIB_FAULT_OP_TWIDDLE || g_tfib_fault.persistent) {
       g_tfib_meta_stats.persistent_fail_count++;
   } else {
       ...
   ```
   The verifier inspects `g_tfib_fault.locus`—a global variable belonging strictly to the fault injection harness! A real production monitor cannot query an attacker's fault locus to decide whether to fail-stop or recover.
   *Correct Logic:* The verifier should check `if (tag_mismatch)` (an operational finding), not `g_tfib_fault.locus`.

2. **In `tfib_ref.c:118` and `tfib_ref.c:201`:**
   ```c
   if (diff_retry == 0 && sum_retry == 0 && !g_tfib_fault.persistent) {
       g_tfib_ref_stats.recovered_count++;
   } else {
       g_tfib_ref_stats.persistent_fail_count++;
   }
   ```
   The verifier checks `&& !g_tfib_fault.persistent` inside its own recovery decision! In genuine hardware or software, persistent fault detection must be driven strictly by the algebraic failure of the post-repair check (`diff_retry != 0 || sum_retry != 0`), never by reading a test harness flag.

### Finding 4: Software Memory Colocation of Supposedly "Independent" Tables
Symbol inspection of the linked executable:
```text
00000001000168a0 (__TEXT,__const) non-external _mlk_zetas
0000000100016a60 (__TEXT,__const) external     _tfib_zetas_ref
0000000100016b60 (__TEXT,__const) external     _tfib_zetas_tag
```
- Both `_mlk_zetas` and `_tfib_zetas_ref` reside in the identical `__TEXT,__const` segment, separated by **448 bytes**.
- They reside in the exact same 4KB virtual memory page and identical L1 cache lines.
- **Linker Hazard:** Toolchains enabling Identical Code/Data Folding (`-Wl,--icf=all`) or LTO (`-flto`) will detect identical 256-byte constant payloads and collapse them into a single symbol, silently destroying software table redundancy.

### Finding 5: Benchmark Flaws (Fixed Order, Missing Warmup, Host Scheduling Jitter)
In [`chatgpt/tfib_benchmark_audit.c`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_benchmark_audit.c):
1. **Fixed Execution Order:** Always executes `BASELINE` (10,000) $\to$ `TFIB_REF` (10,000) $\to$ `TFIB_META` (10,000) $\to$ `ACTIVE_RECOVERY` (10,000). Later tests suffer from thermal throttling or background thread preemption.
2. **Missing Warmup in Active Recovery:** `ACTIVE_RECOVERY` executes 10,000 timed runs without any pre-measurement warm-up loops under the faulted state.
3. **Single Point Coordinate Bias:** The active recovery benchmark tests only `layer=1, b_idx=0, bit=1` rather than sampling randomized butterfly coordinates across all 7 layers.
4. **Extreme Tail Latency:** In `tfib_benchmark_raw.csv`, `TFIB-Meta` records 617 outliers $>1\,\text{ms}$ (max latency $5,552\,\mu\text{s}$) due to instruction-cache pressure interacting with host context switches.

---

## 5. Summary of Verified Observations, Suspected Defects, and Unresolved Questions

### 5.1 Verified Observations
1. **Twiddle Factor Blindness (Theorem 1) is Real:** When `zeta_val` is modified in `poly.c`, the baseline monitor invariant evaluates to 0 modulo 3329 because it consumes the faulted value in the check ($0/50$ detected locally).
2. **Outer FO Transform Acts as Failsafe:** Across all 900 trials, zero Silent Data Corruption (SDC) occurred. Downstream re-encryption caught $100\%$ of uncontained arithmetic errors.
3. **Ineffective Faults Exist in ML-KEM:** In $1/50$ baseline trials and $2/50$ simultaneous common-mode trials, small perturbations ($\Delta = 2$) on layer 1 were absorbed by the LWE decoding error tolerance ($\le q/4 = 832$).

### 5.2 Suspected Defects to Correct
1. **Oracle Circularity:** Replace the self-referential `mlkem768_enc` calls with a genuinely independent oracle (using the installed, independent `liboqs 0.16.0` library at `/opt/homebrew/opt/liboqs` and FIPS 203 Known Answer Tests).
2. **Test-Only Harness Coupling in Production Path:** Strip all occurrences of `g_tfib_fault.locus` and `g_tfib_fault.persistent` from `tfib_ref.c` and `tfib_meta.c`. Verifier decisions must depend purely on arithmetic invariants and tag comparison flags.
3. **Randomness Defect:** Replace `rand()` with standard deterministic FIPS 203 pseudorandom seed derivation (or `OQS_randombytes`).
4. **Benchmark Order & Warmup Bias:** Implement randomized/interleaved iteration blocks and uniform warmup policies in `phase11_benchmark_runner.c`.

### 5.3 Unresolved Questions for Subsequent Phases
1. Does `TFIB-Ref` maintain $100\%$ recovery when tested against an independent `liboqs` oracle under randomized FIPS 203 seeds?
2. Does `TFIB-Meta` fail-stop safely when `g_tfib_fault.locus` is removed from its C code and it relies solely on `tag_mismatch`?
3. When measured under interleaved, randomized benchmark rounds, what is the exact, true performance overhead of `TFIB-Ref` and `TFIB-Meta` on Apple Silicon?

---

## 6. Pre-Modification Readiness Checklist

- [x] Repository inspected; commit `55dd937` recorded; working tree preserved.
- [x] All 6 `chatgpt/` audit files inspected, verified, and cross-referenced.
- [x] Production code path traced from `poly.c` to `kem.c`.
- [x] Source of independent oracle identified (`liboqs 0.16.0` available at `/opt/homebrew/opt/liboqs/include/oqs` and `/opt/homebrew/opt/liboqs/lib/liboqs.dylib`, plus `references/test_vectors/mlkem_expected_kat.h`).
- [x] Test-only harness couplings in `tfib_ref.c` and `tfib_meta.c` isolated.
- [x] Document saved to [`tfib_experiments/phase11_initial_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_initial_audit.md).

**STATUS: Phase 0 Complete. Awaiting user review of initial audit before proceeding to Phase 1 (Independent Oracle Implementation).**
