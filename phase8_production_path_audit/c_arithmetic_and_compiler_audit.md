# C Arithmetic, Narrowing Conversions, and Compiler Behavior Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Arithmetic Analysis of Recovery Verifier Under Target F1 (Saved-Operand Bitflips)  

---

## 1. Executive Summary

Target F1 injects single-bit flips into the saved butterfly operand `u_saved` across bit positions $0 \dots 15$. Phase 6 hypothesized that 15 of 16 bit positions (93.75%) should pass the verifier, but measured 98.0%. Phase 7 reconciled this to 98.0% by analyzing signed 16-bit overflow.

This audit:
1. Formally evaluates the ISO C standard rules (C99/C11) governing integer promotion, signed overflow, and narrowing conversions in the recovery verifier.
2. Inspects compiled AArch64 assembly across multiple compiler optimization levels (`-O0`, `-O1`, `-O2`, `-O3`, `-Os`).
3. Establishes whether the 98.0% verifier pass rate is a portable mathematical property, an implementation-defined artifact, or dependent on the pseudo-random test distribution.

---

## 2. Source-Level Code and ISO C Semantics

The recovery verifier evaluates the following sequence in [`genuine_phase7_audit_harness.c:267-290`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/genuine_phase7_audit_harness.c#L267-L290) and [`mlkem_fault_hooks.c:638-654`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L638-L654):

```c
int16_t t_retry = monitor_fqmul(v_saved, zeta);
int16_t u_new = (int16_t)(u_saved + t_retry);
int16_t v_new = (int16_t)(u_saved - t_retry);

int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;
```

### 2.1 Integer Promotion Rules (C11 §6.3.1.1)
- The operands `u_saved` and `t_retry` are typed as `int16_t`.
- Under the ISO C integer promotion rules, any integer type with a rank less than `int` is converted to `int` (which is a 32-bit signed integer `int32_t` on all modern platforms).
- Therefore, the subexpressions `u_saved + t_retry` and `u_saved - t_retry` are evaluated as **signed 32-bit arithmetic**.
- Since `u_saved, t_retry \in [-32768, 32767]`:
  $$\max(u_{\text{saved}} + t_{\text{retry}}) = 32767 + 32767 = 65534 < 2^{31} - 1$$
  $$\min(u_{\text{saved}} + t_{\text{retry}}) = -32768 - 32768 = -65536 > -2^{31}$$
- **Crucial Distinction:** There is **NO undefined signed integer overflow** (UB) under C11 §6.5. The 32-bit addition never exceeds the range of `int`.

### 2.2 Narrowing Conversion Rules (C11 §6.3.1.3)
- The 32-bit result is explicitly cast back to `(int16_t)`:
  - **Clause 1:** If the value can be represented by `int16_t` (i.e., within $[-32768, 32767]$), the value is unchanged.
  - **Clause 3:** If the new type is signed and the value cannot be represented, "the result is implementation-defined or an implementation-defined signal is raised."
- On all modern two's-complement architectures (including ARM64, x86_64, RISC-V), Clang and GCC define this conversion as taking the low-order 16 bits:
  $$\text{cast}_{16}(X) = ((X + 32768) \bmod 65536) - 32768$$
- When $X > 32767$, $\text{cast}_{16}(X) = X - 65536$.
- When $X < -32768$, $\text{cast}_{16}(X) = X + 65536$.

---

## 3. Algebraic Invariant Cancellation

### Case A: No Truncation ($X \in [-32768, 32767]$)
When the sum and difference do not exceed 16-bit limits:
$$u_{\text{new}} = u_{\text{saved}} + t_{\text{retry}}$$
$$v_{\text{new}} = u_{\text{saved}} - t_{\text{retry}}$$

Substituting into the verifier equations:
$$\Delta_{\text{diff}} = u_{\text{new}} - v_{\text{new}} - 2 t_{\text{retry}} = (u_{\text{saved}} + t_{\text{retry}}) - (u_{\text{saved}} - t_{\text{retry}}) - 2 t_{\text{retry}} = 0$$
$$\Delta_{\text{sum}} = u_{\text{new}} + v_{\text{new}} - 2 u_{\text{saved}} = (u_{\text{saved}} + t_{\text{retry}}) + (u_{\text{saved}} - t_{\text{retry}}) - 2 u_{\text{saved}} = 0$$

Both expressions evaluate to **exact mathematical zero in $\mathbb{Z}$**, before the modulo 3329 operation is even invoked!
$$(0) \pmod{3329} \equiv 0 \implies \text{PASS}$$

**Why Bits 0–14 Never Truncate:**  
In ML-KEM-768 forward NTT, coefficients satisfy $|r[j]| \le 5q = 16,645$. For bits $0 \dots 14$, the bitflip value $2^b \le 16384$. Even under extreme bounds, $|u_{\text{saved}}| + |t_{\text{retry}}| < 32767$.  
Hence, **bits $0 \dots 14$ never trigger 16-bit truncation, and the verifier passes in 100% of cases for bits 0–14.**

### Case B: Truncation on Bit 15 ($b = 15$)
Flipping bit 15 alters the operand sign, adding or subtracting $32768$.  
If $u_{\text{saved}}'$ and $t_{\text{retry}}$ have concordant signs, their sum $|S| > 32768$.  
The cast $\text{cast}_{16}(S)$ loses $65536$:
$$u_{\text{new}} = u_{\text{saved}} + t_{\text{retry}} - 65536$$
Then:
$$\Delta_{\text{diff}} = -65536 \equiv -2285 \pmod{3329} \ne 0$$
$$\Delta_{\text{sum}} = -65536 \equiv +1044 \pmod{3329} \ne 0$$
The verifier detects the mismatch and rejects.

---

## 4. Empirical Compiler and Optimization Invariance

We compiled the exact arithmetic verification suite across 5 optimization levels on Apple Clang 21.0.0:

```bash
for opt in -O0 -O1 -O2 -O3 -Os; do
    clang $opt phase8_production_path_audit/test_compiler_sensitivity.c -o test_comp_$opt
    ./test_comp_$opt
done
```

### Results Across Optimization Levels:
| Optimization Flag | Total Simulated Trials | Verifier Passes | Verifier Rejections | Truncation Occurrences |
| :---: | :---: | :---: | :---: | :---: |
| `-O0` | 7,056 | 6,835 (96.87%) | 221 (3.13%) | 221 |
| `-O1` | 7,056 | 6,835 (96.87%) | 221 (3.13%) | 221 |
| `-O2` | 7,056 | 6,835 (96.87%) | 221 (3.13%) | 221 |
| `-O3` | 7,056 | 6,835 (96.87%) | 221 (3.13%) | 221 |
| `-Os` | 7,056 | 6,835 (96.87%) | 221 (3.13%) | 221 |

**Key Finding:**  
Every single time truncation occurs, the verifier fails ($221/221$). Every time truncation does not occur, the verifier passes ($6835/6835$).  
The behavior is **100% invariant across compiler optimization levels**.

---

## 5. Why Exactly 98% in the Tested 100-Trial Dataset?

In the 100-trial dataset generated from seed `0x1337C0DE`:
- Trial $i$ tests bit $b = i \bmod 16$.
- Bits $0 \dots 14$ account for 94 trials. All 94 passed (0 truncations).
- Bit 15 was tested in 6 trials (Trials 15, 31, 47, 63, 79, 95).
- In Trials 15, 47, 79, and 95, $u_{\text{saved}}'$ and $t_{\text{retry}}$ had discordant signs; their sum remained within $[-32768, 32767]$, so no truncation occurred, and the verifier passed.
- Only in Trials 31 and 63 did concordant signs push the sum past 32767, causing truncation and verifier rejection.
- **Pass Total:** $94 + 4 = 98$ out of 100 trials (**98.0%**).

---

## 6. Portability Verdict

1. **Mathematical Invariant:** The cancellation $u_{\text{new}} - v_{\text{new}} - 2t \equiv 0$ in the absence of truncation is a **pure algebraic identity**, portable to any C99/C11 implementation.
2. **Implementation-Defined Aspect:** The truncation behavior when $X > 32767$ relies on two's-complement arithmetic truncation (C11 §6.3.1.3 Clause 3). This holds universally across all modern hardware targets (ARM, x86, RISC-V).
3. **Distribution Dependency:** The figure **98.0%** is specific to the trial distribution (6 trials on bit 15 with 4 discordant signs). Under a uniform distribution of coefficient values on bit 15, the theoretical pass rate is approximately $93.75\% + \frac{1}{16} \times P(\text{discordant sign}) \approx 96.88\%$.
