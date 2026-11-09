# ASTRA-Sec: Novelty & Feasibility Assessment

**Auditors:** Senior Academic Research Team  
**Evaluation Standard:** Independent, Sceptical Peer Review Ranking with Devil's Advocate Counter-Evidence.

---

## 1. Multi-Criteria Ranking of Candidate Contributions

Every candidate contribution was scored on a 1–5 scale ($5 = \text{Optimal}$) across seven academic criteria:

| Candidate Contribution | Novelty vs. Prior Art | Technical Depth | Feasibility in Codebase | Experimental Testability | Reproducibility | Academic Impact | Implementation Effort Required | Total Score (out of 35) | Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Candidate E: Software NTT Invariants + Local Rollback** | 4.8 | 4.7 | 5.0 | 5.0 | 5.0 | 4.8 | 4.8 (Already done) | **34.1** | **#1** |
| **Candidate A: Cross-Layer Security State Machine** | 4.6 | 4.5 | 4.8 | 4.8 | 4.8 | 4.7 | 4.5 (Mostly done) | **32.7** | **#2** |
| **Candidate C: Crash-Consistent Command Acceptance** | 3.8 | 4.0 | 4.5 | 4.7 | 4.9 | 4.0 | 4.5 (Done) | **30.4** | **#3** |
| **Candidate D: Key-Transition Safety under Disruption** | 4.2 | 4.2 | 3.5 | 3.8 | 4.0 | 4.3 | 3.0 (Partially done) | **27.0** | **#4** |
| **Candidate B: Fault-Aware DTN Delivery Protocol** | 3.9 | 3.8 | 3.8 | 4.0 | 4.2 | 4.0 | 3.5 (Partially done) | **27.2** | **#5** |

---

## 2. Devil's Advocate: Counter-Evidence & Sceptical Critique

As an independent academic reviewer, we must subject our own claims to the harshest possible scientific scrutiny:

### Critique 1: "Isn't checking $r \equiv t\zeta \pmod q$ just textbook Cooley-Tukey arithmetic?"
- **The Skeptic's Argument:** The mathematical relation $a' = a + t$, $b' = a - t \implies a' - b' = 2t$ is high school algebra. Calling this an "invariant monitor" is rebranding a trivial arithmetic check.
- **The Defense:** While the algebraic relation is elementary, **its constant-time, zero-heap realization in a C99 software implementation operating on secret polynomial coefficients without introducing timing side-channels, combined with localized in-place register rollback ($K \le 2$) and Strategy 1 reference twiddle verification**, is not trivial. Prior literature (Paul et al.) only achieved this in hardware FPGA DSP slices, and software implementations (Ravi et al.) defaulted to naive full duplicate execution (+100% latency). Demonstrating $+2.29\%$ latency in C on standard microprocessors is an authentic engineering and algorithmic achievement.

### Critique 2: "Is ASTRA-Sec running real NASA/JPL ION-DTN?"
- **The Skeptic's Argument:** If ASTRA-Sec is evaluated on macOS where `ionadmin` is not running, calling it "DTN integrated" is misleading.
- **The Defense:** ASTRA-Sec must **never** claim to execute against a running NASA C daemon on macOS. It must accurately report that it implements a **fully compliant, independent RFC 9171 (BPv7) engine with RFC 8949 CBOR encoding and RFC 9172 BPSec support**, and that it outputs configuration files for NASA ION. This distinction is scientifically honest and completely defensible.

### Critique 3: "Does a 38-trial campaign prove zero SDC?"
- **The Skeptic's Argument:** Running 38 adversarial trials is far too small a sample size to claim a mathematical guarantee of zero SDC across arbitrary ionizing radiation environments.
- **The Defense:** The 38 trials represent **protocol-level end-to-end integration scenarios (Groups A–E)**. Foundational fault resilience was independently audited across **3,000 cumulative trials in Phase 7/Phase 18**. The manuscript and paper must strictly qualify: *"Zero SDC observed across 3,000 algorithmic fault trials and 38 end-to-end network trials under the tested single-event upset model; does not constitute a mathematical proof of zero failure under arbitrary continuous multi-bit damage."*

---

## 3. Mandatory Negative Claims (What We Must NOT Claim)

To preserve academic integrity in peer review:
1. **DO NOT claim FIPS certification.** (Standardized algorithms FIPS 203 and 204 are implemented, but the codebase has not undergone NIST CMVP certification).
2. **DO NOT claim physical radiation testing.** (Fault injection is conducted at the software/C macro arithmetic level, simulating single-event upsets; it was not executed in a beam cyclotron facility).
3. **DO NOT claim native ION daemon integration on macOS.** (The transport runs through ASTRA-Sec's Python BPv7 engine; ION configuration generation is supported).
4. **DO NOT claim a per-message Double Ratchet.** (Key evolution currently operates on an asynchronous epoch rotation model, not a per-message ephemeral DH ratchet).
5. **DO NOT claim universal zero SDC.** (Zero SDC was empirically observed under the defined single-event and persistent fault models).
