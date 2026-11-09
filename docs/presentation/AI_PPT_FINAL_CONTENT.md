# RESEARCH PRESENTATION — AI PPT SOURCE CONTENT

**Research Programme Title:**  
# FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS

**Current Implementation Case Study:**  
*Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment*

**Presentation Type:** Academic Research Progress Presentation  
**Exact Slide Count:** 11 Slides  
**Audience:** Faculty, Cryptography Reviewers, and Aerospace Panel  
**Design Direction:** Modern, professional, technical research presentation — clean dark navy (`#0F1C2E`) / white theme with teal and amber accents.

---

# SLIDE 01 — TITLE SLIDE: RESEARCH OVERVIEW

**Main takeaway:**
This research programme investigates the reliability and fault resilience of post-quantum cryptographic implementations in space-system environments, presenting an initial software-level case study on NIST FIPS 203 ML-KEM-768.

**Slide content:**

**Title:**
Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems

**Subtitle:**
Investigating Cryptographic Reliability, Localized Recovery, and Containment Under Orbital Fault Environments

**Initial Case Study Focus:**
Software-Level Fault Resilience for ML-KEM-768 Decapsulation

**Presenter:** Dhairya Jain  
**Department:** Computer Science and Engineering  
**Date:** November 2026  
**Primary Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA)

**Key Metric Cards (Current Implementation Progress):**
- 🛰 Space Systems Research Programme
- 🛡 9,856 Operations Monitored (ML-KEM-768)
- ⚡ +16.9% Latency Overhead (Full Decapsulation Benchmark)
- ✅ 0 SDC Observed across 300 Active Production Trials (95% CI: ≤1.26%)

**Visual direction:**
Split layout. Left half: clean title block with overall research title dominating, subtitle, and case study callout. Right half: a 2×2 metric card panel summarizing the initial implementation progress. Bottom accent bar: multi-layer progression strip — "Level A: Space Programme → Level B: ML-KEM-768 Case Study → Level C: 7 Work Packages."

**Speaker notes:**
"Good morning. Today I am presenting our research titled 'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems.' As spaceborne computing platforms transition to post-quantum cryptography, they face extreme operating conditions—such as cosmic radiation and single-event upsets—that threaten cryptographic reliability. In this presentation, I will outline our broader space-systems research programme, present our initial implementation-level progress on ML-KEM-768 decapsulation, discuss the empirical findings and limitations, and map out the remaining research required for full spacecraft integration."

**Evidence sources:**
- `paper/manuscript.md` (Title, Abstract)
- `PROJECT_OVERVIEW.md` (Section 1)
- `docs/architecture/RESEARCH_EVOLUTION.md`
- `phase18_audit/raw_production_trials.csv`

---

# SLIDE 02 — INTRODUCTION: PQC & SPACE SYSTEMS

**Main takeaway:**
Spaceborne platforms must transition to post-quantum cryptography to secure long-life mission data, but operating in unshielded orbital radiation environments exposes cryptographic implementations to severe computational fault risks.

**Slide content:**

**Heading:** Post-Quantum Cryptography in Spaceborne Environments

**The Quantum Imperative for Space:**
- NIST finalized post-quantum standards in August 2024: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
- Satellite missions operate over 10–25 year lifespans; telemetry, telecommand, and payload downlinks require immediate post-quantum security against "harvest-now, decrypt-later" adversaries
- Candidate platforms: CubeSats, LEO mega-constellations, geostationary relays, and deep-space scientific probes

**The Space Radiation Hazard:**
- Outside atmospheric shielding, electronics endure galactic cosmic rays, solar proton events, and trapped radiation belts
- Ionizing particle strikes induce **Single-Event Effects (SEEs)**:
  - *Single-Event Upsets (SEUs):* Bit-flips in registers, configuration latches, and SRAM memory
  - *Single-Event Transients (SETs):* Voltage spikes in arithmetic combinational logic
- Modern aerospace systems increasingly deploy Commercial Off-The-Shelf (COTS) processors to meet high throughput demands, lacking full radiation-hardened silicon

**The Core Reliability Challenge:**
> How can post-quantum cryptographic implementations guarantee correct key establishment and avoid communication link collapse when computational arithmetic is subjected to radiation-induced faults?

