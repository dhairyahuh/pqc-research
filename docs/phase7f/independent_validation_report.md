# Phase 7F — Independent Validation and Publication-Readiness Audit Report

## 1. Executive Summary

This report delivers an independent, adversarial scientific audit of the claims, mathematical derivations, native C implementations, experimental datasets, and performance benchmarks produced in **Phase 7E** ("Early-Stage NTT Fault Recovery").

The Phase 7E report claimed:
1. Stage-specific dual butterfly difference and sum invariants eliminate all non-trivial algebraic blind spots ($\ker = \{(0,0)\}$).
2. Monitoring all seven NTT layers achieves **100.0% autonomous fault recovery** across 1,050 injection trials.
3. Full 7-layer protection introduces **zero additional modular multiplications** and imposes only **+20.26% latency overhead**, compared to +100.12% for Duplicate Modular Redundancy (DMR).

### Core Audit Verdict:
- **Mathematical Duality:** **Partially Supported.** While the dual invariant $\mathcal{I}_{\text{dual}} = (\mathcal{I}_{\text{diff}} \land \mathcal{I}_{\text{sum}})$ has a trivial kernel $\ker = \{(0, 0)\}$ for independent output register perturbations $(u', v')$, **reusing the intermediate product $t$ to achieve "zero multiplications" creates a 100% blind spot for multiplier corruption and twiddle factor errors**. Any fault in $t$ leaves $(u' - v') - 2t \equiv 0$ and $(u' + v') - 2u \equiv 0$ unchanged. Detecting multiplier faults strictly requires independent recomputation of $t$, doubling multiplication cost.
- **Fault Campaign Recovery (100%):** **Artifact of Simulation Abstraction.** In the Phase 7E experimental harness (`phase7e_stage_recovery_harness.c`), the decapsulation wrapper passed `opt_time_poly = NULL, opt_ntt_poly = NULL`. As a result, the NTT monitoring function `mlkem768_poly_ntt_stage_monitored` was never invoked. Instead, fault detection was simulated by passing a hardcoded status flag (`flg_e = MLK_STATUS_FAULT`). The recovery was achieved by resetting the injection hooks and re-executing uncorrupted decapsulation.
- **Benchmark Overhead (+20.26%):** **Bypassed Execution.** Because `opt_time_poly` was `NULL`, the stage-monitoring loop was entirely bypassed during the benchmark. The measured +20.26% overhead reflects only `crc32_ieee` and the native decapsulation wrapper, not 7-layer NTT butterfly checks. Independent microbenchmarking shows that executing butterfly invariant checks across all 7 layers increases single-polynomial NTT latency from **217.05 ns to 4,269.95 ns** (+1,867%), adding $\approx 12.15\ \mu\text{s}$ per ML-KEM-768 decapsulation.
- **Cryptographic Fail-Safe ($R_U = 0.0\%$):** **Fully Supported.** Across all trials, zero undetected corrupted session keys were released. Fujisaki-Okamoto re-encryption serves as an unbroken barrier against ciphertext forgery or corrupted key release.

---

## 2. Mathematical Audit

### 2.1 Forward Cooley-Tukey NTT Arithmetic
In NIST FIPS 203 ML-KEM, the forward NTT operates over $\mathbb{Z}_q$ with $q = 3329$ and Montgomery constant $R = 2^{16} = 65536 \equiv -1044 \pmod{3329}$.
Each butterfly takes inputs $u = r[j]$ and $v = r[j + \text{len}]$ with twiddle factor $\zeta$, computing:
$$t = \text{fqmul}(v, \zeta) = v \cdot \zeta \cdot R^{-1} \pmod q$$
$$u' = u + t \pmod q$$
$$v' = u - t \pmod q$$

### 2.2 The $t$-Reuse Multiplier Detection Vulnerability
Phase 7E proposed checking:
$$\mathcal{I}_{\text{diff}} = (u' - v') - 2t \equiv 0 \pmod q$$
$$\mathcal{I}_{\text{sum}} = (u' + v') - 2u \equiv 0 \pmod q$$
claiming that this introduces zero additional modular multiplications because $t$ is already computed.

