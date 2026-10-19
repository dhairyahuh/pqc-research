# Mathematical and Implementation Audit

**Author:** Independent Cryptographic Auditor & Implementation Research Team  
**Evaluation Scope:** Mathematical Invariants, Twiddle Arithmetic, Input Latching, and Rollback Integrity in ML-KEM-768  
**Audit Target:** [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) and [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c)  

---

## 1. Mathematical Analysis of the Shared Twiddle Factor Verification

### 1.1 Butterfly Definitions in ML-KEM
In ML-KEM-768, polynomial arithmetic operates in the quotient ring $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$ with prime modulus $q = 3329$. The ring supports a fast Number Theoretic Transform (NTT) because $\mathbb{Z}_q$ contains primitive 256th roots of unity.

1. **Forward Cooley-Tukey (CT) Butterfly:**
   Given inputs $u, v \in \mathbb{Z}_q$ and twiddle factor $\zeta \in \mathbb{Z}_q$:
   $$t = v \cdot \zeta \pmod{q}$$
   $$u' = u + t \pmod{q}$$
   $$v' = u - t \pmod{q}$$

2. **Inverse Gentleman-Sande (GS) Butterfly:**
   Given inputs $u, v \in \mathbb{Z}_q$ and twiddle factor $\zeta \in \mathbb{Z}_q$:
   $$u' = u + v \pmod{q}$$
   $$v' = (v - u) \cdot \zeta \pmod{q}$$

### 1.2 The Local Invariant Formulations
The in-tree monitoring architecture in `mlkem_fault_hooks.c` defines local algebraic invariants to verify butterfly integrity:

- **Forward CT Monitor Invariants** ([`mlkem_fault_hooks.c:623-624`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L623-L624)):
  $$\text{diff\_c} = (u' - v' - 2 t_{\text{check}}) \pmod{q}$$
  $$\text{sum\_c} = (u' + v' - 2 u_{\text{saved}}) \pmod{q}$$
  Where $t_{\text{check}} = \text{monitor\_fqmul}(v_{\text{saved}}, \zeta)$ in `NTT_NATIVE_MONITOR_RECOMPUTED_T` mode.

