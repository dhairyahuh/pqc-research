# Smallest Defensible Claim and Pre-Submission Experimental Roadmap

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Evidentiary Synthesis, Minimal Defensible Claim, and Required Pre-Submission Experiments  

---

## 1. The Smallest Defensible Research Claim

Following rigorous source inspection, disassembly verification, bit-for-bit rebuild verification, and 400 corrected production-object trials, the smallest defensible research claim that survives this audit is:

> *"In fault-resilient ML-KEM implementations, recovery verifiers that rely on in-place saved operand snapshots are algorithmically susceptible to verifier blindness under snapshot corruption, as demonstrated in software models matching the production arithmetic. However, in ML-KEM-768 decapsulation, this internal blindness does not cause Silent Data Corruption at the API boundary, because the outer Fujisaki-Okamoto re-encryption loop unconditionally enforces safe implicit rejection on invalid ciphertexts. On authentic compiled production objects, independent recomputation of intermediate butterfly products autonomously recovers 100% of transient arithmetic faults and safely rejects 100% of persistent hardware faults."*

---

## 2. Experimental Roadmap: What Must Be Done Before Submission

To transition this research from a rigorous software audit to a premier academic publication (e.g., CHES, IEEE S&P, USENIX Security), the research team must execute the following four experimental campaigns:

### Campaign 1: Physical EMFI/LFI Fault Injection on Target Hardware
- **Current Limitation:** All fault injection to date has been software-simulated via C function calls.
- **Experimental Objective:** Deploy the compiled ML-KEM-768 firmware onto an ARM Cortex-M4 (e.g., STM32F405) or RISC-V target board. Using a localized electromagnetic pulse (EMFI) or near-infrared pulsed laser (LFI), attempt to perturb the register holding `u_saved` during the forward NTT butterfly without causing an immediate hardware fault exception or core lockup.
- **Deliverable:** Empirical fault sensitivity map and physical verification of whether in-place snapshot corruption is achievable on physical silicon.

### Campaign 2: Evaluation on Non-FO Primitives
- **Current Limitation:** The finding that Silent Data Corruption is absent ($H_2 = 0.0\%$) depends entirely on the outer Fujisaki-Okamoto re-encryption check in ML-KEM decapsulation.
- **Experimental Objective:** Evaluate recovery-verifier blindness on cryptographic operations that **lack** an FO re-encryption loop:
  1. **ML-KEM Key Generation:** Does internal false recovery in $\mathbf{A} \mathbf{s} + \mathbf{e}$ produce a weakened or backdoored public key?
  2. **ML-KEM Encapsulation:** Does internal false recovery alter ciphertext coordinates to leak secret keys?
  3. **ML-DSA-65 (FIPS 204) Signature Generation:** Does internal false recovery in polynomial multiplication produce an invalid signature that leaks private key bits via nonce-fault analysis?
- **Deliverable:** End-to-end vulnerability demonstration where internal false recovery leads directly to private key extraction.

### Campaign 3: In-Tree Native Hook Integration
- **Current Limitation:** Snapshot corruption (Targets F1, F2, F9) required reimplementing `native_ntt_monitor_butterfly` in test harnesses because `algorithms/source_ref/mlkem_fault_hooks.c` passes `u_saved` by value on the stack.
- **Experimental Objective:** Formally integrate snapshot perturbation hooks into `algorithms/source_ref/` and rebuild `mlkem_fault_hooks.o`. Re-run the full 1,200-trial suite against unified production objects.
- **Deliverable:** Elimination of all harness reimplementations from the repository.

### Campaign 4: Microarchitectural Side-Channel & Timing Leakage (DUDCT)
- **Current Limitation:** Constant-time behavior was evaluated solely by inspecting the branchless AArch64 disassembly loop (`fea4-fed4`).
- **Experimental Objective:** Execute a formal Dude, is my code constant time? (DUDCT) evaluation across 1,000,000 decapsulations on target hardware. Measure whether the latency of autonomous rollback retry introduces observable timing or power variations that correlate with secret key data.
- **Deliverable:** Statistical proof ($t < 4.5$) of side-channel invariance under autonomous fault recovery.
