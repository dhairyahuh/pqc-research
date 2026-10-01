# Novelty Risk & Overlap Assessment Table

**Document Version:** 1.0.0-PHASE0  
**Date:** October 1, 2026  
**Status:** CONSERVATIVE ACADEMIC EVALUATION  
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Evaluation Standard:** Aggressively Skeptical Academic Peer Review

---

## 1. Overview and Assessment Methodology

This table provides a critical, conservative evaluation of every proposed research contribution considered in this project. The objective is not to inflate the novelty of our findings, but to establish their defensibility against seasoned peer reviewers in cryptographic hardware, post-quantum security, and aerospace systems engineering.

### Risk Level Definitions
- **CRITICAL RISK:** The contribution is already directly published in major venues; claiming it as novel would lead to immediate paper rejection.
- **HIGH RISK:** Very close prior art exists; differentiation relies on subtle implementation choices that may be perceived as routine engineering.
- **MODERATE RISK:** The core idea exists in adjacent domains (e.g., FPGA hardware or classical crypto), but its adaptation to standardized PQC software is novel and defensible if supported by rigorous data.
- **LOW RISK / STRONG OPPORTUNITY:** Genuine, verifiable gap in the literature with high scientific value, defensible theoretical backing, and solid empirical reproducibility.

---

## 2. Novelty Risk Table

| Proposed Contribution | Existing Work | Overlap Risk | Evidence (Literature & Repository) | What We Would Need to Demonstrate to Defend Novelty |
| :--- | :--- | :---: | :--- | :--- |
| **1. Fujisaki-Okamoto (FO) Re-Encryption Fault Analysis**<br>Inverting decapsulation comparison flag ($0 \to 1$ and $1 \to 0$) | • Pessl & Prokop (TCHES 2021)<br>• Hermelink et al. (INDOCRYPT 2021)<br>• Delvaux (TCHES 2022)<br>• Jaiswal et al. (IEEE TIFS 2024) | **CRITICAL RISK** | Overlap is near-total. Published papers have demonstrated laser FI and branch skipping on `ct_memcmp` to build Plaintext-Checking Oracles for key extraction. | **Do NOT claim FO bypass as a novel attack.** Frame it strictly as an operational baseline: demonstrate that under *accidental/space faults* (where the attacker is absent), inverting the flag under corrupted ciphertext merely produces an invalid candidate key ($K_{cand} \neq K_{ground}$), which does *not* recover the session key or compromise IND-CCA2 security. |
| **2. Software Memory Bit-Flip Injection as "Space Radiation SEUs"**<br>Simulating single-bit flips in key buffers using Python `ctypes` | • NASA-HDBK-4002A (2020)<br>• Dozens of PQC fault injection papers on microcontrollers (`pqm4`) | **CRITICAL RISK** | Simulating bit flips in software memory has been done in hundreds of papers and does NOT represent true radiation testing. Equating Python bit-flips with cosmic ray SEUs is scientifically flawed. | **Do NOT claim physical space qualification.** Explicitly state: "We evaluate an abstract software-level bit-flip fault model inspired by Single Event Upset phenomenology." To publish in aerospace venues, validate against published radiation cross-sections or microarchitectural fault rates. |
| **3. Mathematical Error Diffusion vs. Lossy Compression Absorption**<br>Stage 1 NTT butterfly errors diffuse across 128 coefficients and are absorbed by `Compress_d` ($d_u=10, d_v=4$), yielding 100% valid decapsulation | • FIPS 203 (Algorithms 4, 5, 17)<br>• Fritzmann et al. (IEEE TCAS-I 2022)<br>• General lossy compression rounding literature | **LOW RISK / STRONG OPPORTUNITY** | Prior PQC fault papers (Ravi 2023, Delvaux 2022) assumed any butterfly fault causes failure. Our Phase 4B audit experimentally proved that Stage 1 faults yield 100.0% valid decapsulation, while Stage 4 and 7 yield 100.0% implicit rejection. | 1. Derive formal algebraic bounds: prove the maximum fault magnitude $|\delta|_{\max}$ absorbed by `Compress_d` as a function of NTT layer $L \in \{1 \dots 7\}$.<br>2. Empirically validate across all parameter sets (ML-KEM-512, 768, 1024) with $N \ge 1,000$ per cell. |
| **4. Cross-Implementation Fault Divergence**<br>Comparing fault behavior between formally verified portable C (`mlkem-native`) and SIMD-optimized dynamically linked C (`liboqs`) | • PQCA `mlkem-native` verification docs (2024)<br>• Compiler optimization security literature | **MODERATE RISK** | Standard benchmarking across implementations is routine. However, studying whether formal verification guarantees (CBMC) affect fault sensitivity compared to SIMD assembly is underexplored. | 1. Implement identical fault hooks or assembly breakpoints across both engines.<br>2. Prove statistically whether outcome distributions diverge due to compiler register allocation, instruction scheduling, or vectorization. |
| **5. Cryptographic Desynchronization $\to$ Telecommand Framing Impact**<br>Connecting FO implicit rejection to multi-stage telecommand rejection ($p \ge 1 - 2^{-32}$) and autonomous recovery | • CCSDS SDLS (355.0-B-1)<br>• ESA E2EQSS Report (2024)<br>• Geissler et al. (IEEE AERO 2023) | **LOW RISK / STRONG OPPORTUNITY** | Space communication literature focuses purely on link bandwidth/latency; crypto literature stops at the algorithm return boundary. No paper connects cryptographic session desynchronization to telecommand framing drops and autonomous retransmission. | 1. Align the simulation with standard CCSDS Telecommand (TC) Space Data Link Protocol framing structures.<br>2. Measure session recovery latency and link throughput under variable orbital bit error rates (BER). |
| **6. Selective Software-Only Resilience for Lattice Arithmetic**<br>Using sensitivity maps to protect only critical operations (Layers 4-7, accumulators) with <25% CPU overhead | • Bindel et al. (IEEE TR 2017)<br>• Mozaffari-Kermani et al. (IEEE TCAD 2023, TETC 2024) [FPGA AIC, RESWO] | **MODERATE RISK** | Hardware error detection on FPGAs is extensively published by Mozaffari-Kermani. However, software-only selective assertions for general-purpose processors are rare; most software uses 200% full duplication. | 1. Design concrete, lightweight software assertions (e.g., intermediate norm bounds, modular polynomial checksums).<br>2. Measure exact clock cycles on ARM/RISC-V and demonstrate $>95\%$ fault coverage with $<25\%$ overhead. |
| **7. ML-DSA Rejection Loop Hang & Nonce Tampering**<br>Faulting rejection sampling counters, norm checks, or commitment vectors in FIPS 204 | • Bruinderink & Pessl (CHES 2018)<br>• Krahmer et al. (TCHES 2024)<br>• Bindel et al. (FDTC 2016) | **HIGH RISK** | DFA and Signature Correction attacks on Dilithium are heavily published. Targeting the norm check or rejection loop is well-known. | Do NOT merely reproduce key recovery on Dilithium. Focus on *execution availability* and *loop termination bounds*: quantify the probability of infinite loops (SEFIs) vs. desynchronization under transient upsets in flight software. |
| **8. Formal Verification of Fault Resilience Properties**<br>Using CBMC or SMT solvers to prove fault detection properties in C source code | • PQCA / AWS `mlkem-native` CBMC contracts (2024)<br>• Richter-Brockmann et al. (TCHES 2023) [FIVER, RTL netlists] | **MODERATE RISK** | CBMC currently proves memory safety under *fault-free* semantics. Hardware tools (FIVER) verify RTL. Extending CBMC function contracts to formally prove fault detection properties in C lattice code is novel, but technically demanding. | Formulate precise CBMC loop contracts that prove assertions catch all single-bit corruptions in specific buffers without timing side channels. Must avoid getting bogged down in theorem prover complexity. |

