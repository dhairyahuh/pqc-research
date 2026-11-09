# Progress Presentation Outline & Speaker Handbook
## Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
### Initial Case Study: Software-Level Fault Resilience for ML-KEM-768 Decapsulation

**Presentation Target Duration:** 12–15 Minutes  
**Audience:** Computer Science Faculty, Cryptography Reviewers, and Aerospace Avionics Panel  
**Primary Presenter Goal:** Present the overall space-system research programme, showcase the initial ML-KEM-768 implementation progress and empirical evidence ($0$ SDC, $100\%$ recovery, $+16.9\%$ overhead), candidly discuss scientific limitations, and present the 7-work-package roadmap toward full spacecraft integration.

---

## Slide-by-Slide Presentation Structure (Exactly 11 Slides)

```text
Slide 01: Title Slide — Research Programme Overview
Slide 02: Introduction — Post-Quantum Cryptography & Space Systems
Slide 03: Research Background & Problem Statement — Cryptographic Faults in Space
Slide 04: Research Objectives & Scope — The Three-Level Research Programme
Slide 05: Proposed Research Framework — Multi-Tier Methodology & Defensive Stack
Slide 06: Work Completed So Far: ML-KEM-768 — Initial Implementation Target
Slide 07: Implemented Fault-Resilience Architecture — Dual Invariants & Local Rollback
Slide 08: Experimental Results & Validation — Production Benchmarks & Containment
Slide 09: Current Limitations & Research Gaps — Scope Boundaries of Completed Work
Slide 10: Future Work & Research Expansion — Seven Broad Space-System Work Packages
Slide 11: Conclusion & Research Roadmap — Summary & Long-Term Horizon
```

---

### Slide 01: Title Slide — Research Programme Overview
- **Slide Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
- **Subtitle:** Investigating Cryptographic Reliability, Localized Recovery, and Containment Under Orbital Fault Environments
- **Case Study Subheading:** Initial Implementation Focus: Software-Level Fault Resilience for ML-KEM-768 Decapsulation
- **Visuals / Artifacts to Show:** Title block, NIST FIPS 203 logo, space radiation background icon, and 2×2 metric panel.
- **Key Bullet Points:**
  - Standardized PQC: Transitioning space communications to NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA).
  - The Space Environment: Radiation-induced bit-flips threaten cryptographic reliability.
  - Initial Implementation: Evaluated on ML-KEM-768 (9,856 operations monitored, 0 SDC across 300 active trials).
  - Multi-Stage Vision: Software foundation extending toward full spacecraft system integration.
- **Speaker Notes (~60s):**  
  *"Good morning, esteemed committee members. Today I am presenting our research titled 'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems.' As spaceborne computing platforms transition to post-quantum cryptography, they face extreme operating conditions—such as cosmic radiation and single-event upsets—that threaten cryptographic reliability. In this presentation, I will outline our broader space-systems research programme, present our initial implementation-level progress on ML-KEM-768 decapsulation, discuss the empirical findings and limitations, and map out the remaining research required for full spacecraft integration."*

---

### Slide 02: Introduction — Post-Quantum Cryptography & Space Systems
- **Slide Title:** Post-Quantum Cryptography in Spaceborne Environments
- **Visuals:** Shor's algorithm threat vs. Lattice hardness diagram; satellite orbital paths (LEO, GEO, Deep Space).
- **Key Bullet Points:**
  - NIST finalized post-quantum standards in August 2024: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA).
  - Spacecraft lifespans span 10–25 years; telecommand and telemetry require immediate quantum-safe security.
  - Outside atmospheric shielding, cosmic rays and solar protons cause Single-Event Effects (SEUs and SETs).
  - Modern constellations deploy COTS microprocessors that lack full hardware radiation hardening.
- **Speaker Notes (~60s):**  
  *"Post-quantum cryptography is no longer a theoretical exercise—NIST standardized ML-KEM and ML-DSA in August 2024. Space systems must adopt these algorithms immediately because satellite hardware launched today will remain operational well into the era of quantum computing. However, space platforms operate in an environment flooded with ionizing radiation. When an energetic particle strikes a microprocessor, it causes a bit-flip. Because modern satellite constellations increasingly use high-performance commercial microcontrollers rather than slow, expensive radiation-hardened chips, software-level fault resilience is essential."*

---

### Slide 03: Research Background & Problem Statement
- **Slide Title:** Cryptographic Vulnerabilities Under Hardware Faults
- **Visuals:** SDC vs. Unavailability decision tree; comparison chart showing DMR (+99.33%) and circular verifier blindness (98.5%).
- **Key Bullet Points:**
  - Silent Data Corruption (SDC): Undetected bit-flips corrupt secret keys, risking protocol breakdown or key leakage.
  - Denial of Service / Unavailability: Unhandled faults cause full aborts, triggering link renegotiation storms in space.
  - Hardware ECC Reality: Hardware ECC availability varies across COTS embedded platforms.
  - Circular Verifier Blindness: Naive checkers reading live faulted registers fail 98.5% of the time (591/600 trials).