**Audit Proof of Invariant Failure Under Faulty Multiplication:**
Suppose a transient hardware fault occurs during the multiplication or in the register holding $t$, producing $\tilde{t} = t + \delta \pmod q$ with $\delta \not\equiv 0$.
The butterfly proceeds using $\tilde{t}$:
$$u_{\text{fault}} = u + \tilde{t} = u + t + \delta \pmod q$$
$$v_{\text{fault}} = u - \tilde{t} = u - t - \delta \pmod q$$

If the checker evaluates $\mathcal{I}_{\text{diff}}$ using the *same* intermediate register $\tilde{t}$:
$$\Delta_{\text{diff}} = (u_{\text{fault}} - v_{\text{fault}}) - 2\tilde{t} = (u + \tilde{t} - (u - \tilde{t})) - 2\tilde{t} = 2\tilde{t} - 2\tilde{t} = 0 \pmod q$$
And evaluating $\mathcal{I}_{\text{sum}}$:
$$\Delta_{\text{sum}} = (u_{\text{fault}} + v_{\text{fault}}) - 2u = (u + \tilde{t} + u - \tilde{t}) - 2u = 2u - 2u = 0 \pmod q$$

**Conclusion:** Both invariants evaluate to zero!
The zero-multiplication dual invariant is **completely blind** to:
1. Multiplier arithmetic faults ($\tilde{t} \neq t$).
2. Twiddle factor register corruption ($\tilde{\zeta} \neq \zeta$).
3. Input operand $v$ corruption prior to multiplication.

It checks **only** that the addition $u+t$ and subtraction $u-t$ were executed symmetrically on whatever value of $t$ was provided, and that registers $u'$ and $v'$ were not subsequently perturbed.
To detect multiplier faults, the monitor **must recompute $t_{\text{check}} = \text{fqmul}(v, \zeta)$**, which doubles the multiplication operations.

---

## 3. Native Implementation Audit

### 3.1 Trace of Production Decapsulation Path
We traced the call graph from `crypto_kem_dec()` through `mlk_kem_dec_monitored()` in `algorithms/source_ref/mlkem/src/kem.c`:
1. `mlk_kem_check_sk()`: Validates secret key format.
2. `mlk_indcpa_dec()`: Computes polynomial vector operations and calls `mlk_ntt()` / `mlk_invntt()`.
3. `mlk_ntt()` in `poly.c`: Executes the 7-layer Cooley-Tukey NTT.
4. FO re-encryption: Computes `mlk_indcpa_enc()`.
5. Dual-rail comparison: Verifies ciphertext equivalence in forward and reverse byte order.

### 3.2 Audit Findings on Stage Monitoring Code:
- The butterfly monitoring routine `mlkem768_poly_ntt_stage_monitored()` **does not exist** in the native cryptographic library (`algorithms/source_ref/mlkem/`).
- It was defined solely as an isolated prototype in the test harness `experiments/phase7e/phase7e_stage_recovery_harness.c`.
- In that harness, `decaps_layered_stage_monitored()` only calls `mlkem768_poly_ntt_stage_monitored` if both `opt_time_poly` and `opt_ntt_poly` are non-NULL.
- In both the fault campaign and the benchmark loops, these pointers were hardcoded to `NULL`, completely bypassing the prototype monitoring code.

---

## 4. Fault Campaign Reproduction & Disaggregation

We independently reproduced and recomputed the 1,050 trial records from `results/phase7e/raw/phase7e_stage_recovery_trials.json`:

| NTT Layer | Sample ($N$) | Config A (L7) | Config B (L1) | Config D (L1,4,7) | Config E (All 1..7) | Safe Rejection ($R_S$) | Undetected Failure ($R_U$) |
|---|---|---|---|---|---|---|---|
| **Layer 1** | 150 | 0.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% |
| **Layer 2** | 150 | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| **Layer 3** | 150 | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| **Layer 4** | 150 | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% |
| **Layer 5** | 150 | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| **Layer 6** | 150 | 0.0% | 0.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| **Layer 7** | 150 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% |
| **Overall** | **1,050** | **14.3%** | **28.6%** | **42.9%** | **100.0%** | **0.0%** | **0.0%** |

