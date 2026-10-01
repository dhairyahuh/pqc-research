# Related Work Synthesis: Fault Tolerance, Cryptographic Attacks, and Space Resilience
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 7L — Independent Literature Review, Research Gap Validation, and Novelty Assessment  
**Date:** October 2026  
**Status:** Peer-Reviewed Synthesis  

---

## 1. Executive Summary

This synthesis provides a comprehensive critical review of the academic and technical literature intersecting four fields: **Algorithm-Based Fault Tolerance (ABFT)**, **Physical and Logical Fault Attacks on Lattice-Based Cryptography**, **Post-Quantum Cryptographic (PQC) Implementation Hardening**, and **Space-System Radiation Resilience**. 

The synthesis examines how existing works approach fault detection and recovery in the Number Theoretic Transform (NTT), evaluates the threat models posed by physical fault injection against the NIST FIPS 203 (ML-KEM) standard, and delineates the exact technical boundaries separating prior art from the implementation and findings of this project.

---

## 2. Area A: Algorithm-Based Fault Tolerance (ABFT) & Arithmetic Invariants

### 2.1 Foundational ABFT and Transform Protection
Algorithm-Based Fault Tolerance was formally introduced by **Huang & Abraham (1984)** for systolic matrix operations. Their seminal insight was that linear transformations permit checksum encoding ($A_c = [A \mid A \cdot \mathbf{e}]$) where arithmetic operations on encoded matrices preserve the checksum relationship, enabling error detection and single-fault location with minimal area overhead (~10–20%).