- **Speaker Notes (~60s):**  
  *"When a hardware fault strikes an algorithm like ML-KEM during decapsulation, two bad things can happen. First, Silent Data Corruption: the algorithm finishes and outputs a corrupted key without knowing it, breaking encrypted communications. Second, Denial of Service: the system catches an error and aborts completely. In space communications, where link windows are short and latency is high, repeated full aborts cause communication link collapse. Running the algorithm twice—Dual Modular Redundancy—costs nearly 100% overhead at the transform level, which battery-constrained CubeSats cannot afford. And naive software checks fail 98.5% of the time due to circular blindness."*

---

### Slide 04: Research Objectives & Scope
- **Slide Title:** Research Objectives Across the Three-Level Programme
- **Visuals:** Three-tier hierarchical architecture pyramid (Level A: Programme $\to$ Level B: Initial Case Study $\to$ Level C: 7 Work Packages).
- **Key Bullet Points:**
  - LEVEL A (Overall Programme): Investigate PQC implementation fault resilience across space computing environments.
  - LEVEL B (Work Completed So Far): Initial case study on ML-KEM-768 decapsulation on C99 production binaries.
  - LEVEL C (Remaining Work): 7 comprehensive work packages extending toward full spacecraft flight readiness.
  - Core Objectives: Cross-algorithm fault modeling, lightweight invariant checks, localized rollback, and deterministic containment.
- **Speaker Notes (~60s):**  
  *"To approach this broad problem rigorously, we have structured our research into three distinct levels. Level A is the overall research programme—this is our permanent title and overarching vision: analyzing post-quantum cryptographic fault resilience for space systems. Level B is the work completed so far: an initial, experimentally tractable case study implementing software-level fault resilience on ML-KEM-768. Level C represents the remaining research: extending this cryptographic core into broader algorithms, embedded flight processors, physical radiation testing, and full spacecraft system integration."*

---

### Slide 05: Proposed Research Framework
- **Slide Title:** Unified Methodology for Cryptographic Fault Resilience
- **Visuals:** Mathematical fault propagation pipeline: $\mathcal{O} \to \mathcal{S} \to \mathcal{F} \to \Delta \to \mathcal{P} \to \mathcal{D} \to \mathcal{C}$; four-tier defense stack.
- **Key Bullet Points:**
  - Multi-tier pipeline connecting mathematical operations to cryptographic security outcomes.
  - Layer 1 (Micro-Level): Fine-grained algebraic invariant checking at sub-butterfly granularity.
  - Layer 2 (Local Rollback): Software-managed operand snapshots resolving transient upsets in microseconds.
  - Layer 3 (Containment): Fail-stop escalation to FIPS 203 Section 7.3 implicit rejection.
  - Comprehensive Metrics: SDC elimination, detection coverage, MTTR, availability, and energy overhead.
- **Speaker Notes (~60s):**  
  *"Our research framework bridges theoretical mathematics and physical spacecraft operations. We track how an operation-level fault induces an arithmetic perturbation, how that perturbation propagates through polynomial transforms, and how multi-layer defenses intercept it. At the lowest layer, micro-invariants check arithmetic equations. If a transient fault occurs, localized rollback repairs it in microseconds. If a persistent defect is detected, protocol containment forces safe implicit rejection. Finally, this links into spacecraft fault-management systems. We evaluate this framework across detection coverage, SDC elimination, latency overhead, and energy efficiency."*

---

### Slide 06: Work Completed So Far: ML-KEM-768
- **Slide Title:** Initial Implementation Study: ML-KEM-768 Decapsulation
- **Visuals:** Diagram showing the 11 NTT transforms (6 Forward CT + 5 Inverse GS = 9,856 butterflies); C99 implementation spoke diagram.
- **Key Bullet Points:**
  - Primary NIST post-quantum KEM standard under FIPS 203 (Security Category 3).
  - Heavy arithmetic core: 9,856 butterfly operations per decapsulation across 11 NTT transforms.
  - Integrated directly into standard C99 production codebase (`mlkem-native`).
  - Derived division-free algebraic invariants and software-managed operand snapshots ({u_saved, v_saved}).
  - Implemented standalone cleanroom binary reproducer (`production_reproducer.c`) executing 400 audit trials.
  - Passed 18/18 NIST Known Answer Tests across all ML-KEM and ML-DSA parameter sets.
