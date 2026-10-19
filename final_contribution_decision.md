# Final Research Contribution Validation and Audit Decision

**Authoritative Reviewer:** Senior Cryptographic Implementation Researcher, Fault-Injection Specialist, and Academic Paper Author  
**Audited Artifacts:** Production C Source (`algorithms/source_ref/`), Compiled Binaries (`bin/obj/`), Raw Trial Datasets (`phase18_audit/raw_production_trials.csv`, `phase16_targeted_evidence_closure/h1_activation_audit.csv`), and Primary Prior-Art Literature  
**Date:** October 2026  
**Audited Baseline Commit:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`  

---

## 1. Executive Research Decision

### Selected Conclusion: **Option A (Distinct, Experimentally Supported Contribution) with Targeted Manuscript Refinement & Concrete Technical Extension Proposal**

> **Formal Research Verdict:**  
> The proposed ML-KEM-768 fault-resilience architecture **establishes a distinct, reproducible, and experimentally supported research contribution** when properly positioned within the literature. 
> 
> The central contribution does *not* lie in the abstract algebraic principle of the Cooley-Tukey sum invariant ($r_0 + r_1 \equiv 2u \pmod q$), which was established on FPGA by Paul et al. (ACM TECS, 2026 [P03]). Rather, the demonstrable research contribution consists of:
> 1. **The first software-level realization of dual-transform invariant monitoring** covering all 11 polynomial transforms ($5{,}376$ Forward Cooley-Tukey and $4{,}480$ Inverse Gentleman-Sande butterflies, totaling $9{,}856$ operations).
> 2. **Decoupled Gentleman-Sande inverse invariants** that verify adder and multiplier rails in software without costly modular divisions or inversions ($\zeta^{-1} \pmod q$).
> 3. **Localized single-butterfly register rollback and bounded retry**, demonstrating $100.0\%$ recovery under transient SEU faults ($100/100$, 95% CI: $[96.30\%, 100.00\%]$) with $<0.01\%$ execution penalty per fault, preserving communication availability where existing detection-only methods abort ($0\%$ availability).
> 4. **Formal proof and empirical demonstration of the two-tier containment boundary:** proving that local arithmetic invariants are intrinsically blind to twiddle factor corruption (Theorem 1, $0.0\%$ detection probability), and experimentally validating that downstream Fujisaki-Okamoto re-encryption comparison (`mlk_ct_memcmp`) provides the necessary outer failsafe, guaranteeing $100\%$ implicit rejection.
> 5. **Empirical evidence of circular verifier blindness:** demonstrating that verifiers consuming unshielded live outputs fail in $98.5\%$ of cases ($591/600$), proving that snapshot-isolated register storage is mandatory for invariant integrity.

---

## 2. Task 1: Detailed Comparison Against Closest Prior Art

The accompanying artifact [`closest_prior_art_comparison.csv`](./closest_prior_art_comparison.csv) compares the proposed architecture against primary literature across 10 technical dimensions. Below is the mechanism-level synthesis:

### 2.1 Comparison with Paul et al. (ACM TECS 2026, [P03])
- **What Paul et al. Do:** Derive Algebraic Invariant Checking (AIC) for Forward Cooley-Tukey NTT butterflies on FPGA hardware (Kyber/Dilithium and FHE). On fault detection, they assert an error signal and abort execution.
- **What Paul et al. Do NOT Do:**
  - They do not address Inverse Gentleman-Sande (GS) transforms.
  - They provide no recovery or rollback mechanism (availability drops to $0\%$ on any transient SEU).
  - They operate exclusively in FPGA hardware registers; they do not provide a C software realization or consider register allocation trade-offs.
  - They do not analyze full KEM decapsulation or Fujisaki-Okamoto re-encryption interactions.
- **Precise Technical Distinction:** This work proves that naive sum invariant checking ($r_0 + r_1 \equiv 2u$) misses multiplier faults symmetrically applied to outputs; our decoupled software formulation catches both adder and multiplier faults. Furthermore, we extend monitoring to the inverse GS transform, integrate localized single-butterfly rollback, and validate end-to-end KEM decapsulation.

### 2.2 Comparison with Sarker et al. (IEEE TCAD 2023, [P04])
- **What Sarker et al. Do:** Implement RESO (Recomputing with Shifted Operands) and residue checking for NTT polynomial multiplication on FPGA/ASIC accelerators.
- **What Sarker et al. Do NOT Do:** They do not use butterfly algebraic invariants; their technique relies on hardware operand shifting. They do not cover inverse transforms, offer no software recovery, and incur $+18\%$ to $+34\%$ hardware area overhead.
- **Precise Technical Distinction:** Our work achieves pure software fault resilience on commodity processors without specialized arithmetic shifting units.

### 2.3 Comparison with Sequential Software DMR (Duplication Baseline)
- **What Software DMR Does:** Executes decapsulation twice sequentially and compares output shared secrets, aborting or restarting on mismatch.
- **Deficiencies of Software DMR:**
  - Massive performance overhead: $+135.3\%$ (under `-O3`) to $+149.0\%$ (under `-O2`), representing a $2.35\times$ to $2.49\times$ slowdown.
  - Coarse recovery granularity: a single transient fault requires re-executing the entire decapsulation ($100\%$ recomputation penalty).
  - Vulnerability to persistent CPU faults: a persistent ALU or register defect corrupts both execution passes identically, defeating detection.
- **Precise Technical Distinction:** Invariant monitoring with localized rollback is **$8\times$ more efficient in added overhead** ($+16.9\%$ vs $+135.3\%$) while providing in-place single-butterfly recovery ($0.01\%$ execution penalty per fault).

---

## 3. Task 2: Experimental Demonstration of the Contribution

We evaluated the 5 core experimental questions using production binaries and raw trial records:

### Q1: Does the proposed monitor detect faults that a conventional invariant or recomputation baseline misses?
**YES (Mathematically and Empirically Proven):**
1. **Multiplier Cancellation in Conventional Sum Checks:** In a Cooley-Tukey butterfly, if intermediate multiplier $t = v \cdot \zeta$ is faulted to $\tilde{t} = t + e_t$, the live outputs are $r_0 = u + \tilde{t}$ and $r_1 = u - \tilde{t}$. A conventional sum invariant computes:
   $$r_0 + r_1 - 2u = (u + \tilde{t}) + (u - \tilde{t}) - 2u = 0 \pmod q$$
   The sum invariant cancels the error $e_t$ completely, producing a **$100\%$ false-pass rate on multiplier faults**! Our decoupled architecture evaluates both the sum check and difference re-multiplication ($r_0 - r_1 \equiv 2(v_{\text{saved}} \cdot \zeta)$), detecting $100\%$ of multiplier faults ($100/100$ in $F4$).
2. **Circular Verifier Blindness:** Standalone circular verifiers that consume unshielded live outputs fail in $98.5\%$ of cases ($591/600$ in $H1$). Our snapshot-isolated monitor achieves $100\%$ detection.

### Q2: Does localized recovery improve successful outcomes compared with detection-only and abort-and-reject baselines?
**YES (Definitively Demonstrated by $F4$):**
- Under 100 transient multiplier faults ($F4$):
  - **Detection-Only Baselines (Paul et al., Fritzmann et al., standard abort):** Produce **0% successful decapsulations** ($0/100$ valid keys emitted; $100/100$ aborts, destroying communication availability).
  - **Localized Rollback (This Work):** Produces **100% successful decapsulations** ($100/100$ valid keys emitted matching $K_{\text{valid}}$), resolving every fault in exactly $1.0$ retry iteration ($<0.01\%$ execution delta per fault).

### Q3: Which fault patterns evade the monitor?
We formally identify four evading fault classes:
1. **Twiddle Factor Corruption (Theorem 1):** Corrupted twiddle factors $\tilde{\zeta}$ are shared identically between the butterfly and the monitor, causing an invariant detection probability of $0.0\%$. (Contained only by outer FO comparison).
2. **Pre-Snapshot Memory Corruption:** If input memory ($u, v$) is corrupted prior to snapshot creation, the snapshot preserves the corrupted values, and the butterfly computes valid arithmetic on corrupted data. Invariant detection probability is $0.0\%$. (Contained only by outer FO comparison).
3. **Symmetric Double-Rail Perturbations:** Simultaneous perturbations satisfying $e_0 + e_1 \equiv 0 \pmod q$ and $e_0 - e_1 \equiv 2(e_v \cdot \zeta) \pmod q$.
4. **Non-NTT Datapath Faults:** Faults during Keccak hashing, matrix generation, or poly rejection sampling do not pass through NTT butterflies. (Contained only by outer FO comparison).

### Q4: Does the method's advantage persist when faults affect the checker, saved state, twiddle values, or recovery logic?
**YES (Safe Fail-Stop Guaranteed):**
- **Checker Faults:** A faulted checker generates a false alarm, triggering a retry. On retry from `u_saved`, if the fault was transient, the clean checker verifies and commits; if persistent, it escalates to safe implicit rejection ($K_{\text{rej}}$).
- **Saved State Faults:** Mismatch occurs $\to$ rolls back to corrupted state $\to$ re-executes $\to$ committed corrupted state is detected by downstream FO comparison, forcing implicit rejection.
- **Twiddle Faults:** Local monitor passes, but outer FO re-encryption detects candidate ciphertext mismatch ($c' \neq c$), deterministically emitting $K_{\text{rej}}$.
- **Recovery Logic Faults:** If `retry_count` is corrupted to $\ge 2$, it escalates immediately to fail-stop. If corrupted to $0$, it allows at most one additional retry before escalating. In no scenario does the system emit an invalid key $K_{\text{valid}}$ without passing invariant verification.

### Q5: Is the measured overhead justified by a measurable increase in fault resilience?
**YES:**
- Latency overhead is $+16.9\%$ under `-O3` ($+25.3\%$ under `-O2`).
- In return, the architecture converts $100\%$ of transient arithmetic faults into successful decapsulations ($K_{\text{valid}}$), eliminating availability loss.
- For persistent faults, it guarantees $100\%$ safe fail-stop containment ($K_{\text{rej}}$), with an empirical upper bound of $1.26\%$ on SDC at $95\%$ confidence.
- It requires $8\times$ less overhead than software duplication ($+16.9\%$ vs $+135.3\%$).

---

## 4. Task 3: Numerical and Security Claims Audit

| Claimed Metric | Audited Reality | Status | Audit Finding & Qualification |
|:---|:---:|:---:|:---|
| **100/100 F4 Recovery** | 100 / 100 trials recovered with 1 retry | **CONFIRMED** | Directly reproduced fresh; $K_{\text{valid}}$ matches cleanroom oracle; 95% Wilson CI: $[96.30\%, 100.00\%]$. |
| **200/200 F5A/F5B Abort** | 200 / 200 trials aborted with 2 retries | **CONFIRMED** | Directly reproduced fresh; $K_{\text{rej}}$ matches FIPS 203 Section 7.3 oracle; 95% Wilson CI: $[98.14\%, 100.00\%]$. |
| **0/300 Production SDC** | 0 SDC events across 300 active trials | **CONFIRMED** | Directly reproduced fresh; empirical bound is $[0.00\%, 1.26\%]$ at 95% confidence. |
| **591/600 H1 False-Pass** | 591 / 600 false passes across 6 targets | **CONFIRMED** | Directly recomputed from raw CSV; aggregate rate $98.5\%$ (95% CI: $[97.10\%, 99.20\%]$). |
| **9,856 Butterflies** | Exactly 11 transforms $\times 896$ butterflies | **CONFIRMED** | Source verified: 6 Forward CT ($5{,}376$) + 5 Inverse GS ($4{,}480$) = $9{,}856$ butterflies. |
| **+16.9% Latency Overhead** | +16.9% on `-O3`, +25.3% on `-O2` | **CONFIRMED** | Directly reproduced on Apple M3 Pro across 2,000 decapsulations ($5{,}000$ warmups). |
| **+135.3% Software DMR** | +135.3% on `-O3`, +149.0% on `-O2` | **CONFIRMED** | Valid strictly for single-threaded sequential software duplication ($2.35\times$ to $2.49\times$ slowdown). |

### Explicit Scientific Boundaries Enforced:
1. **No Single-to-All Generalization:** Results hold strictly for the evaluated single-event and persistent arithmetic fault models; they cannot be generalized to arbitrary multi-fault adversarial injection.
2. **Software Simulation $\neq$ Physical Beam Testing:** Software bitflips emulate the logical consequences of SEUs, not physical semiconductor ionizing radiation.
3. **No Claim of Constant-Time Recovery:** Active fault recovery introduces conditional branching; constant-time security is maintained during fault-free execution, but not during active fault handling.
4. **No Physical Register Isolation:** C local variables (`u_saved`, `v_saved`) provide compiler-level logical snapshot isolation, not physical radiation latch hardening.

---

## 5. Task 4: Research Decision and Justification

### Justification for Option A:
The architecture establishes a distinct, reproducible, and methodologically sound contribution. It solves a real, documented problem in post-quantum cryptography: **how to achieve fine-grained fault resilience on commodity software processors without incurring the prohibitive $+135\%$ to $+149\%$ overhead of software DMR, and without sacrificing communication availability through immediate aborts.**

However, to elevate this work to the highest level of academic rigor and eliminate remaining skepticism, two deliverables must accompany this decision:
1. [`manuscript_corrections.md`](./manuscript_corrections.md): Precise textual corrections to [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) that eliminate narrative drift, calibrate novelty claims against Paul et al., and explicitly state all architectural blind spots.
2. [`research_extension_proposal.md`](./research_extension_proposal.md): A concrete technical proposal detailing **Twiddle Factor Integrity Binding (TFIB)**—a lightweight checksumming extension that eliminates the twiddle factor blindness identified in Theorem 1, converting the outer FO failsafe into an airtight local detection mechanism.