**Visual direction:**
Two-column layout. Left column: diagram illustrating Shor's algorithm threat versus lattice-based hardness, with an overlay of satellite orbits (LEO, GEO, Deep Space). Right column: illustration of a cosmic ray particle striking an unhardened CPU register, generating a bit-flip. Callout box at bottom highlighting the vulnerability of COTS microprocessors in space.

**Speaker notes:**
"Post-quantum cryptography is no longer a theoretical exercise—NIST standardized ML-KEM and ML-DSA in August 2024. Space systems must adopt these algorithms immediately because satellite hardware launched today will remain operational well into the era of cryptanalytically relevant quantum computers. However, space platforms operate in an environment flooded with ionizing radiation. When an energetic particle strikes a microprocessor, it causes a bit-flip. Because modern satellite constellations increasingly use high-performance commercial microcontrollers rather than expensive, low-performance radiation-hardened chips, software-level fault resilience is essential."

**Evidence sources:**
- `paper/manuscript.md` (Section 1: Introduction)
- `PROJECT_OVERVIEW.md` (Section 2)
- Survey literature: Kim (Acta Astronautica 2026), Dodd & Massengill (IEEE TNS 2003)

---

# SLIDE 03 — RESEARCH BACKGROUND & PROBLEM STATEMENT

**Main takeaway:**
Arithmetic faults during post-quantum key decapsulation create a dangerous dilemma: undetected faults cause Silent Data Corruption, while unmitigated aborts crash communications—and existing defenses are either unavailable or inefficient.

**Slide content:**

**Heading:** Cryptographic Vulnerabilities Under Hardware Faults

**The Failure Modes in Lattice Key Encapsulation:**
- **Silent Data Corruption (SDC):** An arithmetic bit-flip corrupts intermediate polynomial coefficients, emitting an incorrect shared secret key without signaling an error
  - Result: Cryptographic failure, link desynchronization, or potential fault-enabled key leakage
- **Denial of Service / Unavailability:** Unhandled fault exceptions trigger complete algorithm aborts
  - Result: Repeated cryptographic renegotiation storms over high-latency space links (intermittent line-of-sight)

**Why Evaluated Defenses Fall Short in Space:**
| Defense Approach | Overhead Profile | Operational Limitation in Space |
|---|---|---|
| Hardware ECC / EDAC | ~0% runtime | Hardware ECC availability varies across COTS embedded platforms |
| Dual Modular Redundancy (DMR) | **+99.33% latency** (isolated NTT) | Doubles execution time, draining tight satellite power & thermal budgets |
| Naive Circular Verifiers | Variable | **98.5% blind** (591/600 trials) when verifier reads live faulted output registers |

**The Critical Research Question:**
> Can pure-software countermeasures detect and recover from arithmetic faults at fine granularity without doubling execution time and without relying on specialized hardware?

**Visual direction:**
Three-panel problem diagram. Panel 1: SDC outcome (corrupted secret key accepted silently). Panel 2: Link crash outcome (cryptographic abort triggering lost satellite contact). Panel 3: Bar chart showing DMR overhead (+99.33% at NTT level) alongside circular verifier blindness (98.5% false-pass rate).

**Speaker notes:**
"When a hardware fault strikes an algorithm like ML-KEM during decapsulation, two bad things can happen. First, Silent Data Corruption: the algorithm finishes and outputs a corrupted key without knowing it. That breaks the encrypted communication channel. Second, Denial of Service: the system catches an error and aborts completely. In space communications, where link windows are short and latency is high, repeated full aborts cause communication link collapse. Running the algorithm twice—Dual Modular Redundancy—costs nearly 100% overhead at the transform level, which battery-constrained CubeSats cannot afford. And naive software checks fail 98.5% of the time due to circular blindness."

**Evidence sources:**
- `paper/manuscript.md` (Section 1.1, Section 2.2)
- `phase16_targeted_evidence_closure/h1_activation_audit.csv` (591/600 false passes)
- `results/phase7h/processed/phase7h_timing_distribution.json` (Phase 7H DMR: +99.33%)

---

# SLIDE 04 — RESEARCH OBJECTIVES & PROGRAMME SCOPE

**Main takeaway:**
The overarching programme investigates end-to-end PQC fault resilience for space systems across three structured levels: overall research programme, initial implementation case study, and remaining future work packages.

