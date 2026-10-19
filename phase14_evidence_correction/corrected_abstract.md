# Corrected Abstract: On the Pitfalls of Local Arithmetic Recovery in ML-KEM-768

**Target Manuscript Category:** Applied Cryptographic Hardware & Software Security / Fault Resilience  
**Status:** Audit-Corrected Version (Phase 14 Baseline)  

---

### Abstract

Fault-tolerant implementations of post-quantum key encapsulation mechanisms frequently employ checkpoint-and-verify recovery mechanisms to mitigate transient arithmetic faults during Number Theoretic Transform (NTT) polynomial computations. This study investigates the interplay between internal recovery verification and end-to-end cryptographic integrity in NIST FIPS 203 ML-KEM-768. 

Using standalone software harness models simulating in-place memory corruption, we demonstrate an architectural pitfall termed **circular verifier blindness** ($H_1$): when intermediate operands or snapshot registers are corrupted prior to or during retry execution, local recovery verifiers consistently validate corrupted butterfly computations against their own corrupted baselines, exhibiting false-pass rates between $94.0\%$ and $100.0\%$ across vulnerable configurations. In contrast, an authentic compiled C production implementation (`mlkem768_inst.o`) incorporating native butterfly monitoring achieves $100.0\%$ genuine recovery ($100/100$) under transient single-bit faults and $100.0\%$ safe fail-stop aborts ($200/200$) under recurring bit-inversion and software force-value fault models, safely emitting the FIPS 203 implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$. Across 400 production decapsulation trials, zero Silent Data Corruption ($H_2$) events were observed (95% Wilson score confidence interval: $[0.0\%, 0.95\%]$), demonstrating that outer Fujisaki-Okamoto re-encryption effectively suppresses corrupted internal butterfly states from causing false key acceptance under the evaluated software fault models. 

These findings indicate that naive internal checkpointing introduces circular trust vulnerabilities in cryptographic arithmetic, but that algorithmic ciphertext re-encryption provides robust containment against software-modeled computational corruption. We explicitly delineate the boundaries of this work: physical fault injection (e.g., laser, electromagnetic, clock glitching) and microarchitectural side-channel leakage remain unverified, and formal academic novelty is unresolved pending systematic comparative prior-art analysis against hardware fault-detection literature.
