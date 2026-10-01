# Phase 7G: Precise Fault Model Specification and Trust Boundaries

## 1. Executive Summary & Objective

In Phase 7F, an independent audit revealed that earlier claims regarding 100% transient fault recovery across all ML-KEM NTT layers rested upon a synthetic simulation model that:
1. Relied on an unverified assumption that reusing intermediate products $t = v \cdot \zeta$ could detect faults occurring in $t$ itself.
2. Executed NTT checks via a harness prototype that passed `NULL` callbacks during end-to-end decapsulation.
3. Obscured the fundamental physical distinction between ALU internal register corruptions, memory/operand bit flips, and persistent structural defects.

Phase 7G establishes a mathematically rigorous, physically traceable fault model for spaceborne post-quantum cryptographic systems. We delineate explicit operational boundaries between what a mathematical butterfly invariant can detect, what requires independent recomputation, what falls back to algorithmic implicit rejection, and what is outside the domain of arithmetic fault tolerance.

---

## 2. Hardware Architecture & Execution Model

The target system is an onboard satellite flight computer (e.g., radiation-tolerant RISC-V RV64GC, ARM Cortex-R52, or high-performance SoC) executing FIPS 203 ML-KEM-768 decapsulation (`mlk_kem_dec`).

During decapsulation, NTT operations occur along the critical path in two primary routines:
1. **$\text{NTT}(\mathbf{s})$**: Converting secret key polynomials to the frequency domain (or loaded pre-transformed).
2. **$\text{NTT}(\mathbf{u})$ / Forward Transform of Ciphertext Polynomials**: Transforming vector $\mathbf{u}$ prior to polynomial inner products $\hat{\mathbf{u}} \circ \hat{\mathbf{s}}$ and matrix-vector multiplications during Fujisaki-Okamoto (FO) re-encryption.

### Native Butterfly Unit Structure

Within `mlk_ntt_butterfly_block` (in [poly.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c)), the Cooley-Tukey forward butterfly computes:
$$t = \text{fqmul}(v, \zeta) = (v \cdot \zeta \cdot Q^{-1} \pmod R) \pmod q$$
$$u' = u + t \pmod q$$
$$v' = u - t \pmod q$$
where $q = 3329$, $R = 2^{16}$, and $\zeta \in \mathbb{Z}_q$ is the stage twiddle factor loaded from `mlk_zetas`.

---

## 3. Comprehensive Taxonomy of Fault Classes

We define eight mutually exclusive fault classes spanning the operational lifecycle of the native butterfly computation:

| Class ID | Target Fault Location | Timing Window | Duration | Scope | Assumed Trusted State |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Class 1** | Intermediate product register $t = \text{fqmul}(v, \zeta)$ | Post-multiplier, pre-adder/subtractor | Single cycle (Transient SEU) | Single 16-bit word | Input registers $(u, v)$ and twiddle $\zeta$ |
| **Class 2** | Twiddle factor $\zeta$ operand | Memory fetch or pipeline operand latch | Single cycle (Transient SEU) | Single 16-bit word | Input registers $(u, v)$ |
| **Class 3** | Butterfly output register ($u'$ or $v'$) | Post-ALU adder/subtractor, pre-store | Single cycle (Transient SEU) | Single 16-bit word | Inputs $(u, v)$, twiddle $\zeta$, intermediate $t$ |
| **Class 4** | Joint output perturbation ($u' \oplus \Delta, v' \oplus \Delta$) | Common-mode latch corruption | Single cycle (Transient MBU) | Two 16-bit words | Inputs $(u, v)$, twiddle $\zeta$, intermediate $t$ |
| **Class 5** | Pre-NTT input operand ($u$ or $v$) | Prior to butterfly execution | Persistent in ciphertext/secret | Single or multiple words | None (External input corruption) |
| **Class 6** | Butterfly execution unit (ALU stuck-at) | All butterfly cycles / permanent | Permanent (TID / Hard SEFI) | All arithmetic in butterfly | None (Hardware permanent failure) |
| **Class 7** | Fujisaki-Okamoto control decision barrier | Ciphertext comparison & key selection | Single cycle (Transient SEU) | Condition flag / selector | Hash state & dual-rail register |
| **Class 8** | Negative control (Nominal execution) | Full decapsulation cycle | N/A | None | System baseline |

---

## 4. Analytical Characterization of Each Threat Class

### Class 1: Intermediate Multiplier Result Corruption ($t$)
- **Physical Mechanism**: A cosmic ray heavy-ion strike or proton interaction deposits charge in the pipeline register holding the output of Montgomery multiplication $t = \text{fqmul}(v, \zeta)$.
- **Mathematical Form**: $t^* = t \oplus \delta$ where $\delta \neq 0$.
- **Downstream Consequence**:
  $$u^* = u + t^* = u + t + \delta \pmod q$$
  $$v^* = u - t^* = u - t - \delta \pmod q$$
- **Detection Invariant Analysis**:
  - *Difference Invariant*: $(u^* - v^*) \equiv (u + t + \delta) - (u - t - \delta) = 2t + 2\delta \pmod q$.
    - If the monitor **reuses** $t^*$: $2t^* = 2t + 2\delta$. The invariant $(u^* - v^*) \equiv 2t^*$ **trivially holds**. Thus, Reused-$t$ has a **100% theoretical blind spot** for Class 1.
    - If the monitor **recomputes** $t_{\text{check}} = \text{fqmul}(v, \zeta)$: $(u^* - v^*) - 2t_{\text{check}} = 2\delta \neq 0 \pmod q$. The mismatch is detected with probability 1.