**Slide content:**

**Heading:** Research Objectives Across the Three-Level Programme

**The Three-Level Research Structure:**
- **LEVEL A — OVERALL RESEARCH PROGRAMME (Permanent Scope):**
  - Title: *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems*
  - Objective: Investigate and enhance the reliability of post-quantum cryptographic implementations under orbital radiation, hardware constraints, and mission-critical operating conditions
- **LEVEL B — WORK COMPLETED SO FAR (Initial Case Study):**
  - Title: *Software-Level Fault Resilience for ML-KEM-768*
  - Objective: Evaluate fine-grained NTT arithmetic monitoring, localized rollback, and fail-stop containment on production C99 binaries
- **LEVEL C — REMAINING RESEARCH & FUTURE WORK:**
  - Objective: Expand from the initial software foundation into multi-algorithm analysis, embedded microcontroller porting, hardware/software co-design, physical beam testing, and spacecraft integration

**Core Programme Objectives:**
1. Formulate cross-algorithm fault propagation models across lattice and hash-based PQC
2. Engineer lightweight, division-free arithmetic invariant monitoring in software
3. Implement localized in-place rollback to maximize session availability during transient upsets
4. Enforce deterministic fail-stop containment via cryptographic implicit rejection
5. Establish an empirical foundation leading to spaceborne hardware-in-the-loop validation

**Visual direction:**
Three-tier hierarchical pyramid or structural card layout. Top tier: Level A (Overall Research Programme). Middle tier: Level B (Work Completed So Far: ML-KEM-768 Case Study, highlighted with green completion badge). Bottom tier: Level C (Remaining Research & Future Work Packages).

**Speaker notes:**
"To approach this broad problem rigorously, we have structured our research into three distinct levels. Level A is the overall research programme—this is our permanent title and overarching vision: analyzing post-quantum cryptographic fault resilience for space systems. Level B is the work completed so far: an initial, experimentally tractable case study implementing software-level fault resilience on ML-KEM-768. Level C represents the remaining research: extending this cryptographic core into broader algorithms, embedded flight processors, physical radiation testing, and full spacecraft system integration."

**Evidence sources:**
- `research-roadmap.md` (Section 1)
- `PROJECT_OVERVIEW.md` (Section 2)
- `docs/architecture/RESEARCH_EVOLUTION.md` (Section 2)

---

# SLIDE 05 — PROPOSED RESEARCH FRAMEWORK

**Main takeaway:**
Our methodology establishes a unified mathematical and empirical pipeline that models error propagation, evaluates multi-layer defenses, and measures performance across space-system metrics.

**Slide content:**

**Heading:** Unified Methodology for Cryptographic Fault Resilience

**The Fault-to-Security Propagation Pipeline:**
$$\text{Operation } (\mathcal{O}) \longrightarrow \text{State } (\mathcal{S}) \longrightarrow \text{Fault } (\mathcal{F}) \longrightarrow \text{Perturbation } (\Delta) \longrightarrow \text{Propagation } (\mathcal{P}) \longrightarrow \text{Detection/Rollback } (\mathcal{D}) \longrightarrow \text{Containment } (\mathcal{C})$$

**Multi-Layer Defensive Architecture:**
- **Layer 1: Micro-Level Monitoring:** Algebraic invariant checking embedded directly at arithmetic operation granularity (sub-butterfly level)
- **Layer 2: Localized In-Place Rollback:** Operand snapshotting and localized recomputation to resolve transient single-event upsets
- **Layer 3: Protocol-Level Containment:** Deterministic fail-stop escalation to cryptographic implicit rejection, suppressing invalid key output
- **Layer 4: System-Level Coordination:** Interface with spacecraft Fault Detection, Isolation, and Recovery (FDIR) and safe-mode state machines

**Comprehensive Evaluation Dimensions:**
- **Fault Detection Coverage (%):** Transient and persistent fault detection rates
- **Silent Data Corruption Rate (%):** Probability of undetected incorrect cryptographic outputs
- **Availability & MTTR:** Microsecond recovery latency versus full protocol renegotiation
- **Overhead Profile:** CPU cycle latency, RAM footprint, code size, dynamic stack growth

