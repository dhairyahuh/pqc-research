# Comprehensive Research Gap and Contribution Assessment

**Auditor:** Independent Cryptographic Auditor & Implementation Research Team  
**Evaluation Scope:** Prior Literature Alignment, Theoretical vs. Implementation Boundaries, and Novelty Defense  
**Evaluation Date:** 2026-10-02  

---

## 1. Prior Literature Cross-Check and Overlap Analysis

| Research Domain | Seminal Works Reviewed | What Prior Work Has Already Established | What Was Previously Claimed in Repo | Independent Audit Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Twiddle Factor Faults** | Ravi et al. (*IACR TCHES 2023*) | Proved that twiddle factor corruptions collapse NTT ring entropy, bypass localized butterfly output checks, and allow full secret-key extraction. Recommended table hashing or recomputation. | "Discovered a critical shared-constant vulnerability in ML-KEM NTT monitoring." | **Prior Art (Not Novel).** The vulnerability of localized checks to twiddle corruption was formally established by Ravi et al. in 2023. Our audit confirms this is an expected mathematical limitation, not a new vulnerability discovery. |
| **NTT Algebraic Invariants** | Paul et al. (*IEEE TCAD 2024*);<br>Sarker et al. (*IEEE TVLSI 2023*) | Formulated algebraic invariant checks ($u'+v' \equiv 2u$) for forward Cooley-Tukey NTT butterflies in hardware FPGA pipelines. Detection only (no rollback). | "First implementation of combined forward and inverse NTT monitoring with in-place recovery." | **Engineering Integration.** Forward invariants are directly from prior literature. Extending to Gentleman-Sande ($u'+v'=u+v$) and implementing in C software is a valuable engineering contribution, but not a mathematical breakthrough. |
| **Decapsulation Fault Attacks** | Hermelink et al. (*INDOCRYPT 2021*);<br>Ueno et al. (*IACR TCHES 2022*) | Demonstrated that faulting decapsulation polynomial operations or FO re-encryption comparators allows key recovery via Statistical Ineffective Fault Analysis (SIFA). | "Zero undetected key corruptions proves complete fault immunity." | **Overstated Claim.** Zero SDC was observed under evaluated single-point software faults. However, SIFA and multi-fault comparator bypass were not evaluated under physical EM/clock injection. |
| **Software Fault Recovery** | Standard Fault Tolerance & FT-PQC | Checkpointing, shadow registers, and rollback recovery are established techniques in dependable computing (e.g., SIFT, EDAC). | "Autonomous in-place rollback achieves 100% recovery across all threat classes." | **Disproved.** Recovery is achievable exclusively for transient ALU adder/multiplier faults ($49.9\%$ overall). Corrupted constants, memory, and persistent faults achieve $0\%$ recovery. |

---

## 2. Separation of Findings

### 2.1 Known Implementation Limitations (Defects)
1. **Dead Reference Constant Array:** `static const int16_t g_trusted_zetas[128]` declared in [`mlkem_fault_hooks.c:555`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L555) was never hooked into the monitor.
2. **Instrument Hook Race Condition:** `hook_mid_invntt_pre_butterfly` placed after `u_saved = r[j]` in [`poly.c:557-564`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L557-L564) created an artificial 100% detection rate for what was supposed to simulate pre-latch memory corruption.
3. **Tautological Retry Verification:** The post-retry checks $\text{sum\_retry} \equiv 0$ and $\text{diff\_retry} \equiv 0$ in [`mlkem_fault_hooks.c:653`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L653) are polynomial identities that evaluate to zero for all inputs, failing to verify rollback snapshot integrity.

### 2.2 Inherent Mathematical Boundaries
1. **Constant Table Blind Spot:** An in-tree butterfly monitor that receives its twiddle constant directly from the arithmetic caller can never detect constant table corruption without external reference integrity.
2. **Shadow Latch Boundary:** An in-tree monitor that latches its recovery snapshot from local array memory cannot detect corruptions that occurred prior to latching.

### 2.3 Potentially Unexplored Combinations
- **Coordinating Microarchitectural Fail-Stop with Protocol-Level Retransmission:** Rather than attempting unsafe in-place software rollback on bare-metal registers (which introduces timing channels and circular dependencies), immediately quenching corrupted decapsulation into FIPS 203 implicit rejection and handling recovery via authenticated transport layer retransmission.

---

## 3. Candidate Contribution Statements

### Candidate 1: Narrow Implementation and Empirical Evaluation Contribution
> *"An Empirical Audit of Algorithm-Based Fault Tolerance in ML-KEM-768 Software: Boundaries of In-Tree Butterfly Invariants and Shared-Constant Blind Spots."*
- **Scope:** Document the empirical behavior of forward and inverse NTT invariant monitors in C software; demonstrate that localized butterfly checks exhibit a 100% blind spot for static twiddle factor tables and pre-latch memory faults; evaluate the performance trade-off against software DMR.
- **Minimum Requirements Before Claiming:**
  1. Complete removal of dead code and correction of hook ordering.
  2. Multi-platform benchmarking on ARM Cortex-M4 and RISC-V (not only Apple Silicon).
  3. Formal citation and differential comparison with Ravi et al. (TCHES 2023) and Paul et al. (TCAD 2024).

### Candidate 2: Recovery-Verification Architecture Contribution
> *"Verifiable Fault Resilience for Post-Quantum Key Encapsulation: Breaking Circular Verification in Software-Based Rollback."*
- **Scope:** Formally define the circular verification vulnerability in software rollback; introduce snapshot parity protection and non-tautological diverse recomputation for ML-KEM decapsulation; prove that fail-stop quenching eliminates macro-architectural timing side-channels.
- **Minimum Requirements Before Claiming:**
  1. Implementation and formal verification of the snapshot parity mechanism.
  2. Constant-time TVLA (Test Vector Leakage Assessment) or dudect empirical timing analysis comparing retry vs. fail-stop policies.
  3. Hardware-fault injection (e.g. EMFI or clock glitching) validating that physical fault injection matches simulated behavior.

### Candidate 3: Broader System-Level Contribution (Recommended Direction)
> *"Cross-Layer Fault Resilience for Post-Quantum Space Communications: Coordinating Computational Fail-Stop with Packet-Level Error Control."*
- **Scope:** Integrate ML-KEM-768 decapsulation fail-stop enforcement into a simulated space communication framework (e.g. CCSDS Space Packet Protocol / authenticated transport). Proves that delegating recovery from fragile microarchitectural rollback to protocol-level ARQ achieves higher reliability and zero key leakage under joint radiation SEUs and channel bit errors.
- **Minimum Requirements Before Claiming:**
  1. Discrete-event network simulation modeling realistic orbital radiation flux and packet error rates.
  2. Formally bounded security proof establishing that implicit rejection prevents fault-assisted key extraction across lossy channels.
  3. Experimental demonstration that the cross-layer framework outperforms both unmonitored baseline and full DMR under heavy radiation environments.
