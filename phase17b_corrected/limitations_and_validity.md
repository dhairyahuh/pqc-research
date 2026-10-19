# Comprehensive Statement of Limitations and Threats to Validity

**Phase:** Phase 17B  
**Date:** October 2026  
**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Purpose:** Establish transparent epistemological boundaries for the ML-KEM-768 fault-resilience architecture to ensure defensibility under rigorous academic peer review.

---

## 1. Experimental Limitations

### 1.1. Host Platform vs. Target Space Microprocessors
- **Evaluated Environment:** All empirical trials were compiled and executed on a desktop workstation running macOS AArch64 (Apple Silicon M-series) using Apple Clang 15.0 (`-O2`).
- **Target Deployment Context:** Autonomous space payloads, cubesats, and satellites typically employ radiation-hardened or fault-tolerant embedded processors, such as:
  - Cobham Gaisler LEON3 / LEON4 (SPARC V8 architecture, typically clocked at 50–150 MHz).
  - Microchip AT697F (SPARC V8).
  - NOEL-V or RISC-V RV32IM/RV64GC fault-tolerant soft cores implemented on space-grade FPGAs (e.g., Microchip RT PolarFire, Xilinx Virtex-5QV).
- **Threat to Validity:** Microarchitectural behavior differs substantially between high-performance superscalar desktop CPUs (deep out-of-order execution pipelines, multi-level caches, register renaming) and in-order embedded space cores. Specifically:
  - Register pressure from local snapshot variables may force stack spilling on register-constrained cores (such as RISC-V RV32 with 32 registers or SPARC V8 with register windows).
  - Memory bus arbitration and L1 cache line replacement under cache misses may alter the runtime latency overhead reported (+25.3%).

### 1.2. Software-Implemented Fault Injection vs. Physical Radiation
- **Simulation Mechanism:** Faults were introduced via in-tree C software hooks (`-DMLKEM_RESEARCH_FAULT_HOOKS`) compiled directly into `poly.c` and `kem.c`.
- **Physical Reality:** In orbital radiation environments (Low Earth Orbit, Geostationary Orbit, Deep Space), galactic cosmic rays and solar energetic particles deposit charge along physical ionization tracks in silicon, producing:
  - Single Event Transients (SET) on clock trees, power rails, and combinatorial logic.
  - Multi-Bit Upsets (MBU) across adjacent memory cells.
  - Single Event Latch-up (SEL), potentially causing destructive overcurrent.
- **Threat to Validity:** Software fault injection operates at the architectural state level (post-instruction retirement) and cannot model:
  - Sub-cycle race conditions or setup/hold violations.
  - Analog power droop induced by particle strikes.
  - Glitches affecting instruction decoders or control logic before arithmetic execution.

---

## 2. Statistical Limitations and Bounds

### 2.1. Finite Sample Bounds on Silent Data Corruption (SDC)
- Across 300 active software fault-injection trials (100 each for $F4$, $F5A$, $F5B$), zero SDC events were observed ($0 / 300$).
- Using the 95% Wilson score confidence interval, the true SDC probability is bounded by:
  $$P_{\text{SDC}} \in [0.00\%, 1.26\%]$$
- **Academic Limitation:** Observing zero events in 300 trials does **not** prove mathematical impossibility of SDC. Rare fault combinations (such as an arithmetic fault that simultaneously alters a polynomial coefficient and evades the difference invariant while maintaining an algebraic relation) may occur with probability $p \ll 1/300$.

### 2.2. Harness Model vs. Production Sampling
- Characterization of circular verifier blindness ($H_1$) was performed on standalone software harness models where memory corruption was simulated across six target loci ($F1, F2, F6, F7, F9, F10$).
- While this proves that co-located snapshots are fundamentally susceptible to common-mode failure, the trial counts in early harness runs were variable. The production code mitigates this by placing snapshots in compiler-managed local variables, but production testing was conducted on specific fault targets ($F4, F5A, F5B$).

---

## 3. Implementation Limitations

### 3.1. Compiler Optimization and Snapshot Register Allocation
- The resilience of localized rollback depends upon pre-butterfly operands $(u, v)$ residing in CPU registers rather than being spilled to vulnerable stack memory.
- In modern compilers (Clang/GCC with `-O2`), small local scalar variables in tight loops are prioritized for register allocation. However:
  - If compiled with `-O0` or under extreme register pressure, the compiler will spill these variables to the stack frame.
  - If stack memory is hit by an SEU, the snapshot is vulnerable to the same co-located memory corruption demonstrated in $H_1$.

### 3.2. Twiddle Factor Table Blind Spot
- The algebraic invariants ($r_0 + r_1 \equiv 2u$, $r_0 - r_1 \equiv 2\zeta v$, $r_0 + \zeta r_1 \equiv 2u$) explicitly evaluate polynomial coefficients against the twiddle factor $\zeta$.
- If an SEU corrupts the static table containing $\zeta$ values in memory, the invariant equations evaluate using the corrupted $\zeta$ reference.
- **Consequence:** Butterfly invariants cannot detect twiddle table corruption. A secondary defense (e.g., CRC-32 integrity checking of constant tables or ROM parity) is mandatory for complete hardware hardening.

### 3.3. Fujisaki-Okamoto Comparison Loop Bypass
- While `kem.c` incorporates a dual-rail comparison check (`fail != fail_chk`), a physical laser fault injection or clock glitch that forces the processor program counter (PC) to skip the conditional branch instruction entirely will bypass both comparison rails.
- Software-level dual-rail defenses protect against data-path upsets, not physical instruction-skip attacks.

---

## 4. Threat-Model Boundaries

### 4.1. The SIFA Boundary
- Dobraunig et al. (TCHES 2018) prove that conditional retry under active fault injection enables Statistical Ineffective Fault Attacks (SIFA), leaking secret keys through the distribution of non-aborted runs.
- **Strict Boundary:** The localized rollback and retry mechanism presented in this work is valid **strictly within non-adversarial operating environments** (e.g., natural cosmic ray SEUs in space or avionics).
- In any operational environment where physical access or active fault injection (EMFI, laser, voltage glitching) is plausible, **retry must be disabled**, and the implementation must operate exclusively in detection-only fail-stop mode.

### 4.2. Software Force-Value Semantics (Target F5B)
- Target $F5B$ simulates register failure by forcing an intermediate local variable to zero (`*t = 0`).
- This models software variable zeroing (useful for testing failsafe escalation logic), but must not be conflated with physical semiconductor stuck-at faults, hardware bus shorts, or gate oxide breakdown.

---

## 5. Microarchitectural and Timing Side-Channel Limitations

### 5.1. Absence of Formal TVLA / dudect Verification
- Source code in `verify.c` and `poly.c` uses constant-time conditional selection masks (`mlk_ct_cmov`).
- On clean execution paths, execution timing is uniform (measured at $1.0005\times$ relative to unprotected baselines on desktop microbenchmarks).
- **Limitation:** Activating the recovery path introduces conditional branches upon error detection. Furthermore, no formal microarchitectural timing leakage analysis (Test Vector Leakage Assessment - TVLA, or dudect Welch's t-test) has been performed on compiled binaries. Certified constant-time security is explicitly not claimed.