**Visual direction:**
Horizontal pipeline flowchart displaying the propagation from mathematical operation down to security outcome. Below: a four-layer architectural stack with color coding (Blue: Micro Invariants → Teal: Local Rollback → Amber: Protocol Containment → Purple: Spacecraft FDIR).

**Speaker notes:**
"Our research framework bridges theoretical mathematics and physical spacecraft operations. We track how an operation-level fault induces an arithmetic perturbation, how that perturbation propagates through polynomial transforms, and how multi-layer defenses intercept it. At the lowest layer, micro-invariants check arithmetic equations. If a transient fault occurs, localized rollback repairs it in microseconds. If a persistent defect is detected, protocol containment forces safe implicit rejection. Finally, this links into spacecraft fault-management systems. We evaluate this framework across detection coverage, SDC elimination, latency overhead, and energy efficiency."

**Evidence sources:**
- `paper/manuscript.md` (Section 1.2, Section 3)
- `research-roadmap.md` (Phase 4 Common Framework)
- `docs/architecture/RESEARCH_EVOLUTION.md`

---

# SLIDE 06 — WORK COMPLETED SO FAR: ML-KEM-768

**Main takeaway:**
As an initial implementation-level case study within the broader research, we targeted ML-KEM-768 decapsulation, focusing on its core Number Theoretic Transform (NTT) computational engine.

**Slide content:**

**Heading:** Initial Implementation Study: ML-KEM-768 Decapsulation

**Why ML-KEM-768 Was Selected as the Initial Target:**
- Standardized under NIST FIPS 203 (August 2024); primary general-purpose KEM standard
- Security Category 3: Recommended default parameter set for high-security and aerospace applications
- Highly computationally intensive: Key decapsulation executes **9,856 butterfly operations** across 11 NTT polynomial transforms (6 Forward CT + 5 Inverse GS)
- Complex algebraic structure: Integrates NTT polynomial multiplication with the Fujisaki-Okamoto (FO) transform

**Scope of Implemented Work:**
1. Integration directly into standard production C99 codebase (`mlkem-native` / FIPS 203)
2. Formulation and derivation of division-free algebraic invariants for both CT and GS butterflies
3. Software-managed operand snapshotting ({u_saved, v_saved}) before every butterfly
4. Localized single-butterfly rollback engine for transient fault recovery (retry limit ≤ 2)
5. Deterministic escalation to FIPS 203 Section 7.3 implicit rejection for persistent faults
6. Cleanroom standalone test binary (`phase18_audit/production_reproducer.c`) executing 400 audit trials
7. 18/18 NIST Known Answer Tests (KAT) verified passing with zero regressions

**Important Positioning:**
> This ML-KEM-768 work represents the implementation and experimental progress achieved to date—it provides an initial technical foundation, not the completion of the full space-system research programme.

**Visual direction:**
Two-column layout. Left column: breakdown of the 11 NTT transforms in ML-KEM-768 decapsulation (diagram showing 6 Forward NTTs and 5 Inverse NTTs totaling 9,856 butterflies). Right column: summary of the completed software implementation components with green checkmarks. Highlight box at bottom emphasizing this is an initial case study.

**Speaker notes:**
"To test our framework empirically, we selected ML-KEM-768 as our initial implementation target. Standardized in FIPS 203, ML-KEM-768 is the primary post-quantum key encapsulation standard. Its performance depends entirely on the Number Theoretic Transform—executing exactly 9,856 butterfly operations per decapsulation. We integrated our fault hooks and invariant monitors directly into the production C99 reference codebase without mock stubs. We built a complete localized rollback mechanism and a cleanroom test binary. This work provides our initial experimental foundation, but it is one case study within our larger space-systems agenda."

**Evidence sources:**
- `algorithms/source_ref/mlkem_fault_hooks.c`
- `algorithms/source_ref/mlkem/src/poly.c`, `kem.c`
- `results/phase7i/processed/phase7i_e2e_results.json` (9,856 butterflies: 5,376 CT + 4,480 GS)
- `bin/test_fips_kats` (18/18 PASS)

---

# SLIDE 07 — IMPLEMENTED FAULT-RESILIENCE ARCHITECTURE

**Main takeaway:**
The implemented architecture evaluates decoupled algebraic invariants across all 9,856 butterflies, performs single-butterfly in-place rollback for transient upsets, and enforces safe fail-stop containment.

**Slide content:**

