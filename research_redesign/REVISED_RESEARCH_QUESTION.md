# Revised Research Questions & Defensible Scientific Scope
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Protocol Phase:** Adversarial Evidence Audit & Formulation Revision  
**Date:** October 2026  
**Status:** Defensible Scientific Scope  

---

## 1. Revised Central Research Question

Following the adversarial literature audit, all broad or overreaching formulations have been removed. The central research question is refined to:

> **"In COTS-based space communication systems subject to concurrent transmission channel fades and radiation-induced processor Single-Event Upsets, how can link-layer error control and endpoint post-quantum cryptographic fault handling be jointly coordinated to prevent cross-layer failure misclassification, maximize authenticated telemetry goodput, and maintain standard FIPS 203 implicit rejection guarantees without software-sequential DMR overhead?"**

---

## 2. Refined Sub-Questions (RQs 1–4) & Hypotheses

### Research Question 1 (RQ1): Cross-Layer Failure Disambiguation
> **RQ1:** *To what extent does standard link-layer ARQ misdiagnose cryptographic implicit rejections ($K_{\text{rej}}$) as physical channel fades, and can a cross-layer health telemetry bus eliminate spurious retransmissions during concurrent burst loss and processor SEUs?*

* **Distinction:** Prior work treats crypto verification as a binary black box.
* **Pre-Registered Hypothesis ($H_1$):**
  > *During concurrent channel fades and decapsulation SEUs, an unhardened link layer triggers spurious retransmissions for 100% of packets affected by decapsulation failures; transmitting a 1-byte internal cryptographic status token (`CRYPTO_STATUS_RECOVERED` vs. `CRYPTO_STATUS_REJECTED`) reduces spurious retransmissions to 0.00% by suppressing futile link retries on unrecoverable hardware faults.*

---

### Research Question 2 (RQ2): Joint Adaptation vs. Isolated Baselines
> **RQ2:** *How does a constrained cross-layer controller dynamically adjusting Reed-Solomon coding rates ($R \in [0.50, 0.90]$) and interleaving depth ($D \in [1, 32]$) alongside in-place register rollback compare against conventional fixed-redundancy and channel-adaptive-only baselines in authenticated goodput and transmission energy?*

* **Distinction:** Differentiates from El Bizri et al. (IEEE ICC 2026) by incorporating internal processor health and maintaining a fixed cryptographic security floor (ML-KEM-768).
* **Pre-Registered Hypothesis ($H_2$):**
  > *The joint cross-layer framework achieves at least a 25% improvement in authenticated goodput over static baseline coding during dynamic Markov fading transitions ($G \to B \to G$), while delivering a $>4.0\times$ latency reduction compared to software-sequential DMR.*

---

### Research Question 3 (RQ3): Failure Containment Under Multi-Fault Bursts
> **RQ3:** *What are the failure boundaries of in-place register rollback when subjected to correlated multi-bit SEU bursts striking both primary and shadow registers, and does the framework deterministically enforce FIPS 203 implicit rejection without silent data corruption ($P_{\text{SDC}} = 0.00\%$)?*

* **Distinction:** Acknowledges the limits of single-butterfly transient models identified in our adversarial audit.
* **Pre-Registered Hypothesis ($H_3$):**
  > *For all multi-fault bursts that violate the single-butterfly transient assumption, the complementary dual-invariant check evaluates to non-zero, causing recomputation to fail deterministically and escalating to Tier 2 fail-stop implicit rejection ($K_{\text{rej}}$), guaranteeing that $P_{\text{SDC}} = 0.00\%$ and $P_{\text{Leak}} = 0.00\%$ even under extreme multi-bit radiation bursts.*

---

### Research Question 4 (RQ4): Embedded Microcontroller Feasibility Bounds
> **RQ4:** *What are the static memory footprint, dynamic buffer consumption, and CPU cycle overhead of the joint software-only framework when executed on resource-constrained embedded microprocessors representative of CubeSat on-board computers?*

* **Distinction:** Addresses the hardware platform gap identified between desktop AArch64 benchmarks and physical spacecraft microcontrollers (LEON3 / ARM Cortex-M4).
* **Pre-Registered Hypothesis ($H_4$):**
  > *The entire cross-layer software stack operates within a 512 KB RAM budget and introduces less than 35% processing latency overhead over unencrypted transmission on an in-order RISC core, satisfying SmallSat OBDH operational constraints.*

---

## 3. Explicit Declared Non-Claims (Manuscript Shield)

To insulate the research against reviewer rejection, the following non-claims are permanently established:
1. We do **not** claim to invent a new post-quantum cryptographic algorithm.
2. We do **not** claim to discover new mathematical invariants for forward Cooley-Tukey NTT.
3. We do **not** claim physical radiation hardness assurance under ECSS-Q-ST-60-15C.
4. We do **not** claim that local invariants can detect corrupted static twiddle factor tables without external CRC protection.
5. We do **not** claim to replace heavy-ion cyclotron beam testing with software simulation.
