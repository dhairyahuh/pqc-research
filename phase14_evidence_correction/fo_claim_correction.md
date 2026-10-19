# Correction of Fujisaki-Okamoto and Implicit-Rejection Claims

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Epistemological and Physical Claim Boundary Correction for Outer FO Transform  
**Target Code:** `kem.c` (ML-KEM-768 Decapsulation re-encryption and comparison loop)  

---

## 1. Executive Summary

Previous research drafts in this repository utilized hyperbolic language when describing the protective capability of the outer Fujisaki-Okamoto (FO) transform and implicit rejection. Phrases such as **"unconditionally enforces,"** **"impenetrable cryptographic firewall,"** and **"prevents all Silent Data Corruption"** were repeatedly asserted across Phases 8–13.

This audit report enforces strict scientific accuracy by dismantling these overstated claims. We categorize the decapsulation behavior into five distinct epistemological tiers, purge unverified rhetoric, articulate the concrete physical fault attack vectors that bypass FO comparison, and withdraw unsubstantiated side-channel claims.

---

## 2. Epistemological Disaggregation of Decapsulation Resilience

To prevent conflating theoretical protocol properties with physical silicon behavior, claims regarding ML-KEM decapsulation resilience are formally disaggregated into five distinct tiers:

```
+-------------------------------------------------------------------------+
| Tier 1: FIPS 203 Algorithmic Specification (Mathematical Abstract Model)|
| - If c' != c, the output is defined as K_bar = J(z || c).               |
| - Pure mathematical mapping; assumes perfect, incorruptible execution. |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 2: Source-Code Implementation (C99 Representation in kem.c)         |
| - Evaluates mlk_ct_memcmp(c, c_prime, 1088).                           |
| - Selects K_valid vs K_rej using constant-time bitwise mask selection.  |
| - Code logic is susceptible to compiler transformation and optimization.|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 3: Observed Behavior Under Tested Software Fault Models            |
| - Inverted intermediate butterfly operands (F1, F2, F4, F5A, F5B, etc.) |
| - 100% of corrupt butterfly states produced c' != c.                   |
| - Zero SDC observed across tested software injection loci (0/400 prod). |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 4: Untested Physical / Instruction-Level Fault Hypotheses           |
| - Laser Fault Injection (LFI), Clock Glitching, Voltage Transients.     |
| - Instruction skipping on mlk_ct_memcmp or cmov.                        |
| - Pointer manipulation: forcing c_prime pointer to point to c.          |
| - NOT evaluated by software hooks; FO offers ZERO protection if skipped.|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Tier 5: Microarchitectural Side-Channel & Constant-Time Claims          |
| - No TVLA, dudect, or power/EM trace leakage evaluations executed.      |
| - Source-level bitwise masking does not guarantee machine code CT.      |
| - All constant-time security certifications are WITHDRAWN.              |
+-------------------------------------------------------------------------+
```

---

## 3. Retracted Language and Claim Purge Matrix

The following table records specific phrases that must be purged from all academic deliverables, alongside their empirical corrections:

| Location / Document | Overstated Phrase / Claim | Flaw / Fallacy | Mandatory Corrected Language |
| :--- | :--- | :--- | :--- |
| Phase 8–13 Summaries | "The outer FO transform unconditionally enforces absence of SDC." | The FO transform is executed as software instructions on a processor. Physical faults can skip instructions, alter branch conditions, or force registers to zero. No software routine can "unconditionally" guarantee anything against hardware faults. | "Under the tested software fault models targeting the internal NTT stages, the outer FO re-encryption transform consistently detected corrupted intermediate states and prevented incorrect shared secrets from being accepted." |
| Abstract & Verdicts | "Acts as an impenetrable cryptographic firewall against fault injection." | Metaphorical, unscientific hyperbole. The FO check does not prevent faults; it merely compares re-encrypted ciphertexts. If an adversary glitches the comparison loop, the "firewall" collapses completely. | "Provides secondary algorithmic validation by comparing re-encrypted ciphertext before key release." |
| Traceability Matrices | "Prevents all SDC ($H_2 = 0.0\%$ guaranteed)." | Empirical sample size ($N=400$ production trials) cannot prove universal impossibility ($H_2 = 0$ for all possible attacks). Bounded strictly by 95% Wilson confidence interval $[0.0\%, 0.95\%]$. | "Yielded zero observed SDC events across 400 production trials (95% CI: $[0.0\%, 0.95\%]$)." |
| Resilience Claims | "Certified constant-time implementation guarantees physical side-channel immunity." | No physical side-channel evaluation was conducted. Compiler optimizations (e.g., LLVM backend peephole passes) can introduce timing variations into source-level constant-time C. | "Source code utilizes branch-free bitwise operations; empirical microarchitectural timing and power side-channel leakage remain unverified and subject to future evaluation." |

---

## 4. Plausible Untested Attack Vectors Bypassing FO Protection

The claim that the FO transform renders physical fault protection unnecessary is fundamentally false. The following physical fault attack hypotheses would completely bypass FO protection:

1. **Instruction Skip on `mlk_ct_memcmp` Call:**
   A single-cycle clock glitch or targeted EMFI pulse targeting the `BL mlk_ct_memcmp` branch instruction causes the CPU to treat the call as a `NOP`. The return register `x0` retains its prior zero value (`fail = 0`), causing unconditional key acceptance regardless of ciphertext corruption.
2. **Ciphertext Pointer Corruption (`c_prime = c`):**
   A laser fault injected into the stack frame register containing the pointer to `c_prime` flips bits to alias `c_prime` with the received ciphertext buffer `c`. The comparison routine executes `memcmp(c, c, 1088)`, which evaluates to identical ($0$), releasing the invalid key.
3. **Condition Flag Glitching in `cmov`:**
   Corrupting the mask generation `mask = (uint32_t)(-(int32_t)(fail == 0))` such that `mask` is forced to `0xFFFFFFFF` even when `fail != 0`.
4. **Targeted Perturbation of the Decapsulation API Status:**
   Glitching the fail-stop handler `*internal_status = 0xFFFFFFFF` to write `0x5A5A5A5A`, tricking the caller into treating a fallback buffer as an authentic valid session key.

---

## 5. What the Experiments Demonstrate vs. What Remains Unknown

### 5.1 What Is Conclusively Demonstrated:
1. In the tested software implementation, corrupting NTT butterfly operands during decapsulation reliably causes the reconstructed ciphertext $c'$ to diverge from $c$ across all evaluated algebraic fault models.
2. When the CPU faithfully executes `mlk_ct_memcmp` and `mlk_ct_cmov_zero`, the divergence between $c'$ and $c$ triggers selection of the implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
3. The implicit rejection derivation in `kem.c` conforms bit-for-bit with FIPS 203 Section 7.3 ($K = \text{J}(z \parallel c)$), verified against an independent clean-room oracle across 100 invalid ciphertext mutations.

### 5.2 What Remains Unknown / Unverified:
1. **Behavior Under Physical Fault Injection:** Whether electromagnetic fault injection (EMFI), body-bias injection (BBI), or optical laser fault injection (LFI) can bypass the FO comparison loop in hardware.
2. **Microarchitectural Side-Channel Security:** Whether cache bank conflicts, branch prediction artifacts, or memory bus latency introduce secret-dependent timing leakage during decapsulation or retry loops.
3. **Multi-Fault Co-Location:** Whether concurrent faults simultaneously targeting the internal NTT butterfly and the FO comparison predicate can induce controlled key leakage.