- **Speaker Notes (~60s):**  
  *"To test our framework empirically, we selected ML-KEM-768 as our initial implementation target. Standardized in FIPS 203, ML-KEM-768 is the primary post-quantum key encapsulation standard. Its performance depends entirely on the Number Theoretic Transform—executing exactly 9,856 butterfly operations per decapsulation. We integrated our fault hooks and invariant monitors directly into the production C99 reference codebase without mock stubs. We built a complete localized rollback mechanism and a cleanroom test binary. This work provides our initial experimental foundation, but it is one case study within our larger space-systems agenda."*

---

### Slide 07: Implemented Fault-Resilience Architecture
- **Slide Title:** Implemented Invariant Monitoring & Rollback Architecture
- **Visuals:** Cooley-Tukey and Gentleman-Sande butterfly equations with annotation arrows for $\Delta_{\text{sum}}, \Delta_{\text{diff}}, \Delta_{\text{add}}, \Delta_{\text{mul}}$; state transition diagram.
- **Key Bullet Points:**
  - Forward CT Invariants: Sum rail $\Delta_{\text{sum}}$ checks adders; Diff rail $\Delta_{\text{diff}}$ checks multipliers (5,376 operations).
  - Inverse GS Invariants: Decoupled pre-reduction adders and forward re-multiplications eliminate modular division (4,480 operations).
  - Localized Rollback: Restores saved operand variables; single-butterfly recomputation (~0.0101% operation ratio).
  - Deterministic Escalation: 2 retries exhausted $\to$ Escalates to FIPS 203 §7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$).
  - Scope Boundary: Across evaluated configurations, detected transient faults recovered locally, while persistent faults escalated safely.
- **Speaker Notes (~60s):**  
  *"Here is how our software resilience architecture works internally. For the forward Cooley-Tukey butterfly, adding the outputs cancels the twiddle product, giving an exact adder invariant; the difference verifies the multiplier. For the inverse Gentleman-Sande butterfly, an exact check normally requires modular division by the twiddle factor, which is too slow in software. We solved this by deriving a decoupled verification scheme that checks both pre-reduction adders and forward multiplications using saved inputs. When an error is detected, the engine restores the saved operands and retries only that single butterfly. For transient faults, recovery is instantaneous. For persistent defects, it exhausts retries and forces standard FIPS 203 implicit rejection."*

---

### Slide 08: Experimental Results & Validation
- **Slide Title:** Experimental Validation on Production C99 Binaries
- **Visuals:** Comparison A chart (end-to-end decapsulation: 110.8 µs vs 129.5 µs, +16.9%); Comparison B chart (isolated NTT DMR: +99.33% vs Monitor: +17.27%); KPI cards.
- **Key Bullet Points:**
  - Comparison A (End-to-End Decapsulation): Baseline 110.77 µs vs Monitored 129.51 µs (+16.9% overhead, N=2,000, -O3).
  - Comparison B (Isolated NTT Benchmarks): Baseline 46.65 µs vs Sequential DMR 92.98 µs (+99.33%) vs Monitor 80.30 µs (+17.27%).
  - Transient Recovery (F4): 100/100 genuine recoveries on retry 1 (95% Wilson CI: $[96.3\%, 100\%]$).
  - Persistent Fail-Stop (F5A + F5B): 200/200 safe implicit rejections (95% Wilson CI: $[98.1\%, 100\%]$).
  - Production SDC: **0/300 active trials** (95% Wilson CI: $[0.00\%, 1.26\%]$).
  - Canonical Campaign SDC: **0/750 active trials** (97.5% Clopper-Pearson bound: **0.49%**).
  - System Efficiency: 0 dynamic heap memory allocations; 18/18 NIST KAT vectors pass.
- **Speaker Notes (~60s):**  
  *"To ensure experimental honesty, we present two separate benchmark comparisons. Comparison A measures full end-to-end decapsulation on ARM64 under -O3: baseline is 110.77 µs, monitored is 129.51 µs, giving +16.9% overhead. Comparison B isolates the NTT transforms: sequential DMR required +99.33% overhead, whereas our dual monitor incurred +17.27%. In 400 cleanroom trials on production binaries, every transient fault recovered locally, every persistent fault escalated to safe implicit rejection, and zero SDC was observed in 300 active trials. In our 900-trial canonical campaign, zero SDC occurred across 750 active trials, bounding SDC probability to under 0.49%."*

---

### Slide 09: Current Limitations & Research Gaps
- **Slide Title:** Current Limitations: Why the Broader Research Continues
- **Visuals:** Numbered limitations list with warning icons; conceptual gap diagram (Desktop Software Model $\to$ Full Space Qualification).
- **Key Bullet Points:**
  - Software-Level Scope: Benchmarked on desktop ARM64; no embedded aerospace processor profiling yet.
  - Software-Injected Faults: Register-modeled bit-flips; no physical heavy-ion or proton cyclotron beam testing.
  - Twiddle-Factor Blindness (Theorem 1): Local invariants cannot detect corruption of shared twiddle values; downstream FO catch validated on reference vector pilot (N=16).
  - Side-Channel Timing: Conditional branches in recovery introduce theoretical timing variations; TVLA/dudect unmeasured.
  - Statistical Bounds: 0 SDC is an empirical upper confidence bound, not mathematical proof of zero failure probability.
