# PHASE 0: State-of-the-Art, Research Gap & Contribution Analysis

**Document Title:** Academic Research Audit & Strategic Gap Analysis  
**Project Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Algorithms & Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA)  
**Document Version:** 1.0.0-FINAL  
**Date:** October 1, 2026  
**Author/Role:** Senior Research Engineer & Research-Methodology Lead  
**Classification:** Scientific Ground-Truth Audit & Pre-Phase 1 Strategic Plan  

---

## Executive Summary

This Phase 0 audit establishes the definitive scientific ground truth for the university research project *"Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"*. 

In accordance with strict research discipline, this audit **does not write new production cryptographic code, add fault hooks, or engineer countermeasures**. Instead, it executes an exhaustive, skeptical evaluation of:
1. **The current repository assets**, decomposing all claims into verified facts, formal results, empirical observations, implementation-specific behaviors, simulation artifacts, and unproven hypotheses.
2. **The global academic literature** spanning 25 primary works across IACR (TCHES, EuroS&P, CHES), IEEE (TCAD, TETC, TCAS-I, TIFS, AERO), ACM (CCS, TECS, CSUR), NIST standards, and space engineering standards (NASA, ECSS, CCSDS).
3. **The direct overlaps and genuine research gaps**, establishing what is already known, what previous works do better, what our repository does differently, and where a defensible, publishable scholarly contribution exists.

### Primary Audit Verdicts
- **The Fujisaki-Okamoto (FO) transform comparison check is NOT a novel fault target.** Bypassing `ct_memcmp` or inverting equality flags to build Plaintext-Checking Oracles (PCOs) is well-established (Pessl & Prokop 2021, Hermelink et al. 2021, Delvaux 2022, Jaiswal et al. 2024). We must NOT claim FO comparison vulnerability as a primary discovery.
- **Software memory bit-flips are NOT physical space radiation.** Equating Python `ctypes` memory mutations with cosmic ray Single Event Upsets (SEUs) without silicon-level beam testing, LET thresholds, or microarchitectural fault rates is scientifically indefensible. The space context in this repository is currently an *abstract operational motivation and protocol-level framing simulation*, not a physical radiation qualification.
- **The genuine research opportunity lies in a multi-layer triad:**
  1. *Mathematical Layer:* The analytical modeling of intermediate Number Theoretic Transform (NTT) butterfly error diffusion against non-linear lossy compression quantization rounding thresholds (`Compress_d` in FIPS 203), explaining why early-stage faults result in self-healing valid decapsulations (100.0%) while late-stage faults trigger implicit rejection (100.0%).
  2. *Implementation Layer:* The design and evaluation of *software-only selective algorithmic assertions* for general-purpose embedded space processors, exploiting non-uniform sensitivity maps to achieve $>95\%$ fault coverage with $<25\%$ CPU overhead (avoiding 200% triple modular redundancy).
  3. *Protocol/System Layer:* The end-to-end mapping of cryptographic session desynchronization into multi-stage spacecraft telecommand framing pipelines (CCSDS TC / SDLS), proving that out-of-sync keys result in $100\%$ framing rejection ($p \approx 1 - 2^{-32}$) rather than silent command execution, and evaluating autonomous link recovery.

---

## 1. Factual Inventory of the Current Repository

A rigorous audit of the workspace was conducted, inspecting source code, commit history, build configuration, scripts, documentation, and raw JSON/CSV data.

```
                             [ REPOSITORY ASSET TOPOLOGY ]
 ├── algorithms/
 │   ├── source_ref/mlkem/     <-- Pinned commit fc269bc2d106 (mlkem-native C90)
 │   ├── source_ref/mldsa/     <-- Pinned commit 14d195a82dd2 (mldsa-native C90)
 │   ├── mlkem_fault_hooks.c   <-- Mid-operation butterfly, accumulator, & CBD hooks
 │   └── oqs_wrapper.py        <-- liboqs 0.16.0 (Path A Oracle via ctypes)
 ├── tests/
 │   ├── test_fips_kats.c      <-- 18 NIST KAT vectors (All 6 parameter sets PASS)
 │   └── test_interop_path_a_b.c
 ├── experiments/
 │   ├── fault_injection/      <-- mlkem768_internal_fault_experiment.c & level1_campaign.py
 │   └── system_model/         <-- spacecraft_protocol_sim.py (6-stage telecommand pipeline)
 ├── resilience/               <-- EMPTY STUBS (checkpoint, integrity_checks, redundancy, retry)
 └── results/                  <-- JSON benchmarks, validation logs, literature_matrix.csv
```

### A. What Currently Exists
1. `VERIFIED FACT` **Dual-Engine Architecture:**
   - **Path A (External Oracle):** Unmodified `liboqs` dynamic library version 0.16.0 installed via Homebrew bottle on macOS ARM64 (Apple M1, Darwin 27.0.0, Apple Clang 21.0.0). Accessed via Python `ctypes` for black-box baseline and buffer tests.
   - **Path B (Research Source):** Pinned, standalone C90 source code from the Post-Quantum Cryptography Alliance (PQCA):
     - `mlkem-native`: Git commit `fc269bc2d1068486625a3775310c2c1f28d74732` (September 27, 2026).
     - `mldsa-native`: Git commit `14d195a82dd27ed6bac35b403f5386bf43a893d3` / `88a5369bb911` (September 23, 2026).
