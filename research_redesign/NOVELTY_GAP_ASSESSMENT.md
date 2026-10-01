# Research Gap Validation & Novelty Assessment
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** Phase 3 — Identify a Narrow, Defensible Research Gap  
**Date:** October 2026  
**Status:** Defensible Gap Evaluation  

---

## 1. Candidate Research Gap Formulation

The candidate research gap under investigation is:
> **"Joint, security-constrained adaptation of communication recovery and endpoint cryptographic fault handling under combined, changing channel impairments and injected computational faults in post-quantum space systems."**

---

## 2. Granular Investigation of the Seven Gap Dimensions

### 2.1 Question 1: Does existing work jointly model channel-state changes and endpoint cryptographic computation faults?
* **Literature Evidence:**
  - *Channel-State Literature:* Works on satellite and deep-space communications (e.g., Wondmagegn et al. 2025; Elewaily et al. 2024; Gilbert 1960; Elliott 1963) model time-varying channels (Markov burst errors, packet erasures, variable propagation delays, and rain/cloud fading). However, every single surveyed paper in this category treats the endpoint computers as ideal, infallible Turing machines that never experience bit-flips in registers, memory, or ALUs.
  - *Cryptographic Fault Literature:* Works on post-quantum fault attacks and error detection (e.g., Ravi et al. 2023; Hermelink et al. 2021; Paul et al. 2024) model microarchitectural and arithmetic faults (SEUs, register bit-flips, twiddle corruption) in isolated benchmark programs, completely ignoring the communication channel, packetization, and transmission errors.
* **Finding:** **Zero published works jointly model a dynamic wireless/space channel and internal microprocessor cryptographic faults.**

---

### 2.2 Question 2: Does existing work integrate PQC computation monitoring/recovery with communication-layer adaptation?
* **Literature Evidence:**
  - El Bizri et al. (IEEE ICC 2026) investigate "channel-adaptive PQC," but their adaptation is strictly link-layer: they adjust rekeying frequency or switch algorithm parameter sets based on channel SNR. Their adaptation has zero awareness of whether the onboard cryptographic accelerator is healthy, experiencing transient SEUs, or locked in a persistent stuck-at fault.
  - On the other hand, hardware PQC ABFT schemes (Paul et al. 2024; Sarker et al. 2023) raise a local hardware error flag upon detecting an arithmetic error, but provide no connection to the link-layer transmission policy or retransmission scheduler.
* **Finding:** **No prior work couples internal PQC arithmetic monitoring/recovery with link-layer error control (FEC/ARQ) adaptation.**

---

### 2.3 Question 3: Does existing work evaluate combined failures rather than isolated channel errors or isolated computation faults?
* **Literature Evidence:**
  - Existing evaluation testbenches are strictly bifurcated:
    1. Communication testbeds inject noise, packet loss, or delay into a network socket or RF channel model.
    2. Fault-injection testbeds inject register bit-flips or instruction skips into an isolated C function or FPGA core.
* **Finding:** **The interaction between simultaneous channel packet loss and internal cryptographic arithmetic corruption has never been empirically evaluated in post-quantum communication literature.**

---

### 2.4 Question 4: Does existing work use a mathematical controller or optimization policy that explicitly accounts for both delivery performance and security constraints?
* **Literature Evidence:**
  - Communication adaptation policies (e.g., Adaptive Modulation and Coding [AMC], HARQ rate adaptation) maximize throughput, goodput, or energy efficiency subject to a maximum Block Error Rate (BLER). They treat security as an external invariant or assume static symmetric encryption.
  - In cryptographic engineering, security is analyzed through adversary advantage ($\text{Adv}_{\text{IND-CCA}}$), with zero optimization over link delivery constraints.
* **Finding:** **Existing controllers optimize communication throughput or energy, but do not integrate cryptographic health, in-place arithmetic recovery states, and hard security constraints into their objective functions.**

---

### 2.5 Question 5: Does existing work compare adaptive recovery against fixed recovery and isolated-layer approaches?
* **Literature Evidence:**
  - In communication networking, adaptive ARQ/FEC is routinely compared against fixed FEC.
  - In cryptographic software, invariant monitoring is compared against Dual Modular Redundancy (DMR).
  - However, because the layers have never been unified, no paper compares an **integrated cross-layer adaptive recovery architecture** against:
    - Baseline fixed FEC/ARQ with unmonitored cryptography.
    - Adaptive channel-only recovery with unmonitored cryptography.
    - Fixed channel recovery with isolated endpoint recovery.