**Heading:** Implemented Invariant Monitoring & Rollback Architecture

**Forward Cooley-Tukey (CT) Invariants (5,376 Butterflies):**
```text
t = v · ζ  (mod q);   r₀ = u + t  (mod q);   r₁ = u - t  (mod q)
```
- **Sum Rail:** $\Delta_{\text{sum}} = (r_0 + r_1 - 2u_{\text{saved}}) \pmod q \equiv 0$  (verifies adder, blind to $t$)
- **Diff Rail:** $\Delta_{\text{diff}} = (r_0 - r_1 - 2t_{\text{check}}) \pmod q \equiv 0$  (verifies multiplier, $t_{\text{check}} = v_{\text{saved}} \cdot \zeta$)

**Inverse Gentleman-Sande (GS) Decoupled Invariants (4,480 Butterflies):**
```text
r₀ = u + v  (mod q);   r₁ = (v - u) · ζ  (mod q)
```
- **Adder Rail:** $\Delta_{\text{add}} = (r_0 - u_{\text{saved}} - v_{\text{saved}}) \pmod q \equiv 0$
- **Multiplier Rail:** $\Delta_{\text{mul}} = (r_1 - \text{fqmul}(v_{\text{saved}} - u_{\text{saved}}, \zeta)) \pmod q \equiv 0$
- **Division-Free:** Eliminates expensive modular division in software by checking forward rails

**Localized Rollback & Deterministic Containment:**
- Operand snapshot: Saves $\{u_{\text{saved}}, v_{\text{saved}}\}$ in software-managed state variables before computation
- Mismatch detected $\to$ Restore operands $\to$ Re-execute single butterfly (~0.0101% operation-count ratio)
- Retry limit = 2: Transient faults clear on retry 1 ($K_{\text{valid}}$); persistent faults escalate to FIPS 203 §7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$)

**Evaluated Scope Boundary:**
> Across the evaluated fault configurations, detected transient faults were recovered locally, while evaluated persistent faults escalated to implicit rejection. These results do not establish coverage against every possible fault class.

**Visual direction:**
Two-column technical schematic. Left: circuit-style diagram of Cooley-Tukey and Gentleman-Sande butterflies showing where $\Delta_{\text{sum}}$, $\Delta_{\text{diff}}$, $\Delta_{\text{add}}$, and $\Delta_{\text{mul}}$ are evaluated. Right: state transition diagram showing: Normal Execution $\to$ Invariant Mismatch $\to$ Local Rollback (retry ≤ 2) $\to$ Success ($K_{\text{valid}}$) OR Escalation $\to$ Safe Fail-Stop ($K_{\text{rej}}$).

**Speaker notes:**
"Here is how our software resilience architecture works internally. For the forward Cooley-Tukey butterfly, adding the outputs cancels the twiddle product, giving an exact adder invariant; the difference verifies the multiplier. For the inverse Gentleman-Sande butterfly, an exact check normally requires modular division by the twiddle factor, which is too slow in software. We solved this by deriving a decoupled verification scheme that checks both pre-reduction adders and forward multiplications using saved inputs. When an error is detected, the engine restores the saved operands and retries only that single butterfly. For transient faults, recovery is instantaneous. For persistent defects, it exhausts retries and forces standard FIPS 203 implicit rejection."

**Evidence sources:**
- `algorithms/source_ref/mlkem_fault_hooks.c` (lines 617–656, 819–835)
- `paper/manuscript.md` (Section 3: Mathematical Derivations)
- `phase18_audit/raw_production_trials.csv`

---

# SLIDE 08 — EXPERIMENTAL RESULTS & VALIDATION

**Main takeaway:**
Empirical validation on compiled production binaries demonstrates successful transient recovery, safe persistent fail-stop containment, zero observed SDC, and +16.9% decapsulation latency overhead.

**Slide content:**

**Heading:** Experimental Validation on Production C99 Binaries

**Comparison A: End-to-End Decapsulation Benchmark (ARM64 M3 Pro, -O3, N=2,000):**
| Implementation Configuration | Mean Latency | Overhead | Observed SDC | Recovery Scope | Provenance Notes |
|---|---|---|---|---|---|
| Unmodified ML-KEM-768 Baseline | 110.77 µs | 0.0% | Unmitigated | None | Reference benchmark |
| **Monitored Architecture (Our Work)** | **129.51 µs** | **+16.9%** | **0/300 observed** | Localized single-butterfly retry | Full decapsulation (stdout summary logs) |