2. `VERIFIED FACT` **NIST FIPS Known Answer Test (KAT) Harness:**
   - `tests/test_fips_kats.c` deterministically verifies all 6 parameter sets across both standards:
     - ML-KEM: 512, 768, 1024 (KeyGen, Encaps, Decaps).
     - ML-DSA: 44, 65, 87 (Sign, Verify, Tamper Detection).
   - All 18 KAT test vectors pass with 100% bit-level reproducibility against NIST reference vectors pinned in `references/test_vectors/`.
3. `VERIFIED FACT` **Internal Mid-Operation Research Hooks for ML-KEM-768:**
   - Implemented in `algorithms/source_ref/mlkem_fault_hooks.h` and `mlkem_fault_hooks.c`:
     - `hook_mid_ntt_butterfly`: Injected inside `mlk_ntt_butterfly_block` across layers $1 \dots 7$ and butterflies $0 \dots 127$.
     - `hook_mid_polymul_accumulator`: Injected inside vector accumulation loop $k \in \{0, 1, 2\}$ in `polyvec_basemul_acc_montgomery_cached_c`.
     - `hook_mid_cbd_popcount`: Injected inside 32-bit SWAR Hamming weight intermediate calculation ($d$) in `mlk_poly_cbd2`.
     - `hook_mid_cbd_sample`: Injected into sampled difference $a - b$.
     - `mlk_ct_cmov_zero` flag inversion in `mlk_kem_dec` (bidirectional predicate control).
4. `VERIFIED FACT` **Internal Fault Experiment Runner:**
   - `experiments/fault_injection/mlkem768_internal_fault_experiment.c` executing matched-pair campaigns ($N=100$ and $N=1,000$) with Wilson 95% confidence intervals, serialized to `results/mlkem768_internal_fault_validation.json`.
5. `VERIFIED FACT` **Abstract Spacecraft Protocol Simulator:**
   - `experiments/system_model/spacecraft_protocol_sim.py` implementing a 6-stage telecommand receiver pipeline (`decrypt -> magic sync -> sequence window -> opcode check -> bounds/CRC -> execution`), serialized to `results/spacecraft_protocol_desync_results.json`.
6. `VERIFIED FACT` **Empty Resilience Modules:**
   - Subdirectories in `resilience/` (`checkpoint`, `integrity_checks`, `redundancy`, `retry`) are completely empty stubs. No countermeasures are implemented.

---

### B. What Has Actually Been Experimentally Demonstrated
1. `EMPIRICAL RESULT` **Layer 1 NTT Butterfly Perturbation Absorption:**
   - Single-bit perturbations injected into Cooley-Tukey butterfly operations at **Layer 1** of `mlk_poly_ntt_c()` in ML-KEM-768 resulted in **100/100 (100.0%) legitimate decapsulations (`CORRECT_VALID_DECAPSULATION`)** [95% CI: 96.3% – 100.0%]. The shared secret produced was identical to the clean baseline.
2. `EMPIRICAL RESULT` **Layer 4 & Layer 7 NTT Implicit Rejection:**
   - Identical perturbations injected at **Layer 4** and **Layer 7** resulted in **100/100 (100.0%) implicit rejections (`EXPECTED_IMPLICIT_REJECTION`)** [95% CI: 96.3% – 100.0%].
3. `EMPIRICAL RESULT` **PolyMul Accumulator & CBD Sampling Implicit Rejection:**
   - Additive glitches (+15) on 32-bit vector accumulators $t[0]$ at $k \in \{0, 1, 2\}$ yielded **100.0% implicit rejection**.
   - Bit flips on SWAR popcount intermediates and sampled coefficients yielded **100.0% implicit rejection**.
4. `EMPIRICAL RESULT` **Bidirectional FO Predicate Behavior:**
   - Direction A (Valid CT, `fail` forced $0 \to 1$): **1000/1000 (100.0%)** selected the pseudorandom implicit rejection key $K_{rej} = \text{Hash}_J(z \parallel c)$.
   - Direction B1 (1-bit corrupted CT within LWE slack, `fail` forced $1 \to 0$): **1000/1000 (100.0%)** recovered the legitimate ground key $K_{ground}$, because message decoding tolerated the perturbation.
   - Direction B2 (Severely corrupted CT, `fail` forced $1 \to 0$): **1000/1000 (100.0%)** selected an out-of-sync candidate key $K_{cand} \neq K_{ground} \neq K_{rej}$ (`CANDIDATE_KEY_SELECTED_MISMATCH`).
5. `SIMULATION-SPECIFIC RESULT` **Telecommand Framing Rejection of Desynchronized Keys:**
   - In unauthenticated communication with mismatched keys ($S \neq G$), **1000/1000 (100.0%)** of frames were rejected at the framing layer as `FORMAT_REJECTED` [95% CI: 99.62% – 100.00%]. Zero garbled payloads were accepted or executed.
   - In authenticated mode (HMAC-SHA256), **1000/1000 (100.0%)** of key mismatches triggered autonomous handshakes that successfully recovered the session (`SESSION_RECOVERED`).

