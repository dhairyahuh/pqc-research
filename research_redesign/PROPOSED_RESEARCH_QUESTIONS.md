# Proposed Research Questions, Hypotheses, and Measurable Variables
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** System-Level Redesign & Formulation  
**Date:** October 2026  
**Status:** Defensible Scientific Formulation  

---

## 1. Central Research Question

> **"How can a software-only communication framework jointly adapt link-layer error control and endpoint cryptographic fault resilience to maximize authenticated telemetry/telecommand delivery across dynamic space channels without violating post-quantum cryptographic security constraints?"**

---

## 2. Research Question 1 (RQ1): Cross-Layer Failure Coupling & Misclassification

### RQ1 Formulation
> **In post-quantum space communication links, how do concurrent channel impairments (burst erasures, fading) and endpoint cryptographic computation faults (SEUs during ML-KEM decapsulation) interact, and to what extent do traditional isolated-layer communication protocols misclassify cryptographic rejections as physical channel loss?**

* **Independent Variables:**
  - Channel error mode: Good channel, Bad channel (burst loss via Gilbert-Elliott Markov chain), Intermittent outage.
  - Endpoint computational fault mode: Fault-free, Transient NTT arithmetic SEU, Persistent stuck-at fault, Twiddle corruption.
* **Dependent Variables:**
  - Protocol classification accuracy: Rate of correct root-cause identification (Channel Error vs. Cryptographic Fault).
  - Spurious retransmission ratio: Percentage of retransmissions triggered for packets that were dropped due to cryptographic rejection rather than channel loss.
  - Session desynchronization rate: Frequency with which endpoints fall into irrecoverable out-of-sync key states.
* **Formal Hypothesis (H1):**
  > *Under traditional isolated communication stacks, an uncorrected endpoint arithmetic fault during ML-KEM decapsulation triggers standard FIPS 203 implicit rejection ($K_{\text{rej}}$), causing all subsequent authenticated packets to fail AEAD integrity checks. In the absence of cross-layer status signaling, the link layer misclassifies 100% of these authentication failures as transmission errors, entering a futile retransmission loop that exhausts link buffers and wastes satellite energy.*

---

## 3. Research Question 2 (RQ2): Joint Adaptation vs. Fixed/Isolated Baselines

### RQ2 Formulation
> **How does an adaptive resilience controller that jointly coordinates channel error correction (FEC rate, interleaving depth, ARQ policy) and endpoint arithmetic recovery compare against conventional fixed-redundancy and isolated-layer approaches in terms of authenticated delivery probability and resource efficiency?**

* **Independent Variables:**
  - Architectural configuration:
    1. Baseline A: Fixed FEC + Unprotected Cryptography.
    2. Baseline B: Fixed FEC + Software DMR Cryptography.
    3. Baseline C: Adaptive Channel Coding + Unprotected Cryptography (analogous to El Bizri et al. 2026).
    4. Baseline D: Fixed Channel Coding + In-Place Invariant Monitored Cryptography.
    5. Proposed System: Joint Adaptive Controller + In-Place Invariant Monitored Cryptography.
  - Channel dynamics: Gilbert-Elliott average burst length ($L_{\text{burst}} \in [2, 50]$ packets) and packet drop probability ($P_{\text{loss}} \in [0.01, 0.30]$).
  - Endpoint SEU injection intensity: $10^{-3}$ to $10^{-1}$ faults per decapsulation.
* **Dependent Variables:**
  - Authenticated Message Delivery Rate ($P_{\text{auth}} \in [0.0, 1.0]$).
  - Effective Goodput (useful application payload bytes per second).
  - Transmission Energy & Overhead Factor ($\text{Bytes}_{\text{transmitted}} / \text{Bytes}_{\text{payload}}$).
  - End-to-End Latency ($\mu\text{s}$ or ms).
* **Formal Hypothesis (H2):**
  > *The joint adaptive framework achieves at least a 30% higher authenticated goodput than fixed-redundancy baselines during dynamic channel degradation, while reducing total transmission overhead by $>4.0\times$ compared to software-sequential DMR baselines by eliminating spurious retransmissions and repairing transient SEUs locally in endpoint registers.*

---

## 4. Research Question 3 (RQ3): Security-Constrained Invariance & 4-Tier Outcome Bounding

### RQ3 Formulation
> **Under what mathematical policy constraints can the adaptive controller dynamically tune link-layer coding parameters without relaxing cryptographic security parameters or permitting unauthenticated or silently corrupted data delivery?**

* **Independent Variables:**
  - Adaptation decision space: Permitted actions (adjust FEC block size, adjust interleaving depth, select selective-repeat retransmission) vs. Prohibited actions (bypass AEAD, accept unverified plaintexts, reduce ML-KEM security parameter sets below Level 3).
  - Corrupted input injection: Fuzzed ciphertext, tampered AEAD tag, out-of-order sequence counter.
* **Dependent Variables:**
  - Outcome distribution across the formal 4-tier taxonomy:
    1. $P_{\text{AuthSuccess}}$: Legitimate packet successfully authenticated and delivered.
    2. $P_{\text{SafeReject}}$: Corrupted packet, replayed sequence, or persistent fault safely rejected without leakage.
    3. $P_{\text{SDC}}$: Undetected silent data corruption delivered to application layer.
    4. $P_{\text{SecBreak}}$: Plaintext or private key leakage resulting from compromised decapsulation.
* **Formal Hypothesis (H3):**
  > *By enforcing hard security constraints as inviolable optimization boundaries (rather than soft objective penalties), the joint framework guarantees $P_{\text{SDC}} = 0.0$ and $P_{\text{SecBreak}} = 0.0$ across all channel and fault conditions, routing all uncorrectable events deterministically to $P_{\text{SafeReject}}$.*

---

## 5. Research Question 4 (RQ4): Latency and Storage Feasibility for Space Systems

### RQ4 Formulation
> **What are the memory footprint and latency bounds of the joint software-only framework, and is it computationally feasible for deployment on constrained spacecraft On-Board Data Handling (OBDH) processors?**

* **Independent Variables:**
  - Interleaving buffer depth ($D \in [1, 64]$ packets).
  - Retransmission window size ($W \in [4, 128]$ packets).
  - Cryptographic session rekeying interval ($N_{\text{packets}} \in [10^2, 10^5]$).
* **Dependent Variables:**
  - Static and dynamic memory footprint (RAM and non-volatile buffer consumption in KB).
  - Processing jitter and tail latency ($p95, p99$ latency distributions).
  - CPU utilization percentage on representative RISC microprocessor cores.
* **Formal Hypothesis (H4):**
  > *The complete software framework requires less than 512 KB of total working memory (RAM) and introduces less than 35% processing latency overhead over raw unencrypted transmission, making it fully viable for COTS-based CubeSat and SmallSat flight software.*
