# Countermeasure Source-Level Implementation Audit

**Auditor:** Skeptical Cryptographic Security Researcher, Fault-Tolerance Engineer & Experimental Auditor  
**Audit Target:** Countermeasure Implementations (Variants A, B, C, D) in [`adversarial_audit/test_harness/countermeasure_eval.c`](file:///Users/dhairyajain/Desktop/pqc%20research/adversarial_audit/test_harness/countermeasure_eval.c) and Core Monitors in [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c)  
**Date:** 2026-10-02  

---

## 1. Deep Audit of Variant B: Independent Twiddle Validation

### 1.1 Storage Locus & Independence of Trusted Constants
- **Storage Location:**
  In [`adversarial_audit/test_harness/countermeasure_eval.c:39-52`](file:///Users/dhairyajain/Desktop/pqc%20research/adversarial_audit/test_harness/countermeasure_eval.c#L39-L52), trusted twiddle factors are stored as a second static constant array:
  ```c
  static const int16_t audit_trusted_zetas[128] = { -1044, -758, -359, ... };
  ```
  In production source [`mlkem_fault_hooks.c:555-568`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L555-L568), the unreferenced `g_trusted_zetas[128]` resides in `.rodata`.
- **Independence Evaluation:**
  `audit_trusted_zetas` is **NOT** independently generated at runtime or cryptographically signed; it is an identical static duplicate of the pre-computed array in `zetas.inc`.

### 1.2 Compiler Optimization & Table Folding Vulnerability
- **Inspection Finding:**
  Both `mlk_zetas[128]` and `audit_trusted_zetas[128]` contain identical data with identical types (`const int16_t[128]`).
- **Optimization Risk (Identical Code Folding / Constant Merging):**
  Under optimizing compilers (LLVM / Clang `-O3`) with Link-Time Optimization (`-flto`) or within the same translation unit, identical constant arrays are merged into a single read-only address in the `.rodata` section.
- **Physical Consequence:** If the compiler merges the tables, any physical Single-Event Upset (SEU) striking that memory address corrupts **both** the operational constant and the reference constant simultaneously.
- **Common-Mode Failure Verification:**
  Our controlled test in [`validate_countermeasures_deep.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase2_independent_validation/harness/validate_countermeasures_deep.c) proved that when both tables share corrupted physical state, the local cross-check fails with **100.0% evasion rate** ($100/100$ evasions).

### 1.3 Validation Temporal Locus
- In the initial test harness, validation occurred dynamically inside the butterfly loop.
- **Vulnerability:** Validating during use exposes the check to loop-level instruction-skipping faults.
- **Correct Placement:** Constant table validation must occur as an immutable pre-flight check (e.g. 32-bit CRC or SHA-256 digest verification over the complete 256-byte table) prior to launching polynomial arithmetic.

---

## 2. Deep Audit of Variant C: Diverse Recovery Verification

### 2.1 Recovery Path Dependency Analysis
In [`mlkem_fault_hooks.c:638-655`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L638-L655), the recovery path executes:
```c
*r_j = u_saved;
*r_j_len = v_saved;
int16_t t_retry = monitor_fqmul(v_saved, zeta);
int16_t u_new = (int16_t)(u_saved + t_retry);
int16_t v_new = (int16_t)(u_saved - t_retry);
```

### 2.2 Independence Audit
- **Dependency on Saved Operands:** The recomputation strictly relies on `u_saved` and `v_saved`. If an SEU strikes the stack frame where `u_saved` is held, the recomputation operates on corrupted data.
- **Dependency on Operational Twiddle:** `monitor_fqmul(v_saved, zeta)` uses the exact same `zeta` parameter. If `zeta` was corrupted in the caller, retry repeats the corrupted multiplication.
- **Verification Independence:** In Baseline A, $\text{sum\_retry} \equiv 0$ and $\text{diff\_retry} \equiv 0$ are mathematical tautologies. In Variant C, introducing an interleaved parity check over $(u_{\text{saved}}, v_{\text{saved}})$ successfully caught corrupted snapshot states and suppressed the false recovery from $100\%$ down to $0.0\%$.

---

## 3. Deep Audit of Variant D: Fail-Stop Architecture

### 3.1 Definition of Fail-Stop
Under Variant D, any invariant violation, twiddle discrepancy, or decapsulation anomaly immediately terminates execution, suppresses candidate secret key release, and outputs the deterministic rejection key $K_{\text{rej}} = J(z \parallel c)$ with status code `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`).

### 3.2 State Corruption and Predicate Integrity
- **Vulnerability Analyzed:** Can a single-bit fault in the `fail` flag bypass the fail-stop decision?
- **Source Inspection:** In [`kem.c:477-504`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L477-L504), the reverse dual-rail comparison evaluates:
  ```c
  uint8_t fail_chk = 0;
  for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
    fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
  }
  fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);
  if (fail != fail_chk) fail = 0xFF;
  ```
- **Audit Finding:** Single-bit flips on `fail` are caught by the dual-rail check ($0/8$ bypasses, $0.0\%$). An attacker would need to flip corresponding bits in both `fail` and `fail_chk` simultaneously.

### 3.3 Timing Analysis: Why Low Variance Does Not Equal Constant-Time
- **Empirical Measurement:**
  - Clean Baseline: $\text{Median} = 106.00\,\mu\text{s}$, $\text{StdDev} = 1.88\,\mu\text{s}$
  - Monitored Fail-Stop: $\text{Median} = 153.00\,\mu\text{s}$, $\text{StdDev} = 3.33\,\mu\text{s}$
- **Critical Finding:** While each mode has low standard deviation ($\sigma \approx 1.9\,\mu\text{s}$ to $3.3\,\mu\text{s}$), the **execution delta between clean execution and monitored fail-stop is $+47.00\,\mu\text{s}$ ($+44.3\%$)**!
- **Auditor Warning:** Low intra-mode variance must **never** be conflated with constant-time security. If an adversary or channel error triggers fail-stop, the $47\,\mu\text{s}$ divergence is an observable timing oracle on network links or shared system buses. Constant-time fail-stop requires executing dummy re-encryption cycles to equalize the timeline.
