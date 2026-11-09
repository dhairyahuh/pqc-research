# TFIB Failure Modes, Blind Spots, and Architectural Boundary Analysis

**Document:** Independent Experimental Audit Deliverable — Deep Failure Mode Catalog  
**Target:** ML-KEM-768 Twiddle Factor Integrity Binding (`TFIB-Ref` & `TFIB-Meta`)  
**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  

---

## 1. Failure Case 1: Ineffective Faults via LWE Error-Tolerance Slack

### Empirical Evidence
In both the Baseline suite (`OP_TWIDDLE_TRANSIENT`, Trial 3) and the TFIB-Ref suite (`SIMULTANEOUS_COMMON_MODE`, Trials 3 & 45), single-bit twiddle perturbations were activated during decapsulation, yet the decapsulated shared secret matched the genuine oracle key ($K_{\text{out}} == K_{\text{valid}}$), and downstream Fujisaki-Okamoto (FO) re-encryption did not reject.

- **Observed Behavior:** Fault activated $\to$ Monitor detected 0 mismatches $\to$ Status `0x5A5A5A5A` (Success) $\to$ Decapsulated key $K_{\text{out}} == K_{\text{valid}}$.
- **Root Cause:** In ML-KEM-768, message decoding performs a threshold decision on noisy ring elements:
  $$m_i = \left\lfloor \frac{2}{q} \cdot c_i + \frac{1}{2} \right\rceil \pmod 2$$
  The decoding error tolerance allows coefficients to deviate by up to $\left\lfloor \frac{q}{4} \right\rfloor = 832$ without altering the decoded message bit $m_i \in \{0, 1\}$.
  
  When a twiddle factor $\zeta$ is perturbed at early forward NTT stages (e.g., layer 1, butterfly 0, bit 1: changing $-758$ to $-760$, a delta of $\Delta = 2$), the resulting arithmetic disturbance on downstream polynomial coefficients remains small:
  $$\Delta \cdot v < \frac{q}{4}$$
  Consequently, `mlk_poly_tomsg` rounds the perturbed polynomial back to the identical 32-byte message $m$. Re-encryption using $m$ reproduces the exact ciphertext $ct$, `mlk_ct_memcmp` evaluates to 0 (match), and the decapsulation engine outputs $K_{\text{valid}}$.

### Cryptographic Classification
This is **not** Silent Data Corruption (SDC), nor is it a false negative of the verifier. It is an **ineffective fault**: the perturbation was completely absorbed by the algebraic error gap of the Learning-With-Errors problem. The cryptographic boundary remained intact because the genuine shared secret was legally recovered.

---

## 2. Failure Case 2: Simultaneous Common-Mode Twiddle Corruption

### Empirical Evidence
In Suite 9 (`SIMULTANEOUS_COMMON_MODE`), both operational twiddle $\zeta_{\text{op}}$ and reference twiddle $\zeta_{\text{ref}}$ experienced identical single-bit flips prior to verification across 50 trials.

- **Local Monitor Outcome:** `0/50` detected locally ($0.0\%$ detection rate).
- **Rollback / Recovery Outcome:** `0/50` recovered locally ($0.0\%$ recovery rate).
- **Downstream FO Outcome:** `48/50` rejected by outer FO re-encryption (`0xA5A5A5A5`), `2/50` absorbed by LWE error tolerance.
- **SDC Rate:** `0.0%` (0/50).

### Mathematical Mechanism of Failure
`TFIB-Ref` implements two sequential verification steps in [`tfib_ref.c:64-73`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L64-L73):
1. **Direct Equality Check:**
   $$\text{twiddle\_mismatch} = (\zeta_{\text{op}} \ne \zeta_{\text{ref}})$$
   When both are perturbed by mask $M = 2^b$:
   $$\zeta_{\text{op}} \oplus M == \zeta_{\text{ref}} \oplus M \implies \text{twiddle\_mismatch} = \text{false}$$
2. **Recomputed Arithmetic Invariant:**
   $$t_{\text{check}} = \text{fqmul}(v_{\text{saved}}, \zeta_{\text{ref}} \oplus M)$$
   Since the live operational butterfly also computed $t_{\text{used}} = \text{fqmul}(v_{\text{saved}}, \zeta_{\text{op}} \oplus M)$, we have $t_{\text{used}} \equiv t_{\text{check}} \pmod q$.
   $$\Delta_{\text{diff}} = (r_j - r_{j+\text{len}}) - 2 \cdot t_{\text{check}} = 2 \cdot t_{\text{used}} - 2 \cdot t_{\text{check}} \equiv 0 \pmod q$$
   $$\Delta_{\text{sum}} = (r_j + r_{j+\text{len}}) - 2 \cdot u_{\text{saved}} \equiv 0 \pmod q$$

Both checks pass unconditionally. The local monitor experiences **complete blindness**. 

### Architectural Boundary
This failure mode proves that software-level dual-table duplication **cannot protect against shared-source or common-mode physical faults** (such as bus transient faults, clock glitching on memory read cycles, or cache-line level corruptions). The only defense preserving integrity in this regime is the downstream Fujisaki-Okamoto re-encryption check.

