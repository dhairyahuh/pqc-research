# Phase 3 — Comprehensive ML-DSA Fault Campaign & Sensitivity Mapping Audit

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyajain/pqc-research`  
**Standards:** NIST FIPS 204 (ML-DSA)  
**Document Version:** 1.0.0-AUDIT  
**Date:** October 1, 2026  
**Status:** PHASE 3 COMPLETE  

---

## 1. Phase 3 Objective

The objective of Phase 3 is to execute a rigorous, systematic, implementation-level fault campaign across all NIST FIPS 204 parameter sets (**ML-DSA-44**, **ML-DSA-65**, **ML-DSA-87**), characterizing internal computational sensitivity, quantifying error diffusion across the 8-layer radix-2 NTT, dissecting the rejection sampling firewall, evaluating the verification decision boundary, and mapping fault behavior against the Phase 2 ML-KEM baseline.

**Strict Scope Boundary:** This phase addresses ONLY ML-DSA fault characterization, internal sensitivity mapping, and verification decision boundary modeling. Resilience mechanisms, algorithmic redundancy, retry countermeasures, formal verification, and spacecraft protocol layers are strictly reserved for subsequent phases. No cryptographic breaks are claimed without formal demonstration.

---

## 2. Experimental Research Questions

| Research Question | Focus | Experimental Resolution Summary |
|:---|:---|:---|
| **RQ3.1 — NTT Diffusion Law** | Does ML-DSA exhibit a structural NTT diffusion law across its 8 layers? | **Yes.** In FIPS 204 ($q = 8,380,417 \equiv 1 \pmod{512}$), the 8-layer decomposition follows $N_\text{diffused}^\text{shared}(L) = 2^{9-L}$ and $N_\text{diffused}^\text{single}(L) = 2^{8-L}$. Empirical measurement across all 8 layers confirmed exact agreement with zero deviation. |
| **RQ3.2 — Rejection Sampling Containment** | How does the signing rejection loop respond to internal arithmetic faults? | In signing, secret key NTT perturbations and response vector faults are detected by norm bounds ($\|z\|_\infty < \gamma_1 - \beta$, $\|w_0\|_\infty < \gamma_2 - \beta$). Transient faults cause single-attempt retries followed by recovery. Persistent faults exhaust the attempt budget (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`), acting as a fail-closed firewall. |
| **RQ3.3 — Verification Gate Vulnerability** | Can a single-point fault bypass signature verification? | **Yes (`INVALID -> ACCEPT`).** In `mld_sign_verify_internal`, inverting the constant-time comparison result (`cmp = 0`) causes an invalid/tampered signature to be accepted with **100.0% probability (95% CI: [99.63%, 100.0%])** across all parameter sets. |
| **RQ3.4 — Norm Check Bypass Asymmetry** | Does forcing norm checks to pass during signing compromise verification? | **No.** Forcing norm checks on $z$ or $w_0$ during signing allows out-of-bounds candidates to be emitted into signatures; however, independent clean verification catches them due to verification norm checks and commitment verification, yielding 100% `INVALID_SIGNATURE`. |
| **RQ3.5 — Challenge Generation Sensitivity** | How do bit flips in challenge hash digests propagate? | Single bit flips in $c\text{tilde}$ destroy challenge polynomial consistency in `SampleInBall` and commitment reconstruction, causing 100% verification rejection. |
| **RQ3.6 — Key Material Sensitivity** | How does memory corruption in serialized secret keys affect operations? | Corruptions in $\rho$, $tr$, and $t_0$ produce invalid signatures; corruptions in $s_1$ and $s_2$ trigger 100% attempt budget exhaustion; corruption in private seed $K$ alters nonce derivation in hedged signing mode. |
| **RQ3.7 — Deterministic vs. Hedged Signing** | Does signing randomness mode change fault outcomes? | In deterministic mode ($rnd = 0$), identical fault inputs produce 100% bit-exact reproducible failure states; in hedged mode, randomness masks attempt counters while preserving the rejection containment boundary. |
| **RQ3.8 — ML-KEM vs. ML-DSA Comparison** | How does ML-DSA fault sensitivity contrast with ML-KEM? | ML-KEM possesses decryption slack budget ($\lfloor q/4 \rfloor = 832$) masking single output register faults; ML-DSA verification has zero arithmetic slack (any $\Delta \ge 1$ causes rejection). ML-KEM fails closed to pseudorandom keys; ML-DSA fails closed via retry budget exhaustion (DoS). |