---

## 3. Synthesis: The Defensible Core Contribution

To ensure high publishability and zero vulnerability to prior-art rejections, the project should construct a unified research narrative centered on **three interlocking, low-to-moderate risk pillars**:

```
                              [ CORE RESEARCH PILLAR ]
          The Triad of Quantization Absorption, Selective Software
               Resilience, and Autonomous Protocol Recovery
                                         |
     +-----------------------------------+-----------------------------------+
     |                                   |                                   |
[ PILLAR 1: MATHEMATICS ]      [ PILLAR 2: IMPLEMENTATION ]       [ PILLAR 3: SYSTEM PROTOCOL ]
NTT Diffusion vs Lossy         Sensitivity-Guided Selective       Cryptographic Desync in
Quantization Absorption        Software-Only Resilience           CCSDS Telecommand Framing
• Closed-form error bounds     • Lightweight polynomial checks    • 6-stage receiver rejection
• Self-healing Layer 1         • <25% CPU overhead vs 200% TMR    • Autonomous link recovery
• 100% implicit rej in L4-7    • Tested on C90 mlkem-native       • Zero silent command execution
```

This framing:
1. Avoids repeating established attack claims (FO bypass or twiddle zeroization).
2. Avoids false claims of physical radiation qualification.
3. Provides concrete mathematical theorems, empirical implementations, and systems-level protocol measurements.
