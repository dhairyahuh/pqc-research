# Literature Review: Fault Detection, Algebraic Invariants, and Localized Recovery for Number-Theoretic Transforms in Post-Quantum Cryptography

**Date:** 2026-10-17  
**Scope:** Thematic synthesis of 7 full-text foundation papers across fault detection, NTT arithmetic, software fault tolerance, twiddle corruption, and physical radiation mechanisms.  
**Traceability:** All citations reference exact sections, pages, equations, or tables from verified full-text PDFs in `literature/p1_papers/`.

---

## 1. Fault Detection and Error Checking for NTT Operations

The Number-Theoretic Transform (NTT) is the primary computational bottleneck in lattice-based post-quantum cryptography, including the NIST-standardized Module-Lattice Key Encapsulation Mechanism (ML-KEM, FIPS 203) and Module-Lattice Digital Signature Algorithm (ML-DSA, FIPS 204). Because polynomial multiplication represents over $50\%$ to $80\%$ of total cryptographic execution cycles, hardware accelerators and optimized software implementations have been widely explored. However, their arithmetic density makes them highly sensitive to physical disturbances and adversarial fault injection.

Prior research on NTT fault tolerance has concentrated heavily on custom hardware implementations (ASIC and FPGA). Sarker et al. (2023) [p. 2418, Sec. I] developed concurrent error detection for an NTT hardware accelerator within a hardware/software co-design framework. Their architecture incorporates Recomputing with Encoded Operands (RENO) and operand swapping across four accelerator lines ($A, B, C, D$). By performing a normal cycle followed by a recomputed cycle with modularly negated operands, Sarker et al. achieve $>99.4\%$ error coverage on simulated stuck-at faults [p. 2420, Sec. IV-A]. However, their approach relies entirely on hardware multiplexers, negation circuits, and comparators on FPGA (Zynq UltraScale+ and Spartan-7), introducing a $12.7\%$ area and $8.5\%$ delay overhead [p. 2421, Table I]. Furthermore, their method is **detection-only**: upon error detection, a comparator asserts an error signal, but no localized recovery or rollback is provided.

Fritzmann et al. (2019) [pp. 1148–1153] evaluated the vulnerability of NTT implementations on a RISC-V System-on-Chip (SoC) executing the NewHope cryptosystem. They demonstrated that in an unprotected software NTT implementation, random transient bit-flips produce a Silent Data Corruption (SDC) rate between $3.66\%$ and $4.96\%$ [p. 4, Table II]. To mitigate this, Fritzmann et al. applied macro-level Dual Modular Redundancy (DMR), duplicating the entire NTT routine. While DMR reduced the effective SDC rate to $0.72\%–0.80\%$ by detecting $80.77\%$ of SDCs (168 of 208 cases), it roughly doubled execution time ($>+100\%$ overhead) and left $19.23\%$ of SDCs undetected due to common-mode architectural vulnerabilities [p. 4, Sec. VI-A].

---

## 2. Algebraic Invariants and Recomputation-Based Checking