---

## 3. Failure Case 3: Linker Deduplication & Physical Colocation Hazard

### Empirical Evidence
Binary symbol inspection of `scratch_check_addr` and `tfib_experiments/tfib_experiment_runner` reveals:
```text
00000001000168a0 (__TEXT,__const) non-external _mlk_zetas
0000000100016a60 (__TEXT,__const) external     _tfib_zetas_ref
0000000100016b60 (__TEXT,__const) external     _tfib_zetas_tag
```
- Offset between `_mlk_zetas` and `_tfib_zetas_ref`: $\Delta = 0x1C0 = 448$ bytes.
- Offset between `_tfib_zetas_ref` and `_tfib_zetas_tag`: $\Delta = 0x100 = 256$ bytes.

### Critical Vulnerabilities:
1. **Identical Code / Data Folding (ICF):**
   `_mlk_zetas` and `_tfib_zetas_ref` are byte-for-byte identical arrays of 128 `int16_t` constants. While the current build did not enable aggressive ICF, modern production toolchains using LLVM/Clang with `-Wl,--icf=all` or `-flto` (Link-Time Optimization) automatically identify duplicate read-only data blocks and collapse them into a single memory symbol.
   If ICF is enabled, `&tfib_zetas_ref == &mlk_zetas`. The two tables physically merge into one, completely eliminating software redundancy without emitting any compiler warning!
2. **Silicon Micro-Architectural Colocation:**
   A separation of 448 bytes places both tables in the same 4KB virtual page, and often in adjacent cache lines of the CPU L1 data cache. In embedded or radiation environments, a single ionizing particle track (Single-Event Functional Interrupt or Multi-Cell Upset) or a localized laser fault with a spot size of $>10\,\mu\text{m}$ spans multiple adjacent cache lines, corrupting both tables simultaneously.

---

## 4. Failure Case 4: Non-Cryptographic Metadata Collision Boundary

### Tag Construction
In [`tfib_meta.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_meta.h#L13-L17):
$$\text{tag}(\zeta, k) = ((\zeta \times 31337) \oplus (k \times 1337) \oplus \text{0xA55A}) \pmod{2^{16}}$$

### Mathematical Robustness & Limitations:
1. **Single-Fault Collision Resistance:**
   Since $31337$ is coprime to $2^{16}$ ($\gcd(31337, 65536) = 1$), multiplication by $31337 \pmod{2^{16}}$ is a strict bijective permutation over $\mathbb{Z}_{2^{16}}$.
   Therefore, for any fixed index $k$, no two distinct 16-bit integers $\zeta \ne \zeta'$ can ever yield the same tag:
   $$\forall \zeta \ne \zeta', \quad \text{tag}(\zeta, k) \ne \text{tag}(\zeta', k)$$
   Single-point corruption of $\zeta$ is guaranteed to trigger a tag mismatch.
2. **Targeted Double-Fault Collision:**
   Because this is an affine hash and not a cryptographically secure message authentication code (MAC), an active adversary with precise multi-fault injection capability can perturb $\zeta$ by $\Delta \zeta$ and simultaneously perturb the stored tag $\text{tag}[k]$ by:
   $$\Delta \text{tag} = (\Delta \zeta \times 31337) \pmod{2^{16}}$$
   This completely cancels the discrepancy, allowing arbitrary twiddle corruption to commit without detection.

---

## 5. Failure Case 5: Latency and Tail-Outlier Penalties

### Benchmark Discrepancy Analysis
Under background scheduling load, `TFIB-Meta` and active recovery demonstrated severe latency inflation:
- `BASELINE`: Median $145.96\,\mu\text{s}$, $114$ outliers $> 1\,\text{ms}$.
- `TFIB-REF`: Median $173.17\,\mu\text{s}$ ($+18.6\%$), $105$ outliers $> 1\,\text{ms}$.
- `TFIB-META`: Median $260.04\,\mu\text{s}$ ($+78.2\%$), $617$ outliers $> 1\,\text{ms}$.
- `TFIB-REF (ACTIVE RECOVERY)`: Median $292.92\,\mu\text{s}$ ($+69.1\%$ over fault-free `TFIB-Ref`), $467$ outliers $> 1\,\text{ms}$.

### Root Causes:
1. **Instruction Cache Pressure in `TFIB-Meta`:**
   Inlining `compute_tag`, computing two 32-bit multiplications, bitwise XORs, array lookups, and branch checks across $9{,}856$ inner-loop iterations significantly increases code cache footprint, making the thread disproportionately vulnerable to OS context-switching penalties.
2. **Recovery Latency Penalty:**
   When rollback and repair executes, the butterfly must restore operand snapshots, re-fetch the reference twiddle, perform Montgomery modular multiplication (`tfib_fqmul`), update coefficients, and run secondary invariant verification (`diff_retry`, `sum_retry`). This adds an empirical penalty of $+119.75\,\mu\text{s}$ per decapsulation ($+69.1\%$).