---

## 3. Implementation Under Test & Provenance

- **Primary Native Baseline:** `mldsa-native`
  - **Git Commit:** `14d195a82dd27ed6bac35b403f5386bf43a893d3`
  - **Language / Standards:** C99 / C11, formal CBMC contract annotations.
  - **Source Directory:** `algorithms/source_ref/mldsa/`
  - **Compilation:** `clang -O3 -Wall -Wextra -std=c11`
  - **Host Architecture:** Darwin ARM64 (Apple Silicon) / x86_64 compatible.
- **Cross-Implementation Oracle:** `liboqs`
  - **Version:** `0.16.0`
  - **Role:** Independent oracle for FIPS 204 KAT agreement, signature verification, and tampered signature rejection.

---

## 4. Mathematical & Implementation Mapping

| Mathematical Object | FIPS 204 Spec | C Implementation Struct/Function | Source File | Fault-Sensitive State |
|:---|:---|:---|:---|:---|
| Modulus | $q = 8,380,417$ | `MLDSA_Q` | `common.h` | Modular reduction barrier |
| Ring Degree | $n = 256$ | `MLDSA_N` | `common.h` | NTT transform dimension |
| Forward NTT | $\text{NTT}(a)$ | `mld_poly_ntt_c()` | `src/poly.c` | 8-layer butterfly execution |
| Butterfly Block | Cooley-Tukey | `mld_ntt_butterfly_block()` | `src/poly.c` | Intermediate $t$, output registers |
| Response Vector | $\mathbf{z} = \mathbf{y} + c \mathbf{s}_1$ | `mld_compute_pack_z()` | `src/sign.c` | Response bounds ($\|z\|_\infty$) |
| Norm Check $z$ | $\|z\|_\infty < \gamma_1 - \beta$ | `mld_polyvecl_chknorm()` | `src/polyvec.c` | Rejection predicate |
| Norm Check $w_0$ | $\|w_0\|_\infty < \gamma_2 - \beta$ | `mld_poly_chknorm()` | `src/poly.c` | Low-bits rejection predicate |
| Challenge Gen | $c = \text{SampleInBall}(\tilde{c})$ | `mld_poly_challenge()` | `src/poly.c` | Ball permutation / signs |
| Verification Gate | $c' \stackrel{?}{=} c$ | `ct_memcmp(c, c2, CTILDEBYTES)` | `src/sign.c` | Equality predicate `cmp` |

---

## 5. Fault Taxonomy

The Phase 3 campaign refines the research taxonomy for digital signature operations:

| Taxonomy Category | Description | Implementation Locus | Concrete Examples |
|:---|:---|:---|:---|
| **A — STATE/DATA FAULT** | Mutation of static serialized memory | Secret key buffers, public key buffers | Byte flip in secret seed $K$ or $\rho$ |
| **B — MID-OPERATION FAULT** | Real-time perturbation during transformation | Butterfly arithmetic, Montgomery reduction | Intermediate product glitch $t = \text{fqmul}$ |
| **C — SELECTED-STAGE FAULT** | Stage-isolated perturbation in forward NTT | Layers 1 through 8 of forward NTT | Layer 4 butterfly 15 additive glitch |
| **D — SELECTED-COEFFICIENT FAULT** | Pinpointed perturbation of coefficient | Sampled candidate polynomial $y$ | Perturbation of single coefficient $y_i$ |
| **E — CONTROL/PREDICATE FAULT** | Bypass or forced inversion of decision logic | Constant-time memory comparison `cmp` | Forcing `cmp = 0` on corrupted signature |
| **G — REJECTION-SAMPLING FAULT** | Forcing pass/fail on norm rejection gates | Norm checks on $z$, $w_0$, or $c t_0$ | Forcing norm check pass on invalid $z$ |
| **H — CHALLENGE FAULT** | Perturbation of random oracle digest | Challenge digest $\tilde{c}$ | Bit flip in $\tilde{c}$ prior to `SampleInBall` |

---

## 6. Injection Locations

All injection hooks are placed at verified, operational internal C code loci:

