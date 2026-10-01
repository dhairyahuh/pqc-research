# Input Integrity and Duplicate-Execution Resilience Analysis

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Evaluation Target:** NIST FIPS 203 ML-KEM-768 Ciphertext & Secret Key Integrity

---

## 1. The Common-Mode Blind Spot of Duplicate Decapsulation (DMR)

Duplicate Modularity Redundancy (DMR), evaluated in Phase 6 as Candidate A1, recomputes `mlkem768_dec(ss, ct, sk)` twice and verifies that `ss1 == ss2`.

While DMR achieves high empirical detection (96.7% - 100%) against single transient Single-Event Transients (SET) occurring during one of the execution passes, **it fails catastrophically against common-mode input corruption**:

### Failure Analysis

Consider a physical SEU occurring in the spacecraft's communication SRAM buffer prior to `mlkem768_dec` invocation:
$$ct \to ct^* = ct \oplus e \quad (e \ne 0)$$

When DMR executes:
$$\text{Pass 1:} \quad ss_1 \leftarrow \text{Decaps}(ct^*, sk)$$
$$\text{Pass 2:} \quad ss_2 \leftarrow \text{Decaps}(ct^*, sk)$$

Because both passes read the identical corrupted buffer $ct^*$, and the algorithm is deterministic:
$$ss_1 = ss_2 = ss^* \ne ss_{\text{clean}}$$

The DMR comparator evaluates:
$$\text{memcmp}(ss_1, ss_2, 32) == 0 \implies \text{PASS}$$

DMR yields **0.0% detection** (0/150 trials detected). Both the spacecraft and ground station believe decapsulation succeeded, yet they possess completely mismatched keys, causing fatal session desynchronization.

---

## 2. Integrity Tag vs Cryptographic Validity

We explicitly distinguish **integrity tags** from cryptographic message authentication:
1. **Cryptographic Validity (FO Transform):** In FIPS 203, decapsulation re-encrypts the decrypted message $m$ to produce $c'$, comparing $c' == c$. If $c' \ne c$, it **implicitly rejects** by replacing the shared secret with pseudo-random key $K' = \text{J}(z, c)$. However, because implicit rejection outputs 0 (success) to the caller, the application has no indication that a corrupted ciphertext was processed.
2. **Physical Data Integrity (CRC32 / Checksum):** An integrity tag verifies that the memory representation in SRAM has not suffered physical degradation (single-event upsets, bit flips) between message reception and decapsulation invocation.

---

## 3. Empirical Comparative Evaluation

Across 150 randomized single-bit and multi-bit perturbations in the 1088-byte ciphertext buffer:

| Mechanism | Detection Rate | Latency | Memory Overhead |
| :--- | :--- | :--- | :--- |
| **Unprotected Baseline** | 0.0% (Silent Desync) | 42.77 µs | 0 bytes |
| **Full Duplicate Decapsulation (DMR)** | **0.0% (Complete Failure)** | 86.81 µs (+103.0%) | 2400 bytes |
| **Pre-Invocation CRC32-IEEE** | **100.0% (150/150)** | **1.21 µs (+2.8%)** | **4 bytes** |

### Conclusion

Full duplicate execution cannot protect against pre-invocation memory corruption. Incorporating a 32-bit CRC or lightweight checksum before invocation provides **100% protection against input buffer SEUs** at less than 3% of the computational cost of DMR.
