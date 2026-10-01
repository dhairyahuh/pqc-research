# Experimental Methodology and Evaluation Protocol

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Evaluation Harness:** `experiments/phase7/phase7_layered_resilience.c`  
**Execution Environment:** Apple Silicon AArch64, macOS 26.5 / 27.0, Apple clang 21.0.0 `-O3`

---

## 1. Experimental Configurations Under Comparison

We systematically evaluate five configurations under identical input keys and matched fault seeds:

1. **Config 1: Unprotected Baseline ML-KEM-768**
   - Standard C reference implementation (`mlkem-native`).
   - Implicit rejection per FIPS 203; returns 0 on all decapsulation calls.
2. **Config 2: Existing Unweighted Parity-Projection Invariant (Phase 6 Candidate B)**
   - Computes $\sum \hat{p}_{2i} \equiv 128 p_0 \pmod q$ and $\sum \hat{p}_{2i+1} \equiv 128 p_1 \pmod q$.
3. **Config 3: Complementary NTT Protection**
   - Combines Unweighted Projection with Weighted Inverse-Zeta Projection:
     $\sum \zeta_{2i+1}^{-1} \hat{p}_{2i} \equiv 128 p_2 \pmod q$ and $\sum \zeta_{2i+1}^{-1} \hat{p}_{2i+1} \equiv 128 p_3 \pmod q$.
4. **Config 4: Full Duplicate Decapsulation (DMR, Phase 6 Candidate A1)**
   - Executes `mlkem768_dec` twice and verifies `ss1 == ss2` using constant-time comparison.
5. **Config 5: Layered Architecture**
   - Integrated 4-layer architecture:
     - Layer 1: Pre-invocation Input CRC32-IEEE.
     - Layer 2: Complementary NTT Invariant Protection.
     - Layer 3: Multi-Rail Decision Gate with Compiler Barrier.
     - Layer 4: Explicit Status Reporting & Single Transient Retry.

---

## 2. Fault Injection Campaign Protocol

We conduct **150 trials per fault class** across 8 threat classes (total **1,200 fault injection trials**):

- **Class 1 (Intermediate T):** Single butterfly multiplicative intermediate $t = r[j+\text{len}] \cdot \zeta$ perturbed by additive glitch $\Delta \in [10, 310]$ across layers 1 through 7.
- **Class 2 (Twiddle Zeta):** Single bit flip injected into twiddle factor table entry `mlk_zetas[k]`.
- **Class 3 (Output Add Register):** Single butterfly output register $r'[j]$ perturbed by additive glitch $\Delta$.
- **Class 4 (Correlated Arithmetic):** Double additive glitch injected into consecutive polynomial multiplier accumulators.
- **Class 5 (Pre-Invocation Input Corruption):** Single-bit and multi-bit corruption of the 1088-byte ciphertext buffer $ct$ prior to decapsulation invocation.
- **Class 6 (Checker Perturbation):** Single-bit corruption injected into status token registers during countermeasure evaluation.
- **Class 7 (Control Flow FO Gate):** Inversion of the FO verification flag ($0 \to 1$), forcing rejection of valid ciphertexts.
- **Class 8 (Persistent Stuck-At Fault):** Identical fault injection repeating across both passes of decapsulation to model permanent physical cell latch-up.

---

## 3. Cryptographic Outcome Classification

Every experimental trial is classified into mutually exclusive outcomes:
- **Clean Output (OK):** No fault injected; valid shared secret produced.
- **Detected Fault (FATAL):** Fault detected by Layer 1, 2, or 3; execution safely aborted with explicit error code.
- **Recovered via Retry:** Transient fault detected by Layer 2/3; single transient retry cleared the glitch and safely produced the correct shared secret.
- **Silent Key Corruption:** Fault not detected; incorrect or implicitly rejected key output without caller warning.
- **Common-Mode Failure:** Fault present in both passes (e.g. DMR on bad input or persistent fault); comparison passes erroneously.

---

## 4. Latency Benchmarking Protocol

- **Timer:** High-resolution monotonic clock (`clock_gettime(CLOCK_MONOTONIC)`), providing sub-microsecond resolution.
- **Repetitions:** 2,000 iterations per configuration to minimize measurement noise.
- **Warm-Up:** 200 unmeasured preliminary iterations to populate processor instruction and data caches.
- **Reproducibility:** Pinned seeds (`0x2A` and `0x4B`) ensuring deterministic test generation across runs.