**Comparison B: Isolated NTT-Level Benchmarks (ARM64 M3 Pro, -O3, N=2,000):**
| Benchmark Configuration | Mean Latency | Overhead | Experimental Scope | Source Artifact |
|---|---|---|---|---|
| Baseline Isolated NTT (Phase 7H) | 46.65 µs | 0.0% | Baseline transform | `phase7h_timing_distribution.json` |
| Sequential DMR NTT (Phase 7H) | 92.98 µs | **+99.33%** | Redundant transform computation | `phase7h_timing_distribution.json` |
| Dual-Transform NTT Monitor (Phase 7I) | 80.30 µs (vs 68.47 µs) | **+17.27%** | Combined CT + GS monitoring | `phase7i_e2e_results.json` |

*Note: Conceptual DMR decapsulation latency (≥+100%) is an analytical extrapolation and is not presented as an experimentally measured end-to-end result.*

**Empirical Containment Rates:**
- **Transient Multiplier Faults (F4):** 100/100 GENUINE_RECOVERY on retry 1 (95% Wilson CI: $[96.3\%, 100\%]$)
- **Persistent Faults (F5A + F5B):** 200/200 SAFE_FAIL_STOP (95% Wilson CI: $[98.1\%, 100\%]$)
- **Production Cleanroom Trials (Phase 18):** **0/300 active SDC** (95% Wilson CI: $[0.00\%, 1.26\%]$)
- **Canonical Campaign (TFIB Step 2C-A):** **0/750 active SDC** (97.5% Clopper-Pearson bound: **0.49%**)
  - *Breakdown:* 250 recovered, 350 fail-stop, 147 twiddle faults caught downstream by outer FO, 3 ineffective
- **System Efficiency:** 0 dynamic heap memory allocations; 18/18 NIST KAT vectors pass

**Visual direction:**
Two distinct comparative panels. Left panel: Comparison A bar chart showing end-to-end decapsulation (110.77 µs vs 129.51 µs, +16.9%). Right panel: Comparison B bar chart showing isolated NTT results (Baseline 46.65 µs vs DMR 92.98 µs [+99.33%] vs Monitor 80.30 µs [+17.27%]). Bottom row: three KPI badges: "100/100 Transient Recoveries", "0/300 & 0/750 SDC Observed", "0 Dynamic Heap Bytes".

**Speaker notes:**
"To ensure experimental honesty, we present two separate benchmark comparisons. Comparison A measures full end-to-end decapsulation on ARM64 under -O3: baseline is 110.77 µs, monitored is 129.51 µs, giving +16.9% overhead. Comparison B isolates the NTT transforms: sequential DMR required +99.33% overhead, whereas our dual monitor incurred +17.27%. In 400 cleanroom trials on production binaries, every transient fault recovered locally, every persistent fault escalated to safe implicit rejection, and zero SDC was observed in 300 active trials. In our 900-trial canonical campaign, zero SDC occurred across 750 active trials, bounding SDC probability to under 0.49%."

**Evidence sources:**
- `results/phase7h/processed/phase7h_timing_distribution.json` (Phase 7H DMR: +99.33%)
- `results/phase7i/processed/phase7i_e2e_results.json` (Phase 7I: +17.27%)
- `phase18_audit/raw_production_trials.csv` (N=400 cleanroom trials)
- `tfib_trial_level_results.csv` (N=900 canonical campaign trials)

---

# SLIDE 09 — CURRENT LIMITATIONS & RESEARCH Gaps

**Main takeaway:**
The current implementation provides a verified software foundation, but significant research gaps remain regarding physical radiation, platform diversity, side-channel leakage, and shared twiddle-factor integrity.

**Slide content:**

**Heading:** Current Limitations: Why the Broader Research Continues

**Declared Boundaries of Completed Work:**
1. **Software-Level Execution Scope:**
   - Evaluated on a 64-bit desktop processor (Apple Silicon M3 Pro)
   - Has not yet been profiled or deployed on 32-bit aerospace microcontrollers (ARM Cortex-M4, RISC-V)
