# CHECKPOINT: PQC NTT Fault Resilience Research (`pqc-ntt-fault-resilience`)

**Preserved Checkpoint Identifier:** `pqc-ntt-fault-resilience-v1`  
**Preservation Tag:** `pqc-ntt-fault-resilience-v1`  
**Archival Branch:** `archive/pqc-ntt-fault-resilience`  
**Baseline Git Commit:** `6eadeb0423d06a1535568073ad47e4de7489d1d0`  
**Date of Checkpoint:** October 2026  
**Repository:** [https://github.com/dhairyajain/pqc-research](https://github.com/dhairyajain/pqc-research)  

---

## 1. What This Preserved Project Contains

This checkpoint captures the complete, self-contained, reproducible research implementation and experimental validation of:
**"Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"**

The core technical assets preserved in this state comprise:
1. **Target Cryptosystems:**
   - NIST FIPS 203 (ML-KEM / CRYSTALS-Kyber-768) key encapsulation mechanism.
   - NIST FIPS 204 (ML-DSA / CRYSTALS-Dilithium-65) digital signature algorithm.
   - Native C99 reference implementations (`algorithms/source_ref/`).
2. **Mathematical Invariant Derivations:**
   - Forward Cooley-Tukey (CT) butterfly dual invariant system:
     $$u' + v' \equiv 2u \pmod q \quad \text{and} \quad u' - v' \equiv 2v\zeta \pmod q$$
   - Inverse Gentleman-Sande (GS) butterfly decoupled invariant system:
     $$u' \equiv u + v \pmod q \quad \text{and} \quad v' \equiv \zeta(u - v) \pmod q$$
   - Algebraic error kernel intersection proofs ($\ker(\Delta_{\text{sum}}) \cap \ker(\Delta_{\text{diff}}) = \{(0,0)\}$).
3. **In-Tree Native Software Monitoring Architecture:**
   - Full instrumentation covering all **9,856 butterflies** across ML-KEM-768 decapsulation ($2{,}688$ vector forward + $2{,}688$ secret-key vector forward + $4{,}480$ message-recovery inverse).
   - Zero-heap dynamic allocation (executed strictly within stack and register frames).
   - Constant-time compliance, preserving ABI stability and timing distribution ($Cohen's\ d = 0.0008, p > 0.05$).
4. **Autonomous In-Place Register Rollback (Tier 1):**
   - Register-resident shadow operand preservation and single-butterfly in-place recomputation.
   - Validated across 1,400 clean-room trials yielding a **100% transient fault recovery rate** and **0% undetected silent data corruption (SDC)**.
5. **Standard-Compliant Fail-Stop Hardening (Tier 2):**
   - Unconditional escalation to NIST FIPS 203 Section 7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) upon persistent or uncorrectable faults.
   - Public API protection: caller omission of status return pointers (`mlkem768_dec(ss, ct, sk)`) strictly forces safe rejection without secret-key or plaintext leakage.
6. **Empirical Overhead Characterization vs. DMR:**
   - Native dual-butterfly monitoring latency: **+16.79% to +28.91%** overhead.
   - Software-sequential Dual Modular Redundancy (DMR) baseline: **+140.3% to +160.8%** overhead.
   - Confirmed **5.2$\times$ to 8.1$\times$ overhead reduction** in CPU cycle latency.
7. **Comprehensive Research & Literature Documentation:**
   - Full phase reports from Phase 2 through Phase 7L located in `docs/`.
   - Systematic literature matrix, citation log, and BibTeX file in `docs/phase7l/`.

---

## 2. Original Research Scope & Objectives

The research was formulated to address:
> *"Can native, in-place arithmetic invariant checking and register rollback across all forward and inverse NTT butterflies provide complete transient fault recovery and safe implicit rejection in ML-KEM-768 decapsulation, while significantly reducing latency overhead compared to software-sequential DMR?"*

The scope was bounded strictly to:
- Arithmetic butterflies of the Number Theoretic Transform.
- Single-event transient upsets (SEUs) modeled in CPU registers during single execution cycles.
- Single-core software execution (tested on Apple Silicon AArch64 and portable to ARM Cortex-M4/R5/A53).

---

## 3. Important Experiment and Reproducibility Instructions

To reproduce the validated results from this checkpoint:

### A. Clean-Room Regression & Verification Suite
Run the automated end-to-end regression test suite:
```bash
make test-phase7k
```
This target verifies:
- Phase 7J raw data integrity and 1,600-trial extended campaign metrics.
- All 9,856 native butterfly executions and zero undetected corruptions.
- Multi-run benchmark latencies (Baseline, Forward-Only, Inverse-Only, Combined, DMR).
- Randomized constant-time Kolmogorov-Smirnov and Welch t-tests.
- Symbolic error-kernel algebraic proofs in Python.

### B. NIST FIPS 203 & 204 Known Answer Test (KAT) Runner
To verify bit-level adherence to NIST cryptographic standards across all security levels:
```bash
make bin/test_fips_kats
./bin/test_fips_kats
```
Expected output: 100% PASS across ML-KEM-512/768/1024 and ML-DSA-44/65/87.

### C. Re-running the 1,400-Trial Fault Injection Campaign
```bash
make bin/phase7j_independent_validator
./bin/phase7j_independent_validator
```

---

## 4. Known Limitations & Unverified Assumptions

1. **Software Fault Injection vs. Physical Radiation:**
   All fault experiments use Software-Implemented Fault Injection (SWIFI) at instruction boundaries. They do **not** emulate sub-cycle analog glitching, single-event latchup (SEL), or total ionizing dose (TID). This work proves *architectural and algorithmic resilience*, not physical radiation qualification under ECSS-Q-ST-60-15C.
2. **Twiddle Factor Common-Mode Blind Spot:**
   If a physical upset permanently flips bits in the static twiddle lookup table (`const int16_t zetas[128]`), both the primary butterfly computation and the difference invariant evaluate with the same corrupted twiddle, rendering the fault invisible to local butterfly checks. Protection against twiddle corruption requires external memory integrity verification (e.g., CRC or EDAC).
3. **Single-Butterfly Fault Model:**
   The 100% recovery guarantee applies to isolated transient faults occurring within a single butterfly. Simultaneous multi-bit upsets corrupting both primary registers and shadow copies trigger safe Tier 2 implicit rejection, not Tier 1 recovery.

---

## 5. How to Return to This Checkpoint

To inspect or restore this preserved research state at any time in the future:

```bash
# 1. Fetch tags and branches
git fetch origin --tags

# 2. Check out the archival branch
git checkout archive/pqc-ntt-fault-resilience

# Or check out the exact immutable tag
git checkout tags/pqc-ntt-fault-resilience-v1

# 3. Verify clean reproducibility
make test-phase7k
```