- **Recovery Strategy**: When detected via recomputation, local rollback from stored $(u, v)$ and in-place re-execution restores correct $t, u', v'$.

### Class 2: Twiddle Factor Operand Corruption ($\zeta$)
- **Physical Mechanism**: Bit flip during SRAM read of `mlk_zetas` table or in the twiddle factor pipeline operand latch.
- **Mathematical Form**: $\zeta^* = \zeta \oplus \delta$.
- **Downstream Consequence**: $t^* = \text{fqmul}(v, \zeta^*)$.
- **Detection Invariant Analysis**:
  - Both Reused-$t$ and Recomputed-$t$ (if Recomputed-$t$ fetches from the same corrupted operand latch) calculate $t^*$ identically from $\zeta^*$.
  - In the absence of an independent ROM twiddle verification or dual-path table lookup, the arithmetic invariant $(u' - v') = 2t^*$ is satisfied.
  - **System Safety Outcome**: Twiddle corruption propagates downstream into an invalid polynomial. The Fujisaki-Okamoto re-encryption check fails deterministically ($\hat{c}' \neq c$), triggering **safe implicit rejection** ($K_{\text{rej}}$). Undetected corruption is prevented by the cryptographic protocol barrier.

### Class 3: Butterfly Output Register Corruption ($u'$ or $v'$)
- **Physical Mechanism**: Bit flip in the accumulator/result register holding $u'$ or $v'$ prior to memory store.
- **Mathematical Form**: $u^* = u' \oplus \delta$ (or $v^* = v' \oplus \delta$).
- **Detection Invariant Analysis**:
  - *Difference Check*: $(u^* - v') = (u + t + \delta) - (u - t) = 2t + \delta \neq 2t \pmod q$.
  - Both Reused-$t$ and Recomputed-$t$ detect this mismatch immediately.
- **Recovery Strategy**: Local register rollback to saved $(u, v)$ and single retry yields 100% recovery.

### Class 4: Symmetric Common-Mode Perturbation
- **Physical Mechanism**: Single Event Multi-Bit Upset (MBU) across adjacent output registers or shared bus line corrupting both outputs equally: $u^* = u' + \Delta$, $v^* = v' + \Delta$.
- **Detection Invariant Analysis**:
  - *Difference Check Blind Spot*: $(u^* - v^*) = (u' + \Delta) - (v' + \Delta) = u' - v' = 2t \pmod q$. The difference invariant alone **fails** to detect symmetric faults.
  - *Sum Invariant*: $(u^* + v^*) = (u' + \Delta) + (v' + \Delta) = 2u + 2\Delta \neq 2u \pmod q$.
  - The joint dual invariant (`Diff && Sum`) guarantees complete detection.

### Class 5: Pre-NTT Input Operand Corruption
- **Physical Mechanism**: Radiation strike in DRAM/SRAM holding ciphertext vector $\mathbf{u}$ or secret key vector $\mathbf{s}$ before NTT begins.
- **Detection Invariant Analysis**:
  - The butterfly executes valid arithmetic on invalid input. Internal butterfly invariants cannot and should not detect that the input was wrong.
- **System Safety Outcome**: Forward FO re-encryption detects that the decapsulated candidate does not reproduce the ciphertext, triggering FIPS 203 implicit rejection ($K_{\text{rej}}$).

### Class 6: Persistent Stuck-at Butterfly Fault
- **Physical Mechanism**: Total Ionizing Dose (TID) or Single Event Gate Rupture (SEGR) permanently bridges an ALU line to VDD or GND.
- **Detection Invariant Analysis**:
  - Monitor detects arithmetic mismatch on initial execution.
  - Rollback and retry re-executes on the broken ALU, failing the invariant a second time.
  - **Mitigation Requirement**: Retry limit of $N=1$. Upon repeated mismatch, monitor marks state as `persistent`, sets an unmaskable error flag, and aborts NTT. The decapsulation engine detects this flag and forces immediate implicit rejection ($K_{\text{rej}}$).

### Class 7: FO Control Decision Gate Perturbation
- **Physical Mechanism**: Fault injected into the conditional branch or select instruction that chooses between authentic shared secret $K$ and pseudo-random reject key $K_{\text{rej}}$.
- **Mitigation Requirement**: Reverse dual-rail decision barrier (`fail_stop_flags`) implemented in Phase 7C/7D ensures that single-bit tampering forces safe fallback.

---

## 5. Explicit Trust Boundaries and Out-of-Scope Faults

### What the Native NTT Invariant Assumes (Trusted Computing Base)
1. **Local Register Storage**: Registers holding initial butterfly inputs $(u, v)$ during the single butterfly execution are not subjected to a simultaneous second physical particle strike during the 10–20 clock cycles of local evaluation and retry.
2. **Instruction Decoding**: The CPU continues to execute the instruction stream without catastrophic control-flow hijacking (addressed separately by hardware watchdog timers and control-flow integrity).

### Explicitly Excluded Fault Classes (Out of Scope for Butterfly Invariant)
1. **Simultaneous Multi-Point Particle Strikes**: Heavy-ion strikes that hit the ALU, the register file, and the program counter within the same sub-microsecond window.
2. **Malicious Side-Channel Attacks**: The monitor is designed for space radiation single-event effects (SEE), not power analysis or electromagnetic fault injection by an active physical adversary with laboratory equipment.