2. **Software-Injected Fault Model:**
   - Faults are simulated via register-modeled operand bit-flips
   - Physical radiation phenomena (charge deposition, multi-cell upsets, latchup) have not been tested
3. **Twiddle-Factor Blindness (Theorem 1):**
   - Local invariants cannot independently detect corruption of a shared twiddle-factor value
   - Downstream FO validation returned implicit rejection for the evaluated reference vector in the Phase 15Q pilot (N=16); broader validation remains future work
4. **Side-Channel & Timing Variations:**
   - Conditional branches in the rollback recovery path introduce theoretical timing variations
   - Formal TVLA and dudect leakage evaluations on compiled binaries remain unexecuted
5. **Statistical Bounds vs. Universal Proof:**
   - Observed 0/300 and 0/750 SDC rates represent statistical upper confidence bounds (1.26% and 0.49%), not mathematical proof of zero failure probability across all circuits

**The Scope Gap:**
> The current ML-KEM-768 implementation proves the algorithmic feasibility of fine-grained software resilience, but fulfilling our space-systems research objective requires bridging from software models to physical spacecraft environments.

**Visual direction:**
Two-column alert layout. Left column: numbered list of the five declared scientific limitations with amber warning icons. Right column: conceptual gap bridge diagram showing "Current Software Foundation (Desktop / Simulated Faults)" separated by a chasm from "Full Space-System Qualification (Orbital / Radiation-Hardened / Flight Systems)".

**Speaker notes:**
"Academic integrity requires declaring exactly what our current results do and do not demonstrate. Our implementation proves that fine-grained software invariant monitoring and localized rollback work in software on a desktop ARM processor. But we have not yet tested on embedded flight microcontrollers. Our faults are software register flips, not physical particle accelerator beams. By Theorem 1, local invariants cannot detect twiddle table corruption because the checker re-reads the same corrupted memory. And zero observed SDC represents a statistical upper bound, not an absolute mathematical guarantee. These limitations demonstrate why the ML-KEM work is an initial case study, and why the broader space-systems research programme must continue."

**Evidence sources:**
- `paper/manuscript.md` (Section 7, Section 8.1)
- `AYUSH.md` (Sections 17, 18)
- `phase17b_corrected/revision_summary.md`

---

# SLIDE 10 — FUTURE WORK & RESEARCH EXPANSION

**Main takeaway:**
Remaining research expands across seven comprehensive work packages spanning broader PQC algorithms, embedded computing, space fault modeling, hardware/software co-design, physical testing, and spacecraft integration.

**Slide content:**

**Heading:** Future Work: Seven Broad Space-System Work Packages

**The Seven Work Packages:**
- **WP1 — Broader Cryptographic Evaluation:**
  - Evaluate additional post-quantum implementations: ML-DSA (FIPS 204), SLH-DSA (FIPS 205), stateful hash signatures
  - Compare cross-algorithm mathematical structures and fault-sensitive computational stages
- **WP2 — Embedded & Space-Oriented Computing:**
  - Port to aerospace embedded platforms: ARM Cortex-M4/M7, ARM Cortex-R, RISC-V RV32IM (NOEL-V)
  - Quantify RAM footprint, dynamic stack depth growth during snapshotting, and execution cycle counts
- **WP3 — Space-Relevant Fault Modelling:**
  - Model physical SEEs: Single-Event Upsets (SEUs), Single-Event Transients (SETs), and multi-bit burst faults
  - Expand injection to constant tables, control-flow logic, instruction decoders, and Keccak states
- **WP4 — Hardware/Software Fault Resilience:**
  - Co-design software invariants with hardware ECC, Memory Protection Units (MPUs), and watchdogs
  - Develop dedicated ROM twiddle-factor integrity binding (CRC32/checksums) to resolve Theorem 1 blindness
- **WP5 — Physical Validation:**
  - Conduct laboratory electromagnetic fault injection (EMFI) and pulsed voltage/clock glitching
  - Prepare cyclotron particle accelerator beam campaigns (protons and heavy ions at TRIUMF / LBNL)
- **WP6 — Space-System Integration:**
  - Integrate into flight software architectures: NASA core Flight System (cFS), RTEMS, FreeRTOS
  - Secure telecommand/telemetry links under CCSDS Space Data Link Security (SDLS) standards; integrate with FDIR
