# Remaining Gaps and Future Research Roadmap

**Project:** Software-Level Fault Resilience for ML-KEM-768  
**Document Status:** Research Planning and Venue Submission Strategy  
**Date:** October 2026  

---

## 1. Executive Status of the Research Paper

With the completion of the Phase 18 audit and the creation of `paper/manuscript.md`, the research manuscript is:

> **STATUS: A PROMISING, FULLY REPRODUCIBLE MANUSCRIPT READY FOR SUPERVISOR REVIEW AND TARGETED PEER-REVIEW SUBMISSION**  
> *Recommended Target Venues:*  
> - **Top Embedded Security Conferences:** IEEE HOST (Hardware-Oriented Security and Trust), DATE (Design, Automation and Test in Europe), CARDIS (Smart Card Research and Advanced Applications).  
> - **Applied Cryptography / Embedded Systems Journals:** ACM Transactions on Embedded Computing Systems (TECS), IEEE Embedded Systems Letters (ESL), Journal of Cryptographic Engineering (JCEN).

---

## 2. Specific Technical Gaps and Future Experiments

While the paper is completely defensible for its current stated scope, the following three targeted research expansions would elevate it to top-tier security venues (e.g., CHES, IEEE S&P):

### Gap 1: Microarchitectural Side-Channel Evaluation of the Rollback Path (TVLA / dudect)
- **Current Status:** We qualified the manuscript by explicitly withdrawing claims of constant-time execution under active fault conditions. When a fault is detected, the program branches into the retry loop.
- **Proposed Future Experiment:**
  1. Port the compiled binary to an ARM Cortex-M4 target (e.g., STM32F4 Discovery).
  2. Implement a dudect / Test Vector Leakage Assessment (TVLA) harness that captures 100,000 execution traces during fault-injected decapsulation.
  3. Formally quantify the mutual information / $t$-statistic leakage of the rollback branch.

### Gap 2: Cross-Platform Evaluation on Resource-Constrained Embedded Microcontrollers
- **Current Status:** Empirical benchmarks are currently performed on 64-bit ARM microarchitectures (Apple M3 Pro).
- **Proposed Future Experiment:**
  1. Compile the instrumented ML-KEM-768 codebase with `arm-none-eabi-gcc` for ARM Cortex-M4 (32-bit architecture).
  2. Measure cycle counts and register pressure on Cortex-M4 using ARM Keil $\mu$Vision or QEMU-ARM.
  3. Validate that the decoupled Gentleman-Sande invariant checks continue to operate within the 64 KB SRAM budget of typical space CubeSat controllers.

### Gap 3: Physical Radiation Beam Testing (Aerospace Flight Readiness)
- **Current Status:** The fault model relies on terrestrial software simulation of single-event upsets (SEUs) grounded in nuclear physics literature (Dodd & Massengill, ECSS).
- **Proposed Future Experiment:**
  1. Subject a COTS microprocessor running the monitored ML-KEM implementation to a heavy-ion or proton beam (e.g., at the Texas A&M Cyclotron or PSI PIF facility).
  2. Measure empirical cross-sections ($\sigma_{\text{SEU}}$) and verify that the in-place rollback recovers authentic cryptographic keys under genuine ionizing radiation.

---

## 3. Recommended Actions for Supervisor Review

1. **Review `paper/manuscript.md`:** Focus on the clarified narrative in Section 3 and Section 4, confirming that the FIPS 203 transform flow is faithfully represented.
2. **Review `paper/authoritative_results.csv` and `paper/reproducibility.md`:** Verify that all empirical numbers are directly derived from the fresh Phase 18 execution.
3. **Align on Target Venue:** Decide whether to submit the current software-focused manuscript to an applied venue (e.g., IEEE HOST / ACM TECS) immediately, or to allocate 4–6 weeks for Cortex-M4 embedded benchmarking before submitting to CHES.