Rather than duplicating the entire transform or relying on hardware negation cycles, recent work has explored arithmetic properties of the NTT butterfly. Paul, Baidya, Mandal, and Guha (July 2026) [pp. 70:1–70:20] proposed Algebraic Invariant Checking (AIC) for NTT processing elements on FPGA. In their Full Recomputation AIC (FR-AIC) and Partial Recomputation AIC (PR-AIC) schemes, they observe that in a forward Cooley-Tukey (CT) butterfly:
$$\alpha[k] = (U + V) \bmod q \quad \text{and} \quad \alpha[k+m] = (U - V') \bmod q$$
where $U = \alpha[k]$ and $V = \alpha[k+m] \cdot \omega \bmod q$, recomputing $V'$ with a redundant multiplier yields linear invariants [p. 70:9, Eq. 5–6]:
$$E_1 = (U + V) + (U - V') \equiv 2U \pmod q$$
$$E_2 = (U + V) - (U - V') \equiv 2V \pmod q$$
By verifying that $E_1[\log q : 1] == \alpha[k]$ or $E_2[\log q : 1] == \alpha[k+m] \cdot \omega$, Paul et al. detect arithmetic faults across adders, subtractors, and multipliers with $\approx 99.99\%$ efficiency in simulation [p. 70:17, Table 3].

In parallel, Paul, Baidya, and Guha (August 2025) [arXiv:2508.03062v1] introduced Recomputation with Encoded Modular Offsets (REMO). In word-wise Montgomery reduction (MMRFD), encoding words as $aw_i + K \cdot q$ allows the offset to cancel out modulo $q$ during reduction ($[aw_i + K \cdot q]\cdot \beta \cdot R^{-1} \equiv aw_i \cdot \beta \cdot R^{-1} \pmod q$), detecting faults if the reduced output diverges [p. 5–6, Lemma 1, Alg. 2].

**Key Limitation in Prior Invariant Work:** While mathematically elegant, both AIC (Paul 2026) and REMO (Paul 2025) are designed strictly as **FPGA hardware circuits** and cover **only forward Cooley-Tukey butterflies**. Neither paper formulates algebraic invariants for the **inverse Gentleman-Sande (GS) decimation-in-frequency butterfly**—which is required for inverse NTT in ML-KEM—and neither implements or evaluates software execution on general-purpose CPUs. Crucially, Paul et al. (2026) explicitly state that their method is **detection-only** and does not support fault recovery: *"The present AIC model focuses on fault detection and does not perform fault correction. In future work, we plan to incorporate fault correction mechanisms, such as error correction algorithms and dynamic FPGA reconfiguration"* [p. 70:18, Sec. 6].

---

## 3. Software Fault Tolerance and Localized Recovery

In general-purpose software computing, software-implemented fault tolerance (SIFT) has long sought to protect against transient hardware upsets without full hardware duplication. Reis, Chang, Vachharajani, Rangan, and August (2005) [pp. 243–254] introduced SWIFT (Software Implemented Fault Tolerance). Implemented as a compiler transformation on Intel IA-64, SWIFT duplicates all computational instructions and general-purpose registers, but avoids duplicating memory loads by relying on hardware cache/RAM ECC. Before stores and control branches, SWIFT inserts comparison instructions to ensure register consistency [p. 244, Sec. 3].

SWIFT achieved $>99\%$ transient fault detection across SPEC CPU2000 benchmarks with an average runtime overhead of $41\%$ ($1.41\times$), substantially outperforming older whole-program duplication techniques such as EDDI ($>2.0\times$) [p. 251, Table 2, Fig. 4]. However, SWIFT suffers from three fundamental limitations when applied to cryptographic software:
1. **Coarse Recovery:** SWIFT provides **detection only**. When a comparison fails, it raises an exception or branches to an error handler, relying on full process abort or checkpoint restart [p. 244, Sec. 3.1]. It provides no localized instruction or block-level rollback.
2. **Register Pressure:** Duplicating all register allocations across the entire program significantly increases register pressure, inducing stack spills in tight loops.
3. **Domain Agnosticism:** SWIFT does not exploit the mathematical structure of the underlying algorithm, treating polynomial transforms identically to arbitrary control code.

---

## 4. Fault Injection and Twiddle-Factor Corruption in Lattice-Based PQC

While transient faults in arithmetic pipelines cause localized computational divergence, corruption of persistent cryptographic state introduces catastrophic systemic vulnerabilities. Ravi, Yang, Bhasin, Zhang, and Chattopadhyay (2023) [pp. 447–481] conducted an extensive fault analysis of NTT twiddle factors across Kyber and Dilithium on an ARM Cortex-M4 microcontroller.

Using physical Electromagnetic Fault Injection (EMFI), Ravi et al. demonstrated that corrupting the pointer to the precomputed twiddle factor table during its initial load from Flash/RAM ($T \to T^*$) redirects execution to an all-zero memory buffer [p. 460, Sec. 4.2]. When twiddle factors $\omega$ are zeroed, the entire NTT collapses into a repeated constant output. On Kyber-768, this zeroization attack enabled **$100\%$ key recovery from a single faulty decapsulation exchange**, completely bypassing high-level defenses such as `Verify_After_Sign`, loop counters, and shuffling [p. 475, Table 2 & 3].

Ravi et al. proposed countermeasures including twiddle array sanity checking (verifying $\omega^n \equiv 1 \pmod q$) and output entropy analysis [p. 476, Sec. 8]. However, their work was primarily an attack demonstration; they did not analyze how internal algebraic invariant checkers behave when persistent twiddle factors are corrupted, nor did they explore whether protocol-level encapsulation checks suppress silent data corruption under persistent table faults.

---

## 5. Fault Detection versus Fault Attacks: Security Boundaries

A critical distinction must be drawn between **fault tolerance (reliability)** and **fault-attack resistance (cryptographic security)**:
- **Transient Computational Faults:** Random soft errors striking transient variables or ALU pipelines alter intermediate values for a single operation. If caught immediately, in-place rollback restores mathematical correctness without side-channel or cryptographic consequence.
- **Adversarial / Persistent Fault Attacks:** Targeted physical attacks (such as Ravi's twiddle zeroization or Fritzmann's inverse NTT coefficient clearing [Fritzmann 2019, p. 5]) attempt to induce exploitable mathematical structures in the output ciphertext or signature.

In post-quantum KEMs, the Fujisaki-Okamoto (FO) transform provides a vital protocol-level check: during decapsulation, the decrypted message $m'$ is re-encrypted ($c^* = \text{Encrypt}(pk, m', r')$) and compared against the received ciphertext $c$. If $c^* \neq c$, the KEM returns a pseudo-random reject key rather than leaking the faulty decrypted message. Thus, even when internal operational faults bypass intermediate checks, the FO transform acts as a deterministic cryptographic failsafe against message extraction, provided the comparison logic itself is not simultaneously faulted.

---

## 6. Software-Level Fault Models versus Physical Radiation Physics

A common pitfall in post-quantum literature is claiming "radiation hardness" or "spaceflight resilience" based solely on software bit-flip simulations. The physical foundations of radiation effects, comprehensively reviewed by Dodd and Massengill (2003) [pp. 583–602], demonstrate why this claim is invalid.

Dodd and Massengill establish that a physical Single-Event Upset (SEU) occurs when an ionizing particle (heavy ion, proton, or neutron) deposits charge along an electron-hole track such that the collected charge $Q_{\text{coll}}$ at a reverse-biased pn junction exceeds the critical charge $Q_{\text{crit}}$ of a bistable circuit element [pp. 584–586, Sec. III]. In combinational logic, ionizing strikes generate Single-Event Transients (SETs)—analog voltage pulses that must survive electrical attenuation (amplitude/duration), logical masking (gate sensitization), and temporal masking (arriving within the clock latching window) before being latched as an architectural bit-flip [p. 589, Sec. V].

A software-level bit-flip model (such as XORing a bit in a register or variable) represents only the **architectural manifestation** of an upset that has already successfully latched into an architectural register. Software models do **NOT** capture:
1. Multi-Cell Upsets (MCUs) caused by charge sharing across adjacent sub-micron transistor diffusions [Dodd 2003, p. 597].
2. Voltage rail transients, clock tree jitter, or analog metastability.
3. Total Ionizing Dose (TID) degradation or displacement damage.

Therefore, software fault tolerance mechanisms cannot claim physical radiation qualification; they must be rigorously characterized as providing **architectural resilience against discrete single-event register perturbations**.

---

## 7. The Supported Research Gap

Synthesizing the seven foundation papers reveals a precise, unaddressed research gap:

1. **Hardware Exclusivity of Invariants:** Existing NTT algebraic invariant checking schemes (Sarker 2023, Paul 2026, Paul 2025) are exclusively implemented as FPGA/ASIC hardware circuits. No prior work has realized fine-grained algebraic invariant monitoring in pure software for general-purpose CPUs.
2. **Transform Asymmetry:** Published invariant formulations cover only forward Cooley-Tukey (CT) butterflies. Invariants for inverse Gentleman-Sande (GS) butterflies—essential for ML-KEM decapsulation—have remained unformulated.
3. **Absence of Fine-Grained Recovery:** All existing NTT fault countermeasures are either **detection-only** (asserting an error flag / aborting) or rely on **full-routine re-execution** (DMR). No prior work implements **localized, single-butterfly register rollback and recomputation**.
4. **Twiddle Invariant Blindness & Protocol Containment:** Prior work has not characterized the boundary between fine-grained arithmetic monitoring and persistent table corruption: specifically, the vulnerability where butterfly invariants pass validly on corrupted twiddles, and how this failure mode is contained by the outer Fujisaki-Okamoto protocol.

---

## 8. Positioning of Our Research

Our work directly bridges this gap:

| Dimension | Closest Prior Art | Our Realization |
|:---|:---|:---|
| **Platform** | FPGA / ASIC hardware (Sarker 2023, Paul 2026, Paul 2025) | Pure software C99 for standard 64-bit CPUs (Apple M1 AArch64 / x86_64) |
| **Transform Coverage** | Forward CT only (Paul 2026, Paul 2025) | Dual-transform: Forward CT ($5,376$ butterflies) + Inverse GS ($4,480$ butterflies) across all 11 decapsulation transforms ($9,856$ total) |
| **Recovery Granularity** | Global abort (Paul 2026) or full-routine DMR re-execution (Fritzmann 2019, $+135.3\%$) | Localized 1-butterfly register rollback and in-place recomputation within bounded retry ($M=2$) |
| **Transient Fault Resilience** | Detection only (Sarker 2023, Paul 2026) | $100\%$ recovery of transient butterfly faults ($250/250$ trials); $0$ SDCs observed ($0/300$, bound $<1.26\%$) |
| **Twiddle Corruption Analysis** | Attack demonstrated (Ravi 2023); unaddressed in invariant defenses | Characterized failure boundary: local invariants are blind ($0.0\%$ detection), but outer FO check achieves $100\%$ containment via implicit rejection |
| **Performance Overhead** | $+41\%$ (SWIFT on IA-64); $+135.3\%$ (DMR on M1) | $+16.9\%$ decapsulation latency overhead under `-O3` ($129.51\ \mu\text{s}$ vs. $110.77\ \mu\text{s}$), zero heap allocation, $+48$ bytes BSS |
| **Physical Scope** | Often conflated with physical radiation | Explicitly bounded as an architectural SEU model, grounded in Dodd & Massengill (2003) |