- **WP7 — System-Level Validation:**
  - Build hardware-in-the-loop (HIL) spacecraft communications testbeds measuring link availability and MTTR

**Visual direction:**
Structured 7-card horizontal/grid layout showing the seven work packages (WP1 through WP7). Each card has a work package title, icon, and 2 concise bullet points. Color gradient showing progression from Algorithmic Expansion (WP1-WP2) $\to$ Advanced Modeling & Co-Design (WP3-WP4) $\to$ Physical & Spacecraft Integration (WP5-WP7).

**Speaker notes:**
"To fulfill our original research vision, our future work is structured across seven broad work packages. In WP1, we expand beyond ML-KEM to evaluate digital signature algorithms like ML-DSA. In WP2, we port our code to embedded ARM Cortex-M4 and aerospace RISC-V processors. In WP3, we model multi-bit radiation bursts. In WP4, we explore hardware/software co-design, including dedicated CRC checks for twiddle factors. In WP5, we move to physical laboratory glitching and cyclotron beam testing. In WP6, we integrate with NASA core Flight System and CCSDS space communication protocols. Finally, in WP7, we build hardware-in-the-loop testbeds to evaluate end-to-end mission availability."

**Evidence sources:**
- `research-roadmap.md` (Section 3: Seven Work Packages)
- `paper/manuscript.md` (Section 8.2)
- `docs/architecture/RESEARCH_EVOLUTION.md` (Section 3)

---

# SLIDE 11 — CONCLUSION & RESEARCH ROADMAP

**Main takeaway:**
The ML-KEM-768 case study establishes an empirical software-level foundation, while the overall research programme continues toward comprehensive post-quantum fault resilience for space missions.

**Slide content:**

**Heading:** Conclusion: Research Summary & Long-Term Roadmap

**Summary of Current Progress (ML-KEM-768 Foundation):**
- ✅ **Mathematical Derivations:** Formulated division-free dual invariants covering all 9,856 NTT butterflies
- ✅ **Localized Rollback:** 100/100 transient recoveries on retry 1 with ~0.0101% operation-count recomputation ratio
- ✅ **Deterministic Safety:** 200/200 persistent fail-stops to FIPS 203 implicit rejection; 0 SDC across 300 production and 750 campaign trials
- ✅ **Practical Efficiency:** +16.9% decapsulation latency overhead under `-O3` (vs +99.33% isolated NTT DMR); 0 dynamic heap allocations
- ✅ **Standard Conformance:** 18/18 NIST KAT vectors pass across all ML-KEM and ML-DSA parameter sets

**The Long-Term Research Horizon:**
```text
[Completed Software Foundation] ──► [Embedded Porting & Broader PQC] ──► [HW/SW Co-Design]
                                                                                │
[Flight Mission Deployment] ◄── [System-Level Validation] ◄── [Physical Beam Testing] ◄──┘
```

**Final Research Takeaway:**
> "Our current implementation demonstrates that lightweight software-level invariant monitoring and localized rollback can effectively eliminate Silent Data Corruption and preserve communication availability. This provides a rigorous technical foundation as we advance the broader research programme toward fully qualified, space-resilient post-quantum cryptographic systems."

**Visual direction:**
Split conclusion layout. Left half: checklist of completed ML-KEM-768 milestones with green checkmarks and key empirical metrics in bold cyan. Right half: horizontal roadmap chevron diagram showing the trajectory from the completed software core through the seven work packages to flight mission readiness. Footer: authoritative research title banner.

**Speaker notes:**
"In conclusion, our research investigates fault resilience for post-quantum cryptography in space systems. Within this programme, our initial ML-KEM-768 case study has demonstrated that software-level algebraic invariants and localized single-butterfly rollbacks can recover transient faults and eliminate Silent Data Corruption with only 16.9% decapsulation overhead and zero heap allocations. This provides a strong, mathematically sound foundation. However, our overall mission is not complete: we are advancing through our seven work packages toward embedded processor deployment, physical cyclotron beam testing, and full spacecraft integration. Thank you for your time, and I welcome your questions."

**Evidence sources:**
- `paper/manuscript.md` (Section 9: Conclusion)
- `research-roadmap.md` (Section 1, Section 3)
- `README.md` (Section 1)

---

*End of AI PPT Source Content — Exactly 11 Slides*