---

### C. What Is Only Hypothesized
1. `HYPOTHESIS` **Hypothesis 1 (RQ1):** That single-bit flips and burst memory upsets disproportionately impact operations with wide intermediate polynomial structures ($k \times 256 \times 16$ bits) compared to compact scalar operations. *(Untested parametrically across wide vs. narrow buffers).*
2. `HYPOTHESIS` **Hypothesis 2 (RQ2):** That ML-DSA exhibits significantly greater structural vulnerability during signing due to rejection sampling loops and infinity-norm checks than ML-KEM decapsulation. *(Untested; ML-DSA has no internal hooks implemented).*
3. `HYPOTHESIS` **Hypothesis 5 (RQ5):** That protecting the top 20% most sensitive sub-routines (selective redundancy) can achieve $>95\%$ fault detection with $<30\%$ computational overhead. *(Untested; resilience modules are empty).*
4. `HYPOTHESIS` **Universal Spacecraft Desynchronization Threat:** The assumption that silent session desynchronization in orbit leads to unrecoverable spacecraft lockouts. *(Hypothesized in overview docs; refuted by our telecommand recovery simulation).*

---

### D. What Is Mathematically Derived
1. `FORMAL RESULT` **NTT Butterfly Error Diffusion Tree:**
   - In `mlkem-native`, the forward NTT consists of 7 layers over $R_q = \mathbb{Z}_{3329}[X]/(X^{256}+1)$.
   - A perturbation $\delta$ introduced at layer $L$ diffuses across $N_{\text{diffused}} = 2^{7-L+1}$ coefficients by layer 7:
     - Layer 1: Diffuses across $2^7 = 128$ coefficients.
     - Layer 4: Diffuses across $2^4 = 16$ coefficients.
     - Layer 7: Diffuses across $2^1 = 2$ coefficients.
2. `FORMAL RESULT` **Centered Binomial Distribution Support:**
   - For ML-KEM-768 ($\eta = 2$), valid noise coefficients strictly satisfy $\text{Supp}(D_2) \in \{-2, -1, 0, 1, 2\}$. Perturbing sampled coefficients ($a - b$) can yield values $\notin [-2, 2]$, violating the mathematical noise distribution.