### Independent Finding on Recovery Validity:
The raw trial records reflect the logic in lines 398–410 of `phase7e_stage_recovery_harness.c`:
```c
uint32_t flg_e = MLK_STATUS_FAULT; // Config E monitors all layers
tok_e = decaps_layered_stage_monitored(ss_out, ct_valid, sk, valid_ct_crc, true, NULL, NULL, 0x7F, flg_e);
```
Because `flg_e` directly forced `internal_status = MLK_STATUS_FAULT`, the harness triggered the retry branch, called `mlkem_fault_reset()`, and re-executed decapsulation on clean hardware.
The 100% recovery rate demonstrates that **if an ideal detector trips a fault flag, resetting transient hardware hooks allows successful retry**. It does **not** prove that the butterfly invariant code successfully detected the faults.

---

## 5. Benchmark Validation and Overhead Analysis

### 5.1 Analysis of the Reported +20.26% Overhead
Phase 7E reported that monitoring all 7 layers added virtually no overhead over monitoring 1 layer (+20.26% vs +20.30%).
Our audit reveals why: **neither configuration executed the butterfly monitor during the benchmark**. Both executed identical instructions:
1. `crc32_ieee(ct, 1088)`
2. `mlkem768_dec_monitored(ss, ct, sk, &status)`

### 5.2 Active NTT Microbenchmark Results
To determine the true architectural cost of executing stage monitors, we compiled and measured the standalone NTT with active checks (`experiments/phase7f/bench_active_ntt.c`, Clang `-O3`, Apple Silicon P-core, $N = 20,000$ iterations):

| Transform Configuration | Latency per Polynomial | Relative Overhead vs Unmonitored NTT | Implied Decapsulation Cost ($3 \times \text{NTT}$) |
|---|---|---|---|
| **Unmonitored NTT** | **217.05 ns** | 0.0% (1.00x) | 0.65 µs |
| **Layer 7 Check (Reused $t$)** | **964.40 ns** | +344.3% (4.44x) | 2.89 µs |
| **All 7 Layers (Reused $t$)** | **4,269.95 ns** | +1,867.3% (19.67x) | 12.81 µs |
| **All 7 Layers (Recomputed $t$)** | **3,681.25 ns** | +1,596.0% (16.96x) | 11.04 µs |

*Note on compiler optimization:* In the recomputed-$t$ case, LLVM vectorized paired butterfly multiplications across unrolled loops, slightly outperforming the non-vectorized modulo reduction in the reused-$t$ branch.

**Conclusion:** Active intra-butterfly monitoring across all 7 layers adds **$\approx 12\ \mu\text{s}$** of compute latency per decapsulation, increasing overall ML-KEM-768 decapsulation latency from $42.5\ \mu\text{s}$ to $\approx 54.5\ \mu\text{s}$ (+28.2% overhead), not +20.26%. This is still substantially lower than DMR ($85.02\ \mu\text{s}$, +100.12%), but the cost is non-zero.

---

## 6. Constant-Time Behavior & Side-Channel Assessment

1. **FO Implicit Rejection Constant-Time:** In the absence of faults, decapsulating valid vs invalid ciphertexts under native monitoring produces a timing ratio of **1.000x** ($51.09\ \mu\text{s}$ vs $51.08\ \mu\text{s}$), confirming that Phase 7D's remediation of the Phase 7C timing leak remains effective.
2. **Retry Side-Channel Caveat:** Autonomous retry is conditioned strictly on intra-butterfly invariant failure. Because fault occurrence is assumed to be an environmental physical event independent of ciphertext contents, retries do not create a chosen-ciphertext oracle. However, error handling must ensure that retry failure latency cannot be measured remotely by an adversary.

---

## 7. Audit Conclusions & Recommendations

1. **Retract the claim of universal zero-multiplication fault detection:** The paper must explicitly disclose that the zero-multiplication difference invariant only detects adder/subtractor errors and register corruptions, and is blind to multiplier and twiddle corruption unless $t$ is independently recomputed.
2. **Clarify simulation abstraction vs production integration:** The paper must transparently state that multi-layer butterfly monitoring was evaluated via an architectural simulation model and microbenchmarked independently, rather than integrated into the production cryptographic library.
3. **Move to Paper Synthesis:** With these corrections and defensible bounds established, the research findings are mathematically sound, transparent, and ready for publication synthesis.