* **Finding:** **A multi-baseline comparative evaluation across joint channel and computational fault domains does not exist in published literature.**

---

### 2.6 Question 6: Does existing work distinguish authenticated successful delivery, safe failure, undetected corruption, and cryptographic security failure?
* **Literature Evidence:**
  - Standard communication papers report binary outcomes: packet delivered (ACK) vs. packet dropped (NACK/timeout).
  - Cryptographic fault papers report: detected fault, key recovered, or execution abort.
  - Under FIPS 203 Section 7.3, a decapsulation mismatch triggers *implicit rejection* ($K_{\text{rej}}$). In a multi-layer communication system, an implicit rejection causes all subsequent application packets to fail AEAD authentication, which traditional network stacks misclassify as a "corrupted transmission channel," triggering pointless link-level retransmissions.
* **Finding:** **No published communication framework formalizes a fine-grained, 4-tier outcome taxonomy distinguishing Authenticated Delivery, Safe Implicit Rejection, Undetected Silent Data Corruption (SDC), and Cryptographic Key Leakage.**

---

### 2.7 Question 7: Does existing work provide reproducible software experiments that can be independently repeated?
* **Literature Evidence:**
  - Surveys (Kim 2026; Elewaily et al. 2024; Zhang et al. 2023) provide conceptual syntheses without executable code.
  - Hardware PQC papers (Paul et al. 2024; Sarker et al. 2023) rely on closed proprietary FPGA HDL toolchains.
  - El Bizri et al. (2026) evaluate high-level link simulations without public code repositories.
* **Finding:** **A clean-room, software-only reproducible simulation framework uniting standard C PQC implementations with statistical channel and fault injection models is entirely absent from open science repositories.**

---

## 3. Evaluation of the Three Possible Outcomes

### Candidate Outcome A: Clear, Evidence-Supported Novelty
* *Claim:* The joint modeling of channel impairments and endpoint cryptographic faults, paired with a mathematical adaptation controller, represents an entirely new theoretical paradigm.
* *Critique:* While the combination is absent from literature, the underlying sub-components (Markov channels, Reed-Solomon/LDPC coding, ARQ, ML-KEM decapsulation, and arithmetic invariants) are established engineering concepts. Claiming that combining them is a "foundational scientific discovery" would be an overstatement that invites harsh reviewer skepticism.

### Candidate Outcome B: Narrow, Defensible, High-Impact Contribution
* *Claim:* The contribution is an **applied systems engineering, architectural co-design, and empirical evaluation contribution**:
  1. Designing the first software-only space communication framework uniting NIST FIPS 203 (ML-KEM) and AEAD with an adaptive resilient communication layer and an in-place arithmetic fault recovery subsystem.
  2. A constrained adaptation controller that dynamically balances channel coding, interleaving, and retransmission effort while maintaining strict, non-negotiable cryptographic authentication constraints.
  3. Formalizing and empirically demonstrating the 4-tier failure classification (Authenticated Delivery, Safe Rejection, SDC, Security Failure) under combined, changing channel and computational fault conditions.
* *Critique:* This framing is 100% supported by the literature audit, accurately describes what will be built, and makes no false claims of pure mathematical invention.

### Candidate Outcome C: Pure Engineering Reframing (No Novelty)
* *Claim:* The work has zero novelty and is merely an implementation exercise.
* *Critique:* This is overly pessimistic. The complete disconnect between the space communication literature (which assumes perfect processors) and the PQC fault attack literature (which assumes perfect channels) leaves a glaring, dangerous security blind spot in space systems. Closing this gap with an empirical, reproducible software framework is a definitive, publishable contribution.

---

## 4. Final Recommendation: Outcome B (Narrow, Defensible Applied Research Contribution)

> **Recommended Decision:** **Adopt Outcome B.**  
> The project must be explicitly framed as an **applied systems architecture, cross-layer co-design, and empirical evaluation study**.  
> The manuscript will make no claim of inventing new channel models or new cryptographic primitives. Instead, it will defend the **first unified cross-layer framework that prevents communication-layer adaptation from compromising cryptographic security constraints under concurrent space-channel fades and endpoint radiation SEUs**.
