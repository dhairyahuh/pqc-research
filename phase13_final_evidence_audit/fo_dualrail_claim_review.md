# Comprehensive Review of Fujisaki-Okamoto & Dual-Rail Claims

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** FO Re-encryption & Verification Implementation in `algorithms/source_ref/mlkem/src/kem.c`  
**Standard:** NIST FIPS 203 Section 7.3 (ML-KEM Decapsulation)  

---

## 1. Separation of Implementation, Software Tests, and Physical Realities

To maintain scientific integrity, the audit explicitly partitions findings across four epistemological categories:

| Domain | What is Established / Implemented | What is NOT Established / Tested |
| :--- | :--- | :--- |
| **Source Code (`kem.c`)** | - Re-encrypts candidate message via `mlk_indcpa_enc`.<br>- Computes constant-time forward comparison `mlk_ct_memcmp`.<br>- Computes independent reverse accumulation `fail_chk`.<br>- Checks persistent monitor counter.<br>- Computes rejection key $K_{\text{bar}} = J(z \parallel ct)$.<br>- Conditionally selects key via `mlk_ct_cmov_zero`. | - No guarantee against compiler-induced early-exit branches.<br>- No hardware-level sensor checks.<br>- No protection against register-level physical fault injection on CPU flags. |
| **Software Fault Experiments (Phases 5–13)** | - Injected single-bit flips and force-value assignments into intermediate polynomial coefficients during NTT.<br>- Evaluated recovery under transient faults (F4).<br>- Evaluated safe fail-stop under persistent faults (F5A, F5B).<br>- Evaluated rejection key conformance across 100 ciphertext mutations. | - Did NOT inject faults into the FO comparison loop instructions.<br>- Did NOT inject faults into the conditional move multiplexer.<br>- Did NOT inject faults into Keccak hash state registers.<br>- Did NOT test multi-locus concurrent faults (NTT + FO). |
| **Physical Fault Injection (Hardware)** | - None. No EMFI, clock glitching, body-bias, or laser fault injection was performed on physical silicon. | - Physical microcontroller resilience (e.g. ARM Cortex-M4, RISC-V) is completely untested. |
| **Side-Channel & Timing Leakage** | - Source code avoids data-dependent C `if/else` branches on secret keys. | - No cycle-accurate timing measurements executed.<br>- No `dudect` leakage assessment performed.<br>- No DPA/CPA power/EM side-channel analysis conducted. |

---

## 2. Review of Proposed Bypass Hypotheses

The table below classifies the physical and architectural bypass hypotheses:

| Bypass Scenario | Attack Mechanism | Classification | Detailed Technical Analysis |
| :--- | :--- | :---: | :--- |
| **1. Comparison Instruction Skip** | Glitching the program counter at the call to `mlk_ct_memcmp` to skip ciphertext comparison entirely. | **Plausible Untested Hypothesis** | If the comparison call is skipped, `fail` retains its default pre-call value (`0x00`). The implementation would then copy the decrypted faulted key $K'$ over `ss`, causing Silent Data Corruption. |
| **2. Conditional Move Glitch** | Injecting a fault into the CPU register holding `mask` inside `mlk_ct_cmov_zero`. | **Plausible Untested Hypothesis** | `mlk_ct_cmov_zero` relies on `mask = mlk_ct_cmask_zero_u8(fail)`. If a physical fault flips the register to `0xFF`, the faulted key $K'$ is copied unconditionally, bypassing both `fail` and `fail_chk`. |
| **3. Double-Rail Simultaneous Collapse** | Forcing power supply under-voltage to collapse CPU registers holding `fail` and `fail_chk` to zero. | **Plausible Untested Hypothesis** | Dual-rail comparison prevents single-locus predicate bypass ($fail \ne fail\_chk$). However, an attack that zeroes both registers simultaneously satisfies `fail == fail_chk == 0`, defeating the dual-rail check. |
| **4. Secret Message Pointer Redirection** | Faulting pointer registers `tmp` or `buf` during decapsulation cleanup. | **Plausible Untested Hypothesis** | Could lead to uninitialized stack leakage or pointer aliasing. Untested in software. |

---

## 3. Disallowed and Qualified Claims

1. **DISALLOWED: Universal Fault Immunity of the FO Transform:**  
   The claim that the Fujisaki-Okamoto transform unconditionally prevents Silent Data Corruption under all fault attacks is **scientifically invalid**. It prevents SDC only when the fault is confined to the decapsulation arithmetic and the downstream FO comparison execution is physically fault-free.
2. **DISALLOWED: Certified Constant-Time Execution:**  
   The claim that ML-KEM-768 or its native monitor is certified constant-time is **unsupported**. Constant-time claims require cycle-accurate timing measurements on compiled binaries and statistical leakage detection (`dudect`).
3. **QUALIFIED: Single-Locus Dual-Rail Predicate Bypass Protection:**  
   The dual-rail check is retained as a valid structural countermeasure against single-point predicate flips, with the explicit qualification that it does not protect against simultaneous double-rail collapse.