- **Inverse GS Monitor Invariants** ([`mlkem_fault_hooks.c:819-826`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L819-L826)):
  $$\text{sum\_c} = (u' - (u_{\text{saved}} + v_{\text{saved}})) \pmod{q}$$
  $$\text{diff\_c} = (v' - \text{monitor\_fqmul}(v_{\text{saved}} - u_{\text{saved}}, \zeta)) \pmod{q}$$

### 1.3 Exact Invariant Evaluation Under Corrupted Twiddle $\zeta^*$
Suppose a physical fault perturbs the operational twiddle factor $\zeta \to \zeta^* = \zeta + \Delta\zeta$.
Because the butterfly caller in [`poly.c:408`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L408) and [`poly.c:589`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L589) passes the single variable `zeta_val` to both the arithmetic multiplier and the monitor function:

1. **Forward CT Monitor with Corrupted Twiddle:**
   - Butterfly computes: $t^* = v \cdot \zeta^*$, $u^* = u + t^*$, $v^* = u - t^*$.
   - Monitor recomputes: $t_{\text{check}} = v_{\text{saved}} \cdot \zeta^* = t^*$.
   - Evaluating $\text{diff\_c}$:
     $$\text{diff\_c} = (u^* - v^* - 2 t_{\text{check}}) = ((u + t^*) - (u - t^*) - 2 t^*) = 2 t^* - 2 t^* \equiv 0 \pmod{q}$$
   - Evaluating $\text{sum\_c}$:
     $$\text{sum\_c} = (u^* + v^* - 2 u_{\text{saved}}) = ((u + t^*) + (u - t^*) - 2 u) = 2 u - 2 u \equiv 0 \pmod{q}$$

2. **Inverse GS Monitor with Corrupted Twiddle:**
   - Butterfly computes: $u' = u + v$, $v^* = (v - u) \cdot \zeta^*$.
   - Monitor checks adder: $\text{sum\_c} = u' - (u + v) = (u + v) - (u + v) \equiv 0 \pmod{q}$.
   - Monitor checks multiplier: $\text{diff\_c} = v^* - (v_{\text{saved}} - u_{\text{saved}}) \cdot \zeta^* = (v - u)\zeta^* - (v - u)\zeta^* \equiv 0 \pmod{q}$.

**Theorem 1 (Universal Invariant Blindness to Shared Constants):**
*If the invariant verification routine evaluates using the same twiddle factor operand $\zeta^*$ as the operational butterfly, all local invariant equations evaluate to zero modulo $q$ regardless of $\Delta\zeta$. The detection probability of the local monitor under twiddle corruption is identically zero ($P_{\text{detect}} = 0.0$).*

### 1.4 Conditions Governing Downstream Manifestation
Under what conditions does $\zeta \to \zeta^*$ manifest in decapsulation?

1. **Passes Local Invariant:** Always ($100\%$ probability).
2. **Perturbs Polynomial Arithmetic:**
   $$\Delta t = \text{fqmul}(v, \zeta^*) - \text{fqmul}(v, \zeta) \pmod{q}$$
   The output polynomial is modified if and only if:
   $$v \not\equiv 0 \pmod{q} \quad \text{and} \quad \zeta^* \not\equiv \zeta \pmod{q}$$
   If $v \equiv 0 \pmod{q}$, $\text{fqmul}(0, \zeta^*) = 0 = \text{fqmul}(0, \zeta)$, producing zero output perturbation.
3. **Caught by Fujisaki-Okamoto Check:**
   In ML-KEM decapsulation, the Fujisaki-Okamoto transform re-encrypts the decrypted candidate message $m'$ to obtain $(c_1', c_2')$ and compares:
   $$\text{fail} = \text{mlk\_ct\_memcmp}(ct, tmp, 1088)$$
   The fault is detected and safely rejected if and only if at least one compressed byte differs:
   $$(c_1', c_2') \neq (c_1, c_2)$$
4. **Produces Equivalent Output (Benign Equivalence):**
   Occurs when the error vector in ciphertext coefficients $\mathbf{e}_{\text{ct}} = (c_1', c_2') - (c_1, c_2)$ vanishes under lossy compression:
   $$\text{Compress}_{10}(u + \Delta u) = \text{Compress}_{10}(u) \quad \text{and} \quad \text{Compress}_{4}(v + \Delta v) = \text{Compress}_{4}(v)$$
   Because $\text{Compress}_{d}(x) = \lfloor (x \cdot 2^d + 1664) / 3329 \rfloor \pmod{2^d}$, coefficient deviations $|\Delta u| < \frac{3329}{2 \cdot 1024} \approx 1.62$ can be absorbed by rounding boundaries, yielding bit-identical ciphertexts.

---

## 2. Mathematical Audit of Pre-Latch vs. Post-Latch Input Faults

### 2.1 Trace of Execution Sequences
Let the input array elements at indices $j$ and $j+\text{len}$ be $r[j]$ and $r[j+\text{len}]$.

#### Execution Order in Current Source ([`poly.c:556-589`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L556-L589)):
```text
1. u_saved = r[j];                    // Line 557: Latch u
2. v_saved = r[j + len];              // Line 558: Latch v
3. hook_mid_invntt_pre_butterfly(...) // Line 564: Test Hook Injected Here
4. r[j] = Barrett(r[j] + r[j+len])   // Line 567: Butterfly Adder
5. diff = r[j+len] - r[j]             // Line 568: Difference
6. r[j+len] = fqmul(diff, zeta)       // Line 575: Butterfly Multiplier
7. native_invntt_monitor_butterfly    // Line 589: Invariant Evaluation
```

### 2.2 Formal Comparison of Fault Models

#### Case A: Post-Latch Mutation (What the current hook executes)
- At step 1: $u_{\text{saved}} = u$.
- At step 3: Hook mutates $r[j] \to u^* = u + \Delta$.
- At step 4: Butterfly computes $u' = u^* + v = u + v + \Delta$.
- At step 7: Monitor evaluates:
  $$\text{sum\_c} = u' - (u_{\text{saved}} + v_{\text{saved}}) = (u + v + \Delta) - (u + v) = \Delta \not\equiv 0 \pmod{q}$$
- **Result:** Monitor detects the mismatch ($100\%$ detection). Rollback restores $r[j] = u_{\text{saved}} = u$, successfully recovering.

#### Case B: Pre-Latch Memory Fault (Real Physical SEU in SRAM/Cache)
- An upset strikes memory before step 1: $r[j]$ in memory is already $u^* = u + \Delta$.
- At step 1: $u_{\text{saved}} = r[j] = u^*$.
- At step 3: No hook mutation.
- At step 4: Butterfly computes $u' = u^* + v$.
- At step 5: Difference is $v - u^*$.
- At step 6: $v' = (v - u^*) \cdot \zeta$.
- At step 7: Monitor evaluates:
  $$\text{sum\_c} = u' - (u_{\text{saved}} + v_{\text{saved}}) = (u^* + v) - (u^* + v) \equiv 0 \pmod{q}$$
  $$\text{diff\_c} = v' - (v_{\text{saved}} - u_{\text{saved}})\zeta = (v - u^*)\zeta - (v - u^*)\zeta \equiv 0 \pmod{q}$$
- **Result:** Monitor is 100% blinded ($0\%$ detection). The corrupted polynomial propagates without rollback.

**Theorem 2 (Shadow Register Latching Blindness):**
*An in-tree algorithm-based fault-tolerance checker that initializes its shadow snapshot registers by copying directly from unverified input memory is strictly incapable of detecting pre-existing memory corruptions. It detects only faults injected into ALU registers strictly between snapshot latching and invariant evaluation.*

---

## 3. Mathematical Audit of Post-Retry Verification

### 3.1 Source Implementation of Retry Verification
In [`mlkem_fault_hooks.c:638-656`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L638-L656), upon detecting a mismatch, the monitor executes:

```c
/* In-place rollback using saved pre-butterfly operands */
*r_j = u_saved;
*r_j_len = v_saved;

int16_t t_retry = monitor_fqmul(v_saved, zeta);
int16_t u_new = (int16_t)(u_saved + t_retry);
int16_t v_new = (int16_t)(u_saved - t_retry);

*r_j = u_new;
*r_j_len = v_new;

int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;

if (diff_retry == 0 && sum_retry == 0) {
    g_ntt_native_monitor.recovered_count++;
}
```

### 3.2 Formal Algebraic Proof of Tautology
Let $u_{\text{saved}}, v_{\text{saved}}, \zeta \in \mathbb{Z}_q$ be arbitrary ring elements (including corrupted values).
The retry logic defines:
$$t_{\text{retry}} = \text{fqmul}(v_{\text{saved}}, \zeta)$$
$$u_{\text{new}} = u_{\text{saved}} + t_{\text{retry}}$$
$$v_{\text{new}} = u_{\text{saved}} - t_{\text{retry}}$$

Now compute $\text{diff\_retry}$ and $\text{sum\_retry}$:
1. **Difference Equation:**
   $$\text{diff\_retry} = u_{\text{new}} - v_{\text{new}} - 2 t_{\text{retry}}$$
   $$\text{diff\_retry} = (u_{\text{saved}} + t_{\text{retry}}) - (u_{\text{saved}} - t_{\text{retry}}) - 2 t_{\text{retry}}$$
   $$\text{diff\_retry} = 2 t_{\text{retry}} - 2 t_{\text{retry}} \equiv 0 \pmod{q}$$

2. **Sum Equation:**
   $$\text{sum\_retry} = u_{\text{new}} + v_{\text{new}} - 2 u_{\text{saved}}$$
   $$\text{sum\_retry} = (u_{\text{saved}} + t_{\text{retry}}) + (u_{\text{saved}} - t_{\text{retry}}) - 2 u_{\text{saved}}$$
   $$\text{sum\_retry} = 2 u_{\text{saved}} - 2 u_{\text{saved}} \equiv 0 \pmod{q}$$

**Theorem 3 (Retry Verification Tautology):**
*The expressions $\text{diff\_retry}$ and $\text{sum\_retry}$ are polynomial identities in the ring $\mathbb{Z}_q$. They evaluate to zero for all possible choices of $u_{\text{saved}}$, $v_{\text{saved}}$, and $\zeta$, without constraint. Consequently, the retry check does not verify the mathematical correctness of the recovered state; it merely verifies that the CPU executed immediate integer addition and subtraction without an internal arithmetic fault.*

### 3.3 Vulnerability Surface of the Rollback State

| Variable / State Element | Can it be Corrupted? | Does Retry Verification Detect It? | Downstream Consequence |
| :--- | :---: | :---: | :--- |
| **Saved Operand $u_{\text{saved}}$** | Yes (Stack/Register SEU) | **No** ($\text{sum\_retry} \equiv 0$) | Corrupted polynomial committed to array; fails FO check later. |
| **Saved Operand $v_{\text{saved}}$** | Yes (Stack/Register SEU) | **No** ($\text{diff\_retry} \equiv 0$) | Corrupted polynomial committed to array; fails FO check later. |
| **Twiddle Factor $\zeta$** | Yes (Table or Reg SEU) | **No** (Identity holds for any $\zeta$) | Corrupted polynomial committed to array; fails FO check later. |
| **Retry Multiplier $t_{\text{retry}}$** | Yes (ALU Transient) | **No** ($2t - 2t \equiv 0$) | Tautology masks multiplier glitch unless hook specifically targets $u_{\text{new}}$. |
| **State Between Verify & Commit** | Yes (Memory Bus SEU) | **No** (Check occurs prior to commit) | Corrupted coefficients written to `*r_j`, `*r_j_len`. |
| **Recovery Counter `recovered_count`**| Yes (Counter SEU) | N/A | Corrupted reporting metrics without cryptographic failure. |

**Audit Conclusion:** The retry mechanism does not constitute an independent verification barrier. It provides successful recovery only under the narrow hypothesis that the transient upset was confined strictly to the primary ALU execution and that all snapshot storage remains uncorrupted.