- **Speaker Notes (~60s):**  
  *"Academic integrity requires declaring exactly what our current results do and do not demonstrate. Our implementation proves that fine-grained software invariant monitoring and localized rollback work in software on a desktop ARM processor. But we have not yet tested on embedded flight microcontrollers. Our faults are software register flips, not physical particle accelerator beams. By Theorem 1, local invariants cannot detect twiddle table corruption because the checker re-reads the same corrupted memory. And zero observed SDC represents a statistical upper bound, not an absolute mathematical guarantee. These limitations demonstrate why the ML-KEM work is an initial case study, and why the broader space-systems research programme must continue."*

---

### Slide 10: Future Work & Research Expansion
- **Slide Title:** Future Work: Seven Broad Space-System Work Packages
- **Visuals:** 7-box work package grid (WP1 through WP7) showing progression from cryptographic expansion to flight integration.
- **Key Bullet Points:**
  - WP1 (Broader PQC): Evaluate ML-DSA (FIPS 204), SLH-DSA (FIPS 205), and cross-algorithm fault vulnerabilities.
  - WP2 (Embedded Space Computing): Port to ARM Cortex-M4/M7 and RISC-V RV32IM aerospace cores; profile memory and cycles.
  - WP3 (Space-Relevant Fault Modelling): Model SEUs, SETs, multi-bit bursts, control-flow skips, and memory state upsets.
  - WP4 (HW/SW Co-Design): Integrate with hardware ECC, MPUs, watchdogs, and dedicated twiddle factor ROM CRC32 integrity.
  - WP5 (Physical Validation): Laboratory EMFI/glitch injection and cyclotron proton/heavy-ion beam irradiation.
  - WP6 (Space-System Integration): Integrate into NASA cFS/RTEMS, CCSDS SDLS space communications protocols, and FDIR safe-mode.
  - WP7 (System-Level Validation): Hardware-in-the-loop spacecraft testbeds measuring link availability and MTTR.
- **Speaker Notes (~60s):**  
  *"To fulfill our original research vision, our future work is structured across seven broad work packages. In WP1, we expand beyond ML-KEM to evaluate digital signature algorithms like ML-DSA. In WP2, we port our code to embedded ARM Cortex-M4 and aerospace RISC-V processors. In WP3, we model multi-bit radiation bursts. In WP4, we explore hardware/software co-design, including dedicated CRC checks for twiddle factors. In WP5, we move to physical laboratory glitching and cyclotron beam testing. In WP6, we integrate with NASA core Flight System and CCSDS space communication protocols. Finally, in WP7, we build hardware-in-the-loop testbeds to evaluate end-to-end mission availability."*

---

### Slide 11: Conclusion & Research Roadmap
- **Slide Title:** Conclusion: Research Summary & Long-Term Roadmap
- **Visuals:** Milestone checklist (green checkmarks) + horizontal roadmap chevron diagram leading to spaceflight readiness.
- **Key Bullet Points:**
  - Initial Foundation Established: Verified mathematical invariants, localized rollback, and fail-stop containment on ML-KEM-768.
  - Proven Reliability: 100/100 transient recoveries, 200/200 persistent fail-stops, 0 SDC across 300 active trials.
  - High Efficiency: +16.9% decapsulation overhead vs. +99.33% isolated NTT DMR; 0 dynamic heap allocations.
  - The Road Ahead: Executing the 7 work packages to bridge from software case study to flight-qualified spaceborne cryptographic systems.
- **Speaker Notes (~45s):**  
  *"In conclusion, our research investigates fault resilience for post-quantum cryptography in space systems. Within this programme, our initial ML-KEM-768 case study has demonstrated that software-level algebraic invariants and localized single-butterfly rollbacks can recover transient faults and eliminate Silent Data Corruption with only 16.9% decapsulation overhead and zero heap allocations. This provides a strong, mathematically sound foundation. However, our overall mission is not complete: we are advancing through our seven work packages toward embedded processor deployment, physical cyclotron beam testing, and full spacecraft integration. Thank you for your time, and I welcome your questions."*

---

## Presentation Checklist & Alignment Verification
- [x] **Primary Research Title:** *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems* used consistently.
- [x] **Initial Implementation Scoped:** ML-KEM-768 positioned as an initial implementation case study.
- [x] **Exact 11-Slide Structure:** Both `PROGRESS_PRESENTATION_OUTLINE.md` and `AI_PPT_FINAL_CONTENT.md` have exactly 11 slides with matching titles.
- [x] **Future Work Expanded:** 7 Work Packages covering the complete space-system research vision.