3. `FORMAL RESULT` **Fujisaki-Okamoto Key Derivation Under Corrupted Ciphertexts:**
   - In FIPS 203 Algorithm 17, when ciphertext $c^*$ is severely corrupted, `indcpa_dec` outputs an incorrect message $m' \neq m$.
   - If the equality check is forced to select the candidate key, it computes $K_{cand} = \text{Hash}_G(m' \parallel H(pk))[0..31]$.
   - Because $m' \neq m$ and $m'$ is computationally uncorrelated with $m$, $K_{cand}$ is an unpredictable, pseudorandom value that matches neither $K_{ground} = \text{Hash}_G(m \parallel H(pk))[0..31]$ nor $K_{rej} = \text{Hash}_J(z \parallel c^*)$.

---

### E. What Is Specification-Derived
1. `SPECIFICATION` All algorithm parameter sets, polynomial degrees ($n=256$), moduli ($q=3329$ for ML-KEM, $q=8380417$ for ML-DSA), compression parameters ($d_u, d_v$), rejection sampling norms ($\gamma_1, \gamma_2, \beta$), and hash functions (SHA3-256, SHAKE-128, SHAKE-256) are strictly derived from NIST FIPS 203 and FIPS 204.
2. `SPECIFICATION` Implicit rejection logic ($K = \text{Hash}_J(z \parallel c)$) is directly specified by FIPS 203 Section 7.3 (Algorithm 17).

---

### F. What Is Implementation-Specific
1. `IMPLEMENTATION-SPECIFIC RESULT` **Cooley-Tukey Butterfly Architecture:**
   - The specific structure of `mlk_ntt_butterfly_block` (7 layers, length halving, bit-reversed twiddle factor ordering) is specific to the `mlkem-native` implementation.
2. `IMPLEMENTATION-SPECIFIC RESULT` **SWAR Popcount Vectorization:**
   - The use of 32-bit bitmask logic (`t & 0x55555555`) in `mlk_poly_cbd2` is an optimization technique specific to C90 `mlkem-native`.
3. `IMPLEMENTATION-SPECIFIC RESULT` **Path A vs. Path B Execution:**
   - Path A executes auto-detected ARM64 NEON SIMD assembly in the Homebrew `liboqs` binary.
   - Path B executes portable C90 scalar code compiled with `-O3` in Apple Clang.

---

### G. What Is Simulation-Specific
1. `SIMULATION-SPECIFIC RESULT` **Telecommand Frame Format:**
   - The 4-byte magic sync word (`0x53504143`), 16-bit sequence counter window, 8-bit subsystem ID, and CRC-16-CCITT checksum implemented in `spacecraft_protocol_sim.py` are specific to our Python abstract model. They reflect CCSDS principles, but do not represent a flight-qualified satellite command decoder.
2. `SIMULATION-SPECIFIC RESULT` **Software Memory Bit-Flips:**
   - The Level 1 Python campaign flips random bits in virtual memory buffers allocated on a macOS host. This simulates an abstract binary symmetric channel, not physical radiation.

---

### H. What Is Currently Claimed as Novel in Repository Docs
*(And the critical reality check on each claim)*

1. *Claimed in docs:* "Novel multi-level fault injection taxonomy (Levels 1 to 4)."  
   *Reality Check:* **NOT NOVEL.** Standard fault injection literature (Patranabis 2020, Ravi 2023) has categorized fault targets into inputs, memory buffers, intermediate registers, and control flow for over a decade.
2. *Claimed in docs:* "First identification of ML-KEM FO transform comparison vulnerability."  
   *Reality Check:* **NOT NOVEL.** Pessl & Prokop (2021), Hermelink et al. (2021), and Jaiswal et al. (2024) published comprehensive papers on this exact topic years ago.
3. *Claimed in docs:* "Demonstrating that space radiation leads to silent spacecraft command execution."  
   *Reality Check:* **FACTUALLY REFUTED.** Our own telecommand simulation proved that pseudorandom decrypted bytes fail framing validation with probability $1 - 2^{-32}$.
4. *Claimed in docs:* "Stage 1 NTT error diffusion absorption by lossy compression."  
   *Reality Check:* **POTENTIALLY NOVEL.** Prior PQC fault papers assumed all arithmetic faults disrupt decapsulation. The mathematical and empirical demonstration that early butterfly diffusion divides error energy below the lossy compression quantization threshold is absent from literature.

---

## 2. Literature Matrix Findings & Landscape Analysis

Our comprehensive literature matrix (`results/literature_matrix.csv`) synthesizes 25 primary academic papers, standards, and engineering handbooks.

```
                                [ LITERATURE LANDSCAPE MAP ]
 ┌───────────────────────────────────────┬───────────────────────────────────────┐
 │ ATTACK LITERATURE (Heavily Saturated) │ DEFENSE & SYSTEMS (Sparse / Gaps)     │
 ├───────────────────────────────────────┼───────────────────────────────────────┤
 │ • FO Transform CCA Bypasses:          │ • Hardware Error Detection:           │
 │   - Pessl & Prokop (TCHES 2021)       │   - Mozaffari-Kermani (TCAD 2023)     │
 │   - Hermelink et al. (INDOCRYPT 2021) │   - Fritzmann et al. (TCAS-I 2022)    │
 │   - Delvaux (TCHES 2022) [Roulette]   │   [FPGA/ASIC ONLY; SW unaddressed]    │
 │   - Jaiswal et al. (TIFS 2024)        │                                       │
 │ • NTT Twiddle Table Zeroization:      │ • Space Communications:               │
 │   - Ravi et al. (TCHES 2023)          │   - ESA E2EQSS Report (2024)          │
 │ • Dilithium Rejection / Norm Faults:  │   - Geissler et al. (IEEE AERO 2023)  │
 │   - Bruinderink & Pessl (CHES 2018)   │   [Link budget only; SEUs ignored]    │
 │   - Krahmer et al. (TCHES 2024)       │                                       │
 └───────────────────────────────────────┴───────────────────────────────────────┘
```

### 2.1 The Existing Attack Landscape
The attack literature on lattice-based PQC is mature and heavily saturated:
- **Active Adversary Assumption:** Virtually all published attacks assume an active attacker who can submit thousands of chosen ciphertexts to a decapsulation oracle (Pessl 2021, Hermelink 2021, Delvaux 2022) or collect thousands of signature pairs (Bruinderink 2018, Krahmer 2024).
- **Goal-Directed Optimization:** Attacks focus on extracting the private key using mathematical solvers (belief propagation, Integer Linear Programming, lattice reduction via BKZ).
- **Physical Hardware Targets:** Attacks are physically demonstrated using laser fault injection (LFI) or electromagnetic fault injection (EMFI) on ARM Cortex-M4 microcontrollers (`pqm4`) or custom FPGAs.

### 2.2 The Existing Countermeasure Landscape
- **Hardware Dominance:** Countermeasures for lattice arithmetic are almost exclusively designed for custom FPGA or ASIC silicon (Mozaffari-Kermani 2023, Fritzmann 2022, Sarker 2024). Techniques like Algebraic Invariant Checking (AIC) and Recomputation with Negated/Swapped Operands (RESWO) achieve $>99.9\%$ fault coverage by modifying RTL butterfly logic.
- **Software Absence:** In pure software running on standard CPUs, proposed countermeasures are primitive: either full dual/triple execution (200%+ overhead) or naive "verify-after-sign". Selective, lightweight software assertions tailored to lattice mathematics are virtually unexplored.

### 2.3 The Space-System Literature
- **Aerospace Radiation Standards:** NASA-HDBK-4002A (2020) and ECSS-Q-ST-60-15C (2020) provide authoritative guidelines on Single Event Upsets (SEUs) and Single Event Functional Interrupts (SEFIs), mandating Triple Modular Redundancy (TMR) and memory scrubbing. However, they contain zero analysis of post-quantum lattice cryptography.
- **Satellite PQC Network Studies:** Recent space communications literature (ESA E2EQSS 2024, Geissler et al. 2023) focuses entirely on communication-layer constraints: packet sizes, link margins, framing fragmentation over CCSDS SDLS, and handshake latency. **No published aerospace paper has evaluated the computational fault resilience of PQC algorithms running on flight processors under ionizing radiation.**

### 2.4 The Formal Verification Literature
- **High-Assurance Baseline:** `mlkem-native` represents the state-of-the-art in verified PQC software, with CBMC proving memory and type safety for C code, and HOL-Light proving constant-time execution and correctness for assembly.
- **The Formal Fault Gap:** All existing formal verification in `mlkem-native` and Jasmin/EasyCrypt assumes *fault-free hardware execution semantics*. Tools like VerFI (Arribas 2021) and FIVER (Richter-Brockmann 2023) verify fault countermeasures, but operate strictly on gate-level hardware netlists using BDDs. **Formal verification of software-level fault resilience in C lattice implementations does not exist.**

---

## 3. Detailed Overlap & Research Gap Analysis

A critical comparison between the literature and our project reveals where we overlap directly and where defensible gaps exist (see `docs/research_overlap_matrix.md` and `docs/state_of_art_gap_analysis.md`).

### Summary of Direct Overlaps (What We Must NOT Claim)
1. **FO Comparison Flag Inversion:** Direct overlap with Pessl (2021), Hermelink (2021), and Jaiswal (2024).
2. **Targeting CBD Sampling:** Direct overlap with Delvaux (2022).
3. **Targeting NTT Butterfly Multipliers:** Direct overlap with Ravi (2023) and Mozaffari-Kermani (2023).
4. **Software Memory Bit-Flips as "Radiation":** Conventional, unnovel proxy.

### Summary of What Existing Work Does Better
- Real physical hardware injection (EMFI / Laser on Cortex-M4).
- Full cryptanalytic key extraction algorithms (ILP / Babai's lattice solvers).
- Physical heavy-ion beam radiation testing.
- Automated gate-level formal fault verification (FIVER).

### Summary of Genuinely Underexplored Areas
1. **The Interaction of Linear Error Diffusion and Lossy Compression Rounding:** How multi-stage NTT error dispersion interacts with the non-linear quantization boundaries of FIPS 203 compression.
2. **Cross-Implementation Fault Divergence:** Comparing formally verified portable C90 (`mlkem-native`) with dynamically linked SIMD C (`liboqs`) under identical fault models.
3. **Software-Only Selective Algorithmic Resilience:** Designing sub-30% overhead assertions for flight processors without custom FPGA silicon.
4. **Cryptographic Fault $\to$ Telecommand Framing Propagation:** Connecting algorithmic session desynchronization to multi-stage telecommand rejection and autonomous satellite recovery.

---

## 4. The 10-Layer Research Architecture

To ensure the project maintains structural integrity across all dimensions, we propose a comprehensive **10-Layer Research Architecture**. 

Based on our gap analysis, we explicitly indicate the **recommended research effort allocation** across these layers:

```
[ LAYER 10: FORMAL VALIDATION ]           (Effort: LOW-MEDIUM) - CBMC fault-contract feasibility
       ▲
[ LAYER 9: SPACE-SYSTEM RELEVANCE ]        (Effort: HIGH) - Connect to CCSDS TC / SDLS framing
       ▲
[ LAYER 8: PROTOCOL / SYSTEM IMPACT ]      (Effort: HIGH) - Telecommand receiver state machine
       ▲
[ LAYER 7: RESILIENCE ]                    (Effort: VERY HIGH) - Selective software assertions
       ▲
[ LAYER 6: SECURITY ANALYSIS ]             (Effort: MEDIUM) - Disambiguate SDC vs key recovery
       ▲
[ LAYER 5: OUTCOME CLASSIFICATION ]        (Effort: HIGH) - Statistical sweeps & 95% CIs
       ▲
[ LAYER 4: FAULT PROPAGATION ]             (Effort: VERY HIGH) - Diffusion vs Quantization bounds
       ▲
[ LAYER 3: FAULT INJECTION ]               (Effort: HIGH) - Deterministic mid-op hooks
       ▲
[ LAYER 2: IMPLEMENTATION ]                (Effort: HIGH) - Dual-engine (mlkem-native vs liboqs)
       ▲
[ LAYER 1: MATHEMATICS ]                   (Effort: VERY HIGH) - Ring R_q, NTT, CBD, FO transform
```

### Layer Descriptions & Strategic Focus
- **Layer 1 (Mathematics) [VERY HIGH EFFORT]:** Formalize the polynomial ring $R_q = \mathbb{Z}_q[X]/(X^n+1)$, Cooley-Tukey NTT butterfly tree, Centered Binomial Distribution support, and FIPS 203 compression rounding intervals. Derive closed-form error bounds.
- **Layer 2 (Implementation) [HIGH EFFORT]:** Maintain strict separation between Path A (`liboqs`) and Path B (`mlkem-native` / `mldsa-native`). Complete FIPS 204 instrumentation.
- **Layer 3 (Fault Injection) [HIGH EFFORT]:** Maintain deterministic mid-operation hooks inside active transform loops. Expand hooks to ML-DSA rejection loops and norm checks.
- **Layer 4 (Fault Propagation) [VERY HIGH EFFORT]:** Trace intermediate arithmetic mutations through downstream operations. Mathematically characterize the threshold where error energy exceeds compression quantization.
- **Layer 5 (Outcome Classification) [HIGH EFFORT]:** Classify all outcomes into standard categorical bins (Correct, Implicit Rejection, Candidate Mismatch, Rejection Loop Hang, Crash) with Wilson 95% confidence intervals.
- **Layer 6 (Security Analysis) [MEDIUM EFFORT]:** Strictly disambiguate correctness degradation from actual cryptanalytic breaks. Avoid claiming "security breaks" when outputs are merely desynchronized.
- **Layer 7 (Resilience) [VERY HIGH EFFORT]:** Engineer lightweight, software-only assertions (norm sanity checks, polynomial checksums) that protect sensitive stages (NTT Layers 4–7, accumulators) with $<25\%$ CPU overhead.
- **Layer 8 (Protocol / System Impact) [HIGH EFFORT]:** Map cryptographic outcomes into multi-stage telecommand receiving pipelines. Evaluate packet dropping, sequence tracking, and framing validation.
- **Layer 9 (Space-System Relevance) [HIGH EFFORT]:** Ground the abstract model in published space communication standards (CCSDS 355.0-B-1 SDLS). Explicitly distinguish software fault models from physical radiation.
- **Layer 10 (Formal Validation) [LOW-MEDIUM EFFORT]:** Evaluate the feasibility of using CBMC function contracts to verify that proposed resilience assertions detect single-bit corruptions. Do not allow formal verification complexity to stall empirical progress.

---

## 5. Candidate Research Contributions

We present four distinct candidate research contributions. In accordance with strict academic guidelines, these are **NOT ranked numerically or labeled as "best"**. Each contribution is evaluated across eight standardized dimensions:

---

### Candidate Contribution 1: Analytical and Empirical Characterization of NTT Error Diffusion vs. Quantization Absorption in Module-Lattice KEMs

1. **Contribution Statement:**  
   We prove analytically and demonstrate empirically that in module-lattice key encapsulation mechanisms utilizing Cooley-Tukey NTT and lossy ciphertext compression (NIST FIPS 203), internal arithmetic perturbations exhibit a sharp, layer-dependent dichotomy: early butterfly perturbations diffuse across 128 coefficients and are completely absorbed by downstream compression quantization rounding ($100\%$ valid decapsulation), whereas late-stage perturbations remain localized and trigger implicit rejection ($100\%$).
2. **Existing Literature Overlap:**  
   Prior NTT fault literature (Ravi et al. TCHES 2023, Delvaux TCHES 2022) studied isolated butterfly units or static twiddle tables, assuming any arithmetic disruption causes catastrophic failure. The interaction between linear butterfly error dispersion and non-linear ciphertext compression rounding has never been published.
3. **Why It Is Interesting:**  
   It reveals an inherent, previously uncharacterized *self-healing property* in ML-KEM: the algorithm naturally absorbs a significant class of transient computational faults without requiring expensive redundancy countermeasures.
4. **What Must Be Experimentally Demonstrated:**  
   - Formal algebraic proof of maximum fault magnitude $|\delta|_{\max}$ absorbed by `Compress_d` as a function of NTT layer $L \in \{1 \dots 7\}$.
   - Complete empirical validation across all three parameter sets: ML-KEM-512 ($d_u=10, d_v=4$), ML-KEM-768 ($d_u=10, d_v=4$), and ML-KEM-1024 ($d_u=11, d_v=5$) across $N \ge 1,000$ trials per stage.
5. **What Would Make It Publishable:**  
   Publishable in top hardware security / cryptographic engineering venues (e.g., IACR TCHES, IEEE TIFS) as a definitive study on the arithmetic fault propagation dynamics of the finalized FIPS 203 standard.
6. **Novelty Confidence:**  
   **HIGH.** Directly substantiated by our Phase 4B audit; no prior publication identifies or models this absorption boundary.
7. **Major Risk:**  
   Reviewers might argue that error absorption in lossy compression is an intuitive signal-processing property. The paper must emphasize its specific cryptographic implications on IND-CCA2 decapsulation and implicit rejection.
8. **Required Future Work:**  
   Derive closed-form mathematical bounds and extend the test harness to ML-KEM-512 and ML-KEM-1024.

---

### Candidate Contribution 2: End-to-End Cryptographic Fault Propagation into Spacecraft Telecommand Protocol Architectures

1. **Contribution Statement:**  
   We establish an end-to-end framework connecting implementation-level post-quantum cryptographic faults (in ML-KEM decapsulation) to downstream spacecraft telecommand communication protocols, proving that cryptographic session desynchronization results in $100\%$ framing rejection ($p \ge 1 - 2^{-32}$) rather than silent command execution, and characterizing autonomous link recovery latency.
2. **Existing Literature Overlap:**  
   Space communication literature (ESA E2EQSS 2024, Geissler 2023) evaluates PQC exclusively under normal channel conditions (latency, packet sizes). Cryptographic fault literature evaluates PQC exclusively at the function return boundary. Neither connects internal cryptographic failure modes to multi-stage telecommand framing and autonomous recovery.
3. **Why It Is Interesting:**  
   It bridges the gap between cryptographic hardware security and aerospace systems engineering, directly refuting the widespread assumption that Silent Data Corruption (SDC) in cryptographic decapsulation leads to catastrophic, silent execution of corrupted satellite commands.
4. **What Must Be Experimentally Demonstrated:**  
   - Full integration with standard CCSDS Space Data Link Protocol framing structures.
   - Parametric sweeps measuring frame drop rates, sequence counter desynchronization, and autonomous retransmission latency across orbital bit error rates (BER).
5. **What Would Make It Publishable:**  
   Publishable in premier aerospace and dependability venues (e.g., IEEE Aerospace Conference, IEEE Transactions on Dependable and Secure Computing, AIAA Scitech).
6. **Novelty Confidence:**  
   **HIGH.** No published paper models this specific crypto-to-telecommand failure propagation chain.
7. **Major Risk:**  
   Cryptographic reviewers may view it as "applied protocol engineering," while aerospace reviewers may demand physical satellite hardware-in-the-loop. The paper must be targeted at aerospace security tracks.
8. **Required Future Work:**  
   Formalize the framing specification to match standard CCSDS Telecommand (TC) Green/Blue books and implement automated retransmission state machines.

---

### Candidate Contribution 3: Sensitivity-Guided Selective Software Resilience for Lattice Cryptography on Embedded Space Processors

1. **Contribution Statement:**  
   We propose and evaluate a software-only, sensitivity-guided selective resilience architecture for standardized lattice cryptography (ML-KEM and ML-DSA) that protects only highly vulnerable computational stages (NTT Layers 4–7, vector accumulators, and rejection norm checks), achieving $>95\%$ fault detection coverage with $<25\%$ CPU overhead, outperforming naive full execution duplication.
2. **Existing Literature Overlap:**  
   Hardware error detection for NTT on FPGAs/ASICs is heavily published (Mozaffari-Kermani 2023, Fritzmann 2022). However, software-only resilience for general-purpose embedded processors (e.g., space-grade RISC-V or SPARC/LEON) is virtually unstudied, with existing implementations defaulting to 200% full duplication.
3. **Why It Is Interesting:**  
   Spaceflight computers (e.g., RAD750, GR740) operate under severe SWaP-C (Size, Weight, Power, and Cost) constraints. A lightweight software countermeasure that provides high fault coverage without requiring custom hardware silicon or doubling CPU cycles is highly practical and valuable.
4. **What Must Be Experimentally Demonstrated:**  
   - Concrete design and implementation of lightweight software assertions (norm boundary checks, modular polynomial checksums) in `mlkem-native` and `mldsa-native`.
   - Cycle-accurate execution benchmarks measuring exact CPU overhead.
   - Comprehensive fault injection campaign ($N \ge 10,000$) demonstrating $>95\%$ detection coverage.
5. **What Would Make It Publishable:**  
   Publishable in applied security and embedded systems venues (e.g., ACM TECS, IEEE TCAD, DATE, CHES).
6. **Novelty Confidence:**  
   **MEDIUM-HIGH.** The concept of selective protection is established in classical computing, but its specific mathematical adaptation and sensitivity-guided tuning for FIPS 203/204 software is novel.
7. **Major Risk:**  
   Reviewers may compare software overhead against hardware FPGA overhead and demand ASIC-level performance. The paper must explicitly frame the contribution around software deployment on existing, non-reconfigurable flight processors.
8. **Required Future Work:**  
   Implement the concrete assertion hooks in `resilience/integrity_checks/` and benchmark on ARM Cortex / RISC-V targets.

---

### Candidate Contribution 4: Cross-Implementation Fault Behavior and Formal Safety Divergence in Standardized PQC

1. **Contribution Statement:**  
   We conduct a comparative empirical fault resilience analysis between a formally verified C90 implementation (`mlkem-native`) and a SIMD-optimized dynamically linked library (`liboqs`), demonstrating how compiler optimizations, inlining, and formal contract structures alter intermediate fault sensitivity.
2. **Existing Literature Overlap:**  
   Compiler-induced timing leakage has been studied, but cross-implementation fault injection across verified vs. unverified PQC codebases is unaddressed. Most papers study a single implementation and generalize indiscriminately.
3. **Why It Is Interesting:**  
   It addresses a critical question for high-assurance systems: does formally proving memory/type safety (via CBMC) make a software implementation more or less robust to physical computational faults?
4. **What Must Be Experimentally Demonstrated:**  
   - Identical fault models executed across both `mlkem-native` and `liboqs` under matched seeds.
   - Statistical quantification of outcome divergence caused by compiler vectorization.
5. **What Would Make It Publishable:**  
   Publishable in software engineering and security venues (e.g., USENIX Security, IEEE S&P, ACM CCS).
6. **Novelty Confidence:**  
   **MEDIUM.** Highly dependent on whether significant, meaningful divergence is observed.
7. **Major Risk:**  
   If both codebases exhibit virtually identical fault distributions, the research value is diminished.
8. **Required Future Work:**  
   Instrument Path A with equivalent mid-operation hooks or assembly-level breakpoints and execute comparative sweeps.

---

## 6. Recommended Next Phase & Required Experiments

To transition from Phase 0 to Phase 1 with maximum scientific defensibility, we recommend focusing on a **Unified Research Narrative** combining:
- **Candidate Contribution 1 (Quantization Absorption Mathematics)**
- **Candidate Contribution 2 (Telecommand Protocol Mapping)**
- **Candidate Contribution 3 (Selective Software Resilience)**

```
                                [ PHASE 1 EXECUTION PLAN ]
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ WORKSTREAM 1: Mathematical Quantization Modeling                                      │
 │ • Derive closed-form bounds: |delta|_max vs L in {1..7} for FIPS 203                   │
 │ • Validate across ML-KEM-512, 768, 1024 (N=1000 per cell)                             │
 ├────────────────────────────────────────────────────────────────────────────────────────┤
 │ WORKSTREAM 2: ML-DSA-Native Instrumentation                                            │
 │ • Implement mid-operation hooks for FIPS 204 (rejection sampling, infinity-norm checks)│
 │ • Quantify rejection loop hang probability and signature corruption distributions      │
 ├────────────────────────────────────────────────────────────────────────────────────────┤
 │ WORKSTREAM 3: Selective Software Resilience Engine                                     │
 │ • Implement lightweight assertions in resilience/integrity_checks/                    │
 │ • Benchmark CPU overhead on ARM/Apple Silicon; prove >95% coverage with <25% penalty   │
 ├────────────────────────────────────────────────────────────────────────────────────────┤
 │ WORKSTREAM 4: Spacecraft Framing Protocol Formalization                               │
 │ • Align telecommand simulator with CCSDS 355.0-B-1 (SDLS) standard                     │
 │ • Measure autonomous session recovery latency across simulated orbital bit error rates │
 └────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. STOP POINT

To ensure absolute adherence to scientific rigor, the state of the project at the conclusion of Phase 0 is defined as follows:

### What We Know
1. `VERIFIED FACT` The repository has verified, bit-accurate KAT test vectors for all 6 parameter sets across FIPS 203 (ML-KEM-512/768/1024) and FIPS 204 (ML-DSA-44/65/87).
2. `EMPIRICAL RESULT` In `mlkem-native`, single-bit perturbations in Layer 1 of the forward NTT diffuse across 128 coefficients and are completely absorbed by lossy compression rounding ($d_u=10, d_v=4$), resulting in 100.0% legitimate decapsulation.
3. `EMPIRICAL RESULT` Inverting the FO verification predicate under corrupted ciphertext does not recover the legitimate key, but produces an invalid, desynchronized candidate key ($K_{cand} \neq K_{ground} \neq K_{rej}$).
4. `SIMULATION-SPECIFIC RESULT` Mismatched session keys in our telecommand receiver simulation result in 100.0% framing rejection ($p \approx 1 - 2^{-32}$) rather than silent command execution.

### What We Do Not Know
1. `HYPOTHESIS` We do not know whether the quantization absorption threshold holds symmetrically across ML-KEM-512 and ML-KEM-1024.
2. `HYPOTHESIS` We do not know how ML-DSA-native behaves under mid-operation rejection sampling faults (hooks are not yet implemented).
3. `HYPOTHESIS` We do not know whether selective software assertions can actually achieve $>95\%$ fault coverage with $<25\%$ overhead in production C code.
4. `HYPOTHESIS` We do not know the exact divergence in fault sensitivity between `mlkem-native` and `liboqs`.

### What Is Already Established in Literature
1. `LITERATURE CLAIM` Bypassing the Fujisaki-Okamoto re-encryption comparison flag reduces CCA security to CPA and enables chosen-ciphertext key recovery (Pessl 2021, Hermelink 2021, Jaiswal 2024).
2. `LITERATURE CLAIM` Zeroizing NTT twiddle factors collapses polynomial multiplication entropy (Ravi 2023).
3. `LITERATURE CLAIM` Deterministic Dilithium signing is vulnerable to Differential Fault Analysis (Bruinderink 2018).
4. `LITERATURE CLAIM` Hardware-level error detection (AIC, RESWO) detects $>99.9\%$ of NTT faults on FPGAs (Mozaffari-Kermani 2023).

### What May Be Underexplored
1. Analytical and empirical modeling of intermediate NTT butterfly error diffusion against non-linear lossy compression quantization rounding thresholds.
2. End-to-end propagation of PQC cryptographic session desynchronization into CCSDS-compliant telecommand framing pipelines and autonomous recovery.
3. Software-only selective algorithmic resilience for lattice PQC running on general-purpose embedded space processors.

### What Should NOT Yet Be Claimed as Novel
1. **DO NOT CLAIM** that FO transform comparison vulnerability is our discovery.
2. **DO NOT CLAIM** that software bit-flips prove spacecraft radiation hardness.
3. **DO NOT CLAIM** that NTT faults universally cause implicit rejection (Layer 1 proves otherwise).
4. **DO NOT CLAIM** that ML-KEM desynchronization leads to silent satellite command execution.

### What Phase 1 Should Implement
1. Derive closed-form mathematical error bounds for quantization absorption in FIPS 203.
2. Instrument mid-operation fault hooks in `mldsa-native` (rejection loop and norm checks).
3. Implement lightweight software assertions in `resilience/` and benchmark CPU overhead.
4. Formalize the spacecraft framing simulator against CCSDS SDLS standards.