1. **Forward NTT Butterfly (`poly.c:mld_ntt_butterfly_block`)**:
   - `INPUT_B_PRE_MUL`: Perturbation of $r[j+\text{len}]$ before Montgomery multiplication.
   - `TWIDDLE_ZETA`: Perturbation of root of unity $\zeta$.
   - `INTERMEDIATE_T`: Perturbation of intermediate product $t = \text{fqmul}(r[j+\text{len}], \zeta)$.
   - `OUTPUT_ADD`: Perturbation of upper branch $r[j] = r[j] + t$.
   - `OUTPUT_SUB`: Perturbation of lower branch $r[j+\text{len}] = r[j] - t$.
2. **Rejection Norm Checks (`sign.c:mld_attempt_signature_generation`)**:
   - `NORM_CHECK_Z`: Norm bound check on response vector $z$.
   - `NORM_CHECK_W0`: Low-bits norm bound check on $w_0$.
   - `NORM_CHECK_CT0`: Hint check on $c t_0$.
3. **Challenge Random Oracle (`sign.c:hook_mid_mldsa_challenge`)**:
   - Intercepts 32/48/64-byte challenge digest $\tilde{c}$ prior to `SampleInBall`.
4. **Verification Decision Gate (`sign.c:mld_sign_verify_internal`)**:
   - `VERIFY_CMP`: Constant-time memory comparison `cmp = ct_memcmp(c, c2, CTILDEBYTES)`.
   - `VERIFY_NORM_Z`: Verification-time norm bound check on $z$.
5. **Secret Key Memory Regions (`mldsa_campaign_runner.c`)**:
   - `REGION_RHO`: Public matrix seed $\rho$ (32 bytes).
   - `REGION_SEED_K`: Private signing randomness seed $K$ (32 bytes).
   - `REGION_TR`: Public key hash $tr = H(pk)$ (64 bytes).
   - `REGION_S1`: Private vector $\mathbf{s}_1$.
   - `REGION_S2`: Private vector $\mathbf{s}_2$.

---

## 7. Parameter Sets Evaluated

Every major campaign covers all three FIPS 204 parameter sets:

| Parameter Set | Security Category | Matrix $(K, L)$ | $(\eta, \tau, \beta)$ | $(\gamma_1, \gamma_2)$ | Signature Size | Public Key Size | Secret Key Size |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **ML-DSA-44** | NIST Level 2 | $(4, 4)$ | $(2, 39, 78)$ | $(2^{17}, (q-1)/88)$ | 2,420 B | 1,312 B | 2,560 B |
| **ML-DSA-65** | NIST Level 3 | $(6, 5)$ | $(4, 49, 196)$ | $(2^{19}, (q-1)/32)$ | 3,309 B | 1,952 B | 4,032 B |
| **ML-DSA-87** | NIST Level 5 | $(8, 7)$ | $(2, 60, 120)$ | $(2^{19}, (q-1)/32)$ | 4,627 B | 2,592 B | 4,896 B |

---

## 8. Baseline Results & Controls

Baseline verification was conducted with $N=1,000$ trials per parameter set under fixed deterministic PRNG seeds:

| Algorithm | Control | Injected Delta | Total Trials | Success Rate | 95% Wilson CI | Throughput |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **ML-DSA-44** | Control A (No-Fault) | None | 1,000 | 100.00% | [99.63%, 100.00%] | 2,862.59 ops/sec |
| **ML-DSA-44** | Control B (Zero-Glitch) | $\Delta = 0$ | 1,000 | 100.00% | [99.63%, 100.00%] | 2,862.59 ops/sec |
| **ML-DSA-65** | Control A (No-Fault) | None | 1,000 | 100.00% | [99.63%, 100.00%] | 1,931.38 ops/sec |
| **ML-DSA-65** | Control B (Zero-Glitch) | $\Delta = 0$ | 1,000 | 100.00% | [99.63%, 100.00%] | 1,931.38 ops/sec |
| **ML-DSA-87** | Control A (No-Fault) | None | 1,000 | 100.00% | [99.63%, 100.00%] | 1,502.75 ops/sec |
| **ML-DSA-87** | Control B (Zero-Glitch) | $\Delta = 0$ | 1,000 | 100.00% | [99.63%, 100.00%] | 1,502.75 ops/sec |

---

## 9. NTT 8-Layer Diffusion Results

The forward NTT in ML-DSA decomposes completely into 8 radix-2 layers. Diffusion testing evaluated the exact number of perturbed time-domain coefficients produced by a single fault injected at Layer $L$:

| Layer $L$ | Locus | Mathematical Law | Predicted Diffused Coeffs | Observed Diffused Coeffs | Discrepancy |
|:---:|:---|:---:|:---:|:---:|:---:|
| 1 | `INTERMEDIATE_T` (Shared) | $2^{9-1}$ | 256 | 256 | 0 |
| 1 | `OUTPUT_ADD` (Single) | $2^{8-1}$ | 128 | 128 | 0 |
| 2 | `INTERMEDIATE_T` (Shared) | $2^{9-2}$ | 128 | 128 | 0 |
| 2 | `OUTPUT_ADD` (Single) | $2^{8-2}$ | 64 | 64 | 0 |
| 3 | `INTERMEDIATE_T` (Shared) | $2^{9-3}$ | 64 | 64 | 0 |
| 3 | `OUTPUT_ADD` (Single) | $2^{8-3}$ | 32 | 32 | 0 |
| 4 | `INTERMEDIATE_T` (Shared) | $2^{9-4}$ | 32 | 32 | 0 |
| 4 | `OUTPUT_ADD` (Single) | $2^{8-4}$ | 16 | 16 | 0 |
| 5 | `INTERMEDIATE_T` (Shared) | $2^{9-5}$ | 16 | 16 | 0 |
| 5 | `OUTPUT_ADD` (Single) | $2^{8-5}$ | 8 | 8 | 0 |
| 6 | `INTERMEDIATE_T` (Shared) | $2^{9-6}$ | 8 | 8 | 0 |
| 6 | `OUTPUT_ADD` (Single) | $2^{8-6}$ | 4 | 4 | 0 |
| 7 | `INTERMEDIATE_T` (Shared) | $2^{9-7}$ | 4 | 4 | 0 |
| 7 | `OUTPUT_ADD` (Single) | $2^{8-7}$ | 2 | 2 | 0 |
| 8 | `INTERMEDIATE_T` (Shared) | $2^{9-8}$ | 2 | 2 | 0 |
| 8 | `OUTPUT_ADD` (Single) | $2^{8-8}$ | 1 | 1 | 0 |

**Finding:** The radix-2 diffusion tree is exact and deterministic across all 8 layers. Unlike ML-KEM's 7-layer incomplete NTT, ML-DSA's complete 8-layer NTT extends diffusion down to individual coefficients ($2^{8-8} = 1$).

---

## 10. Rejection Sampling Results & Norm Checks

| Experiment ID | Target Locus | Override Action | Dominant Outcome | Rate (95% CI) | Analysis |
|:---|:---|:---|:---|:---:|:---|
| `NORM_Z_FORCED_PASS` | Response norm $z$ | Force Pass ($0$) | `INVALID_SIGNATURE` | 100.00% [99.63%, 100.00%] | Signature emitted with $\|z\|_\infty \ge \gamma_1 - \beta$. Clean verification immediately catches and rejects it. |
| `NORM_Z_TRANSIENT_RETRY` | Response norm $z$ | Force Fail (single) | `CORRECT` | 100.00% [99.63%, 100.00%] | Attempt 0 rejected; retry attempt 1 succeeds cleanly. Transparent fault recovery. |
| `NORM_Z_FORCED_REJECT` | Response norm $z$ | Force Fail (persist) | `SIGNING_REJECT_RETRY` | 100.00% [92.89%, 100.00%] | All 821 attempts rejected. Fails closed with `MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED` (DoS). |
| `NORM_W0_FORCED_PASS` | Low-bits norm $w_0$ | Force Pass ($0$) | `INVALID_SIGNATURE` | 100.00% [99.63%, 100.00%] | Out-of-bounds low bits cause hint reconstruction mismatch in verification. |

---

## 11. Verification Decision Predicate Results (4 Canonical States)

The verification predicate experiment tested the 4 canonical transitions on `mld_sign_verify_internal`:

| State | Canonical Name | Signature Input | Injected Gate Fault | Observed Decision | Rate (95% CI) | Security Consequence |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| **1** | `VALID -> ACCEPT` | VALID | None (Control) | **ACCEPT** | 100.00% [99.63%, 100.00%] | Nominal valid traffic passes. |
| **2** | `INVALID -> REJECT` | INVALID | None (Control) | **REJECT** | 100.00% [99.63%, 100.00%] | Nominal invalid traffic blocked. |
| **3** | `VALID -> REJECT` | VALID | Forced Fail (`cmp = 1`) | **REJECT** | 100.00% [99.63%, 100.00%] | Operational Denial of Service (valid command dropped). |
| **4** | `INVALID -> ACCEPT` | INVALID | Forced Pass (`cmp = 0`) | **ACCEPT** | 100.00% [99.63%, 100.00%] | **CRITICAL:** Verification decision bypass. Corrupted or forged payload accepted. |

**Critical Finding:** State 4 (`INVALID -> ACCEPT`) succeeds with 100% reliability under a single predicate inversion. Because verification terminates with a single Boolean decision, hardware control glitches on this gate represent an unmitigated single point of failure.

---

## 12. Secret Key Memory Region Decomposition

| Region | Bytes | Functional Role | Dominant Outcome | Rate (95% CI) | Impact Mechanism |
|:---|:---:|:---|:---|:---:|:---|
| `REGION_RHO` | 32 B | Public seed for matrix $\hat{A}$ | `INVALID_SIGNATURE` | 100.00% [99.63%, 100.00%] | Matrix desynchronization between signer and verifier. |
| `REGION_SEED_K` | 32 B | Private signing PRF seed | `CORRECT` (det) / `VALID` | 100.00% [99.63%, 100.00%] | In deterministic mode, seed $K$ does not alter validity of clean signatures. |
| `REGION_TR` | 64 B | Hash $tr = H(pk)$ | `INVALID_SIGNATURE` | 100.00% [99.63%, 100.00%] | Alters message digest $\mu$, causing challenge commitment mismatch. |
| `REGION_S1` | Packed | Secret vector $\mathbf{s}_1$ | `SIGNING_REJECT_RETRY` | 100.00% [99.63%, 100.00%] | 100% attempt exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`). |
| `REGION_S2` | Packed | Secret vector $\mathbf{s}_2$ | `SIGNING_REJECT_RETRY` | 100.00% [99.63%, 100.00%] | 100% attempt exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`). |

---

## 13. Cross-Implementation Findings (`mldsa-native` vs `liboqs 0.16.0`)

1. **Clean Baseline Interoperability**: 100% interoperable across all three security levels (ML-DSA-44, 65, 87). Keys and signatures generated by `mldsa-native` verify cleanly in `liboqs`, and vice versa.
2. **Tampered Signature Rejection**: Both implementations deterministically reject modified signatures with 100% consistency.
3. **Internal Hook Comparability**: `liboqs` utilizes opaque vectorized SIMD/AVX2 routines without internal fault hooks. Direct mid-butterfly or norm-check hooks cannot be portably placed in `liboqs` without invasive modifications, rendering internal hooks **NOT COMPARABLE** at the binary level.

---

## 14. ML-KEM vs. ML-DSA Comparison

| Dimension | ML-KEM (FIPS 203) | ML-DSA (FIPS 204) | Cross-Algorithm Significance |
|:---|:---|:---|:---|
| **Mathematical Domain** | Incomplete 7-layer NTT ($n/2=128$ degree-2 rings) | Complete 8-layer NTT ($n=256$ degree-1 rings) | ML-DSA errors diffuse across all 256 coefficients at Layer 1; ML-KEM stops at 128 coefficients. |
| **Operational Flow** | Deterministic forward decapsulation pass | Non-deterministic rejection sampling loop | Faults in ML-KEM alter output key; faults in ML-DSA cause attempt looping and potential DoS. |
| **Slack / Fault Tolerance** | Error slack budget $\lfloor q/4 \rfloor = 832$ masks small register glitches | Zero arithmetic slack in verification | ML-KEM is inherently more resilient to small register glitches than ML-DSA verification. |
| **Containment Failure** | Implicit rejection to pseudorandom key (no crash) | Attempt budget exhaustion (error return) | Both schemes fail closed, preventing naive secret extraction. |
| **Decision Vulnerability** | N/A (produces 32-byte shared key) | Boolean comparison gate `cmp = 0` | ML-DSA has an exploitable `INVALID -> ACCEPT` bypass gate that has no analog in ML-KEM. |

---

## 15. Security & Space-System Interpretation