In **1988, Jou & Abraham** extended ABFT principles to Fast Fourier Transform (FFT) networks. They recognized that while intermediate stages in FFT butterfly networks do not maintain simple linear column/row checksums due to twiddle factor phase rotations, overall network energy conservation (Parseval's theorem: $\sum_{n=0}^{N-1} |x_n|^2 = \frac{1}{N}\sum_{k=0}^{N-1} |X_k|^2$) and stage-by-stage weighted checksums can detect transient butterfly arithmetic faults. However, Jou & Abraham’s formulation was fundamentally rooted in complex floating-point or fixed-point arithmetic, which is subject to rounding noise and cannot be directly mapped to finite rings $\mathbb{Z}_q$.

### 2.2 Algebraic Invariant Checking (AIC) for the Number Theoretic Transform
The Number Theoretic Transform operates over the finite field or ring $\mathbb{Z}_q$ (with prime $q = 3329$ and degree $n = 256$ in ML-KEM). Because arithmetic in $\mathbb{Z}_q$ is exact (modular), roundoff noise does not exist. However, any single-bit transient error completely scrambles polynomial coefficients, propagating through the $\log_2(n) = 7$ transform layers and causing Silent Data Corruption (SDC).

Recent research has adapted algebraic invariants to NTT hardware accelerators on FPGAs:
- **Paul, Baidya, Mandal, and Guha (ACM TECS 2024/2026)** introduced *Full Recomputation AIC (FR-AIC)* and *Partial Recomputation AIC (PR-AIC)* for NTT processing elements on Xilinx FPGAs. Their scheme checks algebraic consistency between input operands and output butterfly results. However, their work was confined strictly to **forward NTT** Cooley-Tukey butterflies in hardware DSP slices, targeting fault detection flags rather than autonomous recovery.
- **Sarker et al. (2022/2023)** and **Canto et al. (2023)** explored time-redundant recomputation techniques on FPGAs, including:
  - *RENO (Recomputing with Negated Operands)*: Inverts input operand signs ($x \to -x \pmod q$) and verifies that butterfly outputs satisfy additive inverse symmetry.
  - *RESWO (Recomputing with Swapped Operands)*: Swaps symmetrical operands to identify asymmetry caused by stuck-at faults in Barrett multipliers.
  - *RESO / RECO (Recomputing with Shifted/Scaled Operands)*: Scales inputs by modular constants to detect datapath corruptions.

### 2.3 Mathematical Divergence: Cooley-Tukey vs. Gentleman-Sande Invariants
A crucial limitation of prior literature is the near-universal focus on the forward Cooley-Tukey (CT) butterfly, neglecting the distinct algebraic structure of the inverse Gentleman-Sande (GS) butterfly:

1. **Forward Cooley-Tukey (CT) Butterfly:**
   Given inputs $u, v \in \mathbb{Z}_q$ and twiddle factor $\zeta \in \mathbb{Z}_q$, the outputs are:
   $$u' \equiv u + v\zeta \pmod q, \quad v' \equiv u - v\zeta \pmod q$$
   The forward butterfly admits a decoupled sum invariant:
   $$u' + v' \equiv 2u \pmod q$$
   Notice that the twiddle product $v\zeta$ cancels out completely in the sum. This allows $u$ to be verified independently of the twiddle multiplication. The complementary difference invariant:
   $$u' - v' \equiv 2(v\zeta) \pmod q$$
   subsequently checks the integrity of the modular product.

2. **Inverse Gentleman-Sande (GS) Butterfly:**
   In the inverse transform, the operations are reversed:
   $$u' \equiv u + v \pmod q, \quad v' \equiv \zeta(u - v) \pmod q$$
   Here, the sum of outputs is:
   $$u' + v' \equiv (u + v) + \zeta(u - v) \pmod q$$
   Unlike the CT butterfly, the twiddle factor $\zeta$ **does not cancel out** in the sum of outputs. Consequently, checking $v'$ cannot bypass the twiddle multiplication. To establish rigorous error detection in the inverse NTT, one must decouple the checks:
   $$\text{Invariant 1 (Sum): } u' \equiv u + v \pmod q$$
   $$\text{Invariant 2 (Recomputed Difference): } v' \equiv \zeta(u - v) \pmod q$$
   Prior literature often overlooked this structural difference, assuming that invariant formulations from forward CT butterflies could be mirrored symmetrically to the inverse transform.

---

## 3. Area B: Cryptographic Fault Attacks on Lattice-Based Schemes

### 3.1 Fault Injection Surface in ML-KEM Decapsulation
Physical fault attacks against lattice-based schemes represent a severe threat to post-quantum deployments:
- **Ravi, Roy, Chattopadhyay, and Bhasin (TCHES 2020)** demonstrated that electromagnetic (EM) and laser fault injection can create a "plaintext-checking oracle" in IND-CCA secure lattice-based schemes, converting decryption failures into secret-key leaking inequalities.
- **Hermelink, Pessl, and Pöppelmann (INDOCRYPT 2021)** formulated the *Fault-Enabled Chosen-Ciphertext Attack* on CRYSTALS-Kyber. By injecting a single transient bit-flip into the ciphertext polynomial decoding routine during decapsulation, they bypassed the Fujisaki-Okamoto (FO) integrity checks. Over approximately 6,000 fault injections, the full secret key $s$ was extracted with high probability.
- **Delvaux (TCHES 2022)** published the *Roulette* attack family against masked Kyber implementations, showing that transient faults injected during NTT polynomial multiplication or binomial sampling can bypass high-order masking countermeasures, demonstrating that side-channel resistance does not confer fault resilience.

### 3.2 Twiddle Constant Corruption Attacks
A seminal contribution to the threat model was made by **Ravi, Bhasin, Roy, and Chattopadhyay (TCHES 2023)** in *"Fiddling the Twiddle Constants – Fault Injection Analysis of the Number Theoretic Transform"*. They proved that:
1. If an attacker injects a fault into the twiddle factor lookup table (e.g., zeroizing $\zeta$ or replacing $\zeta$ with 1), the NTT butterfly operation collapses:
   $$u' \equiv u + 0 = u, \quad v' \equiv u - 0 = u \pmod q$$
2. This collapses the output polynomial ring dimension from 256 to smaller sub-rings, destroying algebraic entropy.
3. In decapsulation, this ring collapse leaks secret key coefficients directly through the decrypted message $m'$.

This finding directly motivates the **common-mode limitation analysis** of the current research: because both the primary butterfly computation and the difference invariant verification rely on reading the twiddle table $\zeta$, a corrupted twiddle factor stored in ROM/RAM represents a common-mode fault that cannot be detected by internal butterfly invariants alone.

---

## 4. Area C: PQC Implementation Resilience & Software Hardening

### 4.1 Software-Sequential DMR vs. Local Invariant Rollback
In software implementations (e.g., NIST reference C, `pqm4` library on ARM Cortex-M4), fault resilience has traditionally been addressed via coarse-grained redundancy:
- **Dual Modular Redundancy (DMR):** The entire NTT operation (or the entire decapsulation routine) is executed twice sequentially, and the output arrays are compared coefficient by coefficient.
- **DMR Overhead Reality:** In single-core embedded processors, DMR inherently requires $\ge +100\%$ additional CPU cycle latency, plus memory overhead for shadow buffers. When control logic, verification loops, and buffer copying are accounted for, empirical software-sequential DMR overhead routinely reaches **+140% to +160%** (as validated in the Phase 7I/7J repository benchmarks).
- **Fail-Stop vs. Recovery:** Standard software DMR is strictly **fail-stop**: when a mismatch is detected, execution aborts, returning an error code. In high-availability or remote environments (such as satellites in deep space), aborting cryptographic sessions forces protocol timeouts, packet retransmissions, or session renegotiations.

### 4.2 Two-Tiered Semantic Resilience in FIPS 203
Under **NIST FIPS 203 (Section 7.3)**, ML-KEM decapsulation is explicitly required to implement **implicit rejection**:
$$\text{If } c \neq c', \quad K \leftarrow \text{SHAKE256}(z \parallel c)$$
where $z$ is a 32-byte pseudo-random seed stored in the secret key. The standard forbids returning explicit error flags to remote callers to prevent chosen-ciphertext decapsulation oracle attacks.

This creates a critical design tension:
1. **Tier 1 (Transient Autonomous Recovery):** If an arithmetic fault in the NTT butterfly is caused by a transient SEU, local register rollback can repair the computation in-place, allowing decapsulation to succeed legitimately ($K = \text{SHAKE256}(K' \parallel H(c))$) without false rejections.
2. **Tier 2 (Hardened Implicit Rejection):** If a persistent fault occurs or uncorrectable corruption persists, the system must **fail safely** by ensuring that corrupted plaintext $m'$ never leaks, driving the output deterministically to the pseudo-random rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
The current project’s public API fail-stop hardening ensures that even if callers discard status return codes, the internal decapsulation logic forces implicit rejection unconditionally.

---

## 5. Area D: Space-System Radiation Resilience & SWIFI Methodology

### 5.1 Radiation Effects in Space Environments
In orbital environments (LEO, MEO, GEO, and interplanetary space), ionizing radiation induces physical effects in semiconductor microelectronics:
- **Single-Event Upsets (SEU):** A heavy ion, galactic cosmic ray (GCR), or high-energy proton deposits charge in a silicon bistable cell (SRAM cell, register flip-flop), inverting its logical state ($0 \to 1$ or $1 \to 0$) without permanent damage (**Dodd & Massengill, IEEE TNS 2003**).
- **Single-Event Transients (SET):** Voltage spikes generated in combinational logic that are latched into downstream registers if they coincide with clock edges.
- **Multiple-Node Upsets (MNU):** High Linear Energy Transfer (LET) particles traversing modern deep-submicron dies deposit charge across multiple adjacent cells simultaneously.

Spacecraft on-board data handling (OBDH) architectures conform to rigorous dependability standards (e.g., **ECSS-Q-ST-60-15C**, **NASA-HDBK-4002A**). Avionics systems on small satellites (CubeSats, SmallSats) increasingly rely on Commercial Off-The-Shelf (COTS) System-on-Chip (SoC) architectures (e.g., ARM Cortex-A53, RISC-V) to execute heavy post-quantum algorithms, making software-level fault tolerance imperative.

### 5.2 Methodological Reality: SWIFI vs. Physical Beam Testing
A rigorous academic manuscript must clearly articulate the limitations of **Software-Implemented Fault Injection (SWIFI)**:
- **Hsueh, Tsai, and Iyer (IEEE Computer 1997)** established the taxonomy and boundary conditions of SWIFI tools (e.g., FERRARI, FINE). SWIFI accurately models the architectural manifest state of single-bit and multi-bit register upsets at instruction boundaries.
- **Physical Non-Equivalences:** SWIFI cannot replicate analog physical phenomena:
  1. *Sub-cycle timing transients:* Glitches that violate setup/hold times during intermediate ALU pipeline stages.
  2. *Single-Event Latchup (SEL):* Parasitic PNPN thyristor activation causing destructive high-current short circuits.
  3. *Unmapped peripheral and microarchitectural registers:* Hidden speculative execution registers, branch prediction tables, and cache tagging units outside the C compiler's accessible register set.
- Consequently, this project’s results represent **algorithmic and architectural fault resilience**, not physical radiation hardness assurance. Claims of "radiation tolerance" must always be qualified as architectural resilience against the canonical SEU register fault model.
