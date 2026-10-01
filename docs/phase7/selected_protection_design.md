# Selected Protection Architecture: Layered Fault Resilience for ML-KEM

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Implementation:** `experiments/phase7/phase7_layered_resilience.c`

---

## 1. Overview of the Layered Architecture

To achieve defense-in-depth against both environmental SEUs and adversarial fault injection without the punitive +100% latency penalty of full duplicate decapsulation, we designed a **4-Layer Fault-Resilience Architecture**:

```text
              +------------------------------------------+
              |    Incoming Ciphertext ct + sk Buffer    |
              +------------------------------------------+
                                   |
    [LAYER 1]                      v
    Pre-Invocation    +--------------------------+  Mismatch (Bit-flip)
    Input Integrity   |   Compute CRC32(ct)      | ---------------------> [FATAL: Reject & Alert]
                      +--------------------------+
                                   | Match
                                   v
    [LAYER 2]         +--------------------------+  Sum / Weight Mismatch
    Arithmetic        |   ML-KEM-768 Decaps      | ---------------------> [Trigger Layer 4 Retry]
    Transform Guard   |   - Dual NTT Invariants  |
                      |   - Butterfly Stage Check|
                      +--------------------------+
                                   |
                                   v
    [LAYER 3]         +--------------------------+  Inconsistent Rails
    Compiled Multi-   |   Multi-Rail FO Gate     | ---------------------> [FATAL: Reject & Alert]
    Rail Barrier      |   (__asm__ volatile)     |
                      +--------------------------+
                                   | Both Rails Match OK
                                   v
    [LAYER 4]         +--------------------------+  Transient Single Glitch
    Controlled        |   Decapsulation Result   | ---------------------> [1-Shot Transient Retry]
    Session Recovery  |   (Explicit Status Code) |
                      +--------------------------+
                                   | Clean Success
                                   v
                      +--------------------------+
                      | Established Shared Key K |
                      +--------------------------+
```

---

## 2. Detailed Layer Specifications

### Layer 1: Pre-Invocation Input Integrity (CRC32-IEEE)
- **Purpose:** Detects transient memory bit-flips in $ct$ (1088 bytes) or $sk$ (2400 bytes) stored in SRAM buffers *before* cryptographic operations begin.
- **Mechanism:** Evaluates standard 32-bit CRC (polynomial `0xEDB88320`) over the ciphertext payload:
  $$\text{CRC32}(ct) = \text{CRC32}(ct_0, \dots, ct_{1087})$$
- **Properties:** Detects 100% of single-bit flips, odd bit errors, and burst errors up to 32 bits.
- **Latency Cost:** ~1.2 µs on Apple Silicon AArch64 (<2.8% of baseline decapsulation).
- **Advantage Over DMR:** Solves the primary common-mode blind spot of duplicate execution, which blindly accepts corrupted inputs.

### Layer 2: Complementary NTT Invariant Protection
- **Purpose:** Detects intermediate arithmetic glitches, MAC failures, and twiddle table bit-flips inside polynomial transformations.
- **Mechanism:** Evaluates dual algebraic projections:
  1. *Unweighted Parity Invariant:*
     $$\sum_{i=0}^{127} \hat{p}_{2i} \equiv 128 \cdot p_0 \pmod q, \quad \sum_{i=0}^{127} \hat{p}_{2i+1} \equiv 128 \cdot p_1 \pmod q$$
  2. *Weighted Inverse-Zeta Invariant:*
     $$\sum_{i=0}^{127} \zeta_{2i+1}^{-1} \cdot \hat{p}_{2i} \equiv 128 \cdot p_2 \pmod q, \quad \sum_{i=0}^{127} \zeta_{2i+1}^{-1} \cdot \hat{p}_{2i+1} \equiv 128 \cdot p_3 \pmod q$$
- **Properties:** Completely closes the Universal Parity Cancellation loophole at Layer 7 ($m=7$) while maintaining 100% detection of asymmetric output register perturbations.

### Layer 3: Redundant Multi-Rail Decision Gate with Compiler Barriers
- **Purpose:** Protects the Fujisaki-Okamoto (FO) transform verification and decision logic from single-instruction bypasses and compiler optimization collapse.
- **Mechanism:** Dual status rails initialized with complementary tokens separated by Hamming distance 32:
  $$\text{Rail}_1 = \texttt{0x5A5AA5A5}, \quad \text{Rail}_2 = \sim\text{Rail}_1 = \texttt{0xA5A55A5A}$$
- **Compiler Optimization Barrier:**
  ```c
  __asm__ volatile("" : "+r"(rail1), "+r"(rail2) : : "memory");
  uint32_t pass1 = (rail1 == RESILIENCE_OK_TOKEN);
  uint32_t pass2 = (rail2 == ~RESILIENCE_OK_TOKEN);
  __asm__ volatile("" : "+r"(pass1), "+r"(pass2) : : "memory");
  return (pass1 & pass2) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
  ```
- **Properties:** Forces the compiler to emit independent compare instructions (`cmp w0, ...; cset w8, eq; cmp w1, ...; cset w9, eq; and w0, w8, w9`), preventing the single condition flag collapse documented in Phase 6B.

### Layer 4: Explicit Status Reporting & Controlled Transient Retry
- **Purpose:** Prevents silent cryptographic failure and session desynchronization while maintaining system availability under radiation bursts.
- **Mechanism:**
  1. Distinguishes transient SEU from persistent corruption.
  2. If Layer 2 or Layer 3 reports an anomaly on an otherwise valid ciphertext, a single controlled retry is executed after clearing CPU pipeline state.
  3. If retry passes, the session key is safely accepted (`RESILIENCE_RETRY_TOKEN`).
  4. If retry fails, an explicit fault status is propagated to the spacecraft protocol (`RESILIENCE_FAULT_TOKEN`), aborting the handshake cleanly.