### Security Classification
- **Robustness Observation**: Rejection sampling acts as a strong arithmetic containment barrier. Perturbing intermediate values during signing consistently triggers rejection retries or budget exhaustion rather than emitting exploitable faulty signatures.
- **Critical Vulnerability Primitive**: Verification decision predicate inversion (`INVALID -> ACCEPT`). An attacker capable of clock-glitching or EM-pulsing the final memory comparison can forge signatures with 100% success.
- **Denial-of-Service Primitive**: Any single stuck-at fault or persistent corruption in $\mathbf{s}_1$ or norm check circuitry forces 100% signing attempt exhaustion, disabling spacecraft uplink/downlink authentication.

### Space-System Context
Under the simulated computational fault model:
- Heavy-ion strikes (SEUs) striking the arithmetic datapath during signing are absorbed by the rejection sampling firewall.
- SEUs striking verification comparison registers represent a high-severity mission risk, enabling unauthenticated command injection.
- No radiation hardness or space qualification is claimed.

---

## 16. Limitations & Threats to Validity

1. **Simulation Abstraction**: Faults are injected in software via C hooks, simulating transient register glitches and memory bit flips. Physical silicon radiation effects (latchup, multi-cell upsets) are not modeled.
2. **Single-Fault Assumption**: Experiments focus on single-event upsets per operation. Multi-bit simultaneous upsets in distinct registers were not exhaustively swept.
3. **Compiler Optimization Sensitivity**: Hooks are marked with `volatile` boundaries; however, aggressive `-O3` vectorization by different compilers (e.g., GCC vs. Clang) could reorder non-observable state.

---

## 17. Reproducibility

Every experiment configuration is fully captured in version-controlled YAML files:
- `experiments/configurations/mldsa_phase3/*.yaml`
- Deterministic PRNG seeds: `123456789ULL`, `5544332211ULL`, `9988776655ULL`
- CLI Replay Command:
  ```bash
  python3 experiments/mldsa/run_campaign.py --config experiments/configurations/mldsa_phase3/ntt_stage_screening.yaml
  ```
- Full Re-run Command:
  ```bash
  python3 experiments/mldsa/run_campaign.py --all
  ```

---

## 18. Files Created & Modified

### Created
- `docs/mldsa-implementation-map.md`
- `docs/phase3-mldsa-fault-campaign-audit.md`
- `algorithms/source_ref/mldsa_fault_hooks.h`
- `algorithms/source_ref/mldsa_fault_hooks.c`
- `experiments/mldsa/mldsa_campaign_runner.c`
- `experiments/mldsa/run_campaign.py`
- `experiments/mldsa/analyze_campaign_results.py`
- `experiments/configurations/mldsa_phase3/baseline_verification.yaml`
- `experiments/configurations/mldsa_phase3/ntt_stage_screening.yaml`
- `experiments/configurations/mldsa_phase3/fault_magnitude.yaml`
- `experiments/configurations/mldsa_phase3/rejection_sampling.yaml`
- `experiments/configurations/mldsa_phase3/challenge_faults.yaml`
- `experiments/configurations/mldsa_phase3/key_region_faults.yaml`
- `experiments/configurations/mldsa_phase3/verification_faults.yaml`
- `tests/test_phase3_campaign.py`
- `results/phase3/raw/mldsa_campaign_raw_results.json`
- `results/phase3/processed/sensitivity_matrix.csv`
- `results/phase3/summaries/phase3_executive_summary.md`
- `results/phase3/summaries/ntt_diffusion_validation.md`
- `results/phase3/summaries/verification_decision_matrix.md`
- `results/phase3/summaries/secret_key_region_decomposition.md`
- `results/phase3/summaries/mldsa_vs_mlkem_comparison.md`
- `results/phase3/figures/ntt_sensitivity_map.txt`
- `results/phase3/figures/fault_magnitude_curve.txt`
- `results/phase3/figures/verification_decision_boundary.txt`

### Modified
- `algorithms/source_ref/mldsa/src/poly.c` (Fault injection hooks in butterfly and layer loops)
- `algorithms/source_ref/mldsa/src/sign.c` (Fault injection hooks in signing and verification gates)
- `Makefile` (Added multi-level instrumented targets and campaign runner binary)
- `docs/research-roadmap.md` (Updated Phase 3 status and findings)

---

## 19. Git Commit

Commit Hash: (Pending final git commit)  
Message: `research(phase-3): implement systematic ML-DSA fault campaign`
