# Corrected Research Claims and Contribution Boundaries

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Rigorous Reassessment of Research Contributions and Claim Boundaries  

---

## 1. Executive Summary

Scientific integrity requires distinguishing between **an architectural vulnerability demonstrated in an abstract software model** and **an exploitable vulnerability in compiled production software**. 

Previous project drafts conflated simulated memory corruption in standalone C testbeds with production security flaws, claiming that ML-KEM-768 implementations possess general vulnerability to recovery-verifier blindness while simultaneously claiming unconditional fault tolerance via Fujisaki-Okamoto re-encryption.

This document formally recalibrates the research contribution, articulates the four critical distinctions mandated by rigorous cryptographic engineering, establishes the strongest defensible research question, and marks academic novelty as unresolved pending a comprehensive literature audit.

---

## 2. Four Mandatory Distinctions

To prevent academic overstatement or misrepresentation, the findings of this study are partitioned into four distinct categories:

### 2.1 An Architectural Design Pitfall Demonstrated in a Software Model
- **Finding:** Checkpoint-and-verify recovery mechanisms that snapshot intermediate state in shared or in-place memory exhibit **circular verifier blindness** ($H_1$).
- **Evidence:** Demonstrated across 600 harness simulation trials (Targets F1, F2, F6, F7, F9, F10). When snapshot variables or parity state registers are corrupted, the internal verifier approves corrupt butterfly computations (observed in 94% to 100% of trials across vulnerable configurations) because it checks the computation against its own corrupted baseline.
- **Scope:** This is an **architectural cautionary design result**. It demonstrates that naive local rollback/recovery patterns—frequently borrowed from fault-tolerant embedded computing—fail silently in cryptographic contexts unless the snapshot itself is cryptographically authenticated or isolated.

### 2.2 A Weakness in the Specific Implementation Tested
- **Finding:** The native monitored decapsulation prototype (`mlkem768_dec_monitored`) relies on single-rail state variables in internal C functions and passes diagnostic pointers across subroutine boundaries.
- **Evidence:** If compiled without aggressive inlining or stack canary protection, memory pointers to recovery telemetry could theoretically be corrupted.
- **Scope:** This is an implementation artifact of the instrumented prototype, not an inherent flaw in the mathematical specification of ML-KEM.

### 2.3 A Demonstrated Production Vulnerability
- **Finding:** **NO production vulnerability was demonstrated.**
- **Evidence:** In the compiled production objects (`mlkem768_inst.o` + `mlkem_fault_hooks.o`), the implementation exhibited **zero** Silent Data Corruption events ($0/400$, 95% CI: $[0.0\%, 0.95\%]$). Under transient butterfly faults (F4), the native monitor achieved 100% genuine recovery ($100/100$). Under recurring and software force-value faults (F5A, F5B), the native monitor safely failed-stop ($200/200$), returning the FIPS 203 implicit rejection key $K_{\text{rej}} = \text{J}(z \parallel c)$.
- **Scope:** The study did **not** find any attack vector that allows an external attacker to extract private keys or decrypt ciphertexts against the compiled production implementation under the tested fault models.

### 2.4 A General Cryptographic Security Claim
- **Finding:** Overstated claims asserting that ML-KEM possesses "general physical fault resilience," "radiation hardening," or "unconditional absence of SDC" are **scientifically invalid and WITHDRAWN**.
- **Evidence:** Software-level hook injection cannot evaluate physical silicon effects (e.g., clock glitching, optical laser fault injection, electromagnetic pulse, power rail droop). Software re-encryption comparison loops can be bypassed by physical instruction skipping.

---

## 3. Prior Art and Academic Novelty Status

A preliminary literature matrix was compiled in [`results/literature_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/literature_matrix.csv). However:
1. No systematic, peer-reviewed comparative prior-art analysis has been published evaluating whether circular verifier blindness in checkpointed NTT butterflies has been previously documented in hardware fault-tolerance literature (e.g., in AES/RSA fault detection literature or prior lattice-based fault injection studies such as Ravi et al., CHES 2020; Delvaux, 2022).
2. Consequently, claiming absolute novelty for the discovery of recovery-verifier blindness is premature.
3. **Formal Academic Stance:** **Novelty is marked as UNRESOLVED**, pending a systematic, documented prior-art literature review comparing this mechanism against published fault-detection countermeasures.

---

## 4. The Strongest Defensible Research Question

To maximize academic rigor and impact, the paper must abandon claims of general physical security and focus squarely on the demonstrated architectural trade-off.

### 4.1 Recommended Research Question:
> **"In lattice-based key encapsulation mechanisms (ML-KEM-768), does local checkpoint-and-verify arithmetic recovery introduce circular verifier blindness under internal memory corruption, and does outer Fujisaki-Okamoto re-encryption reliably suppress resulting end-to-end silent data corruption under software fault models?"**

### 4.2 Supporting Sub-Questions:
1. **$RQ_1$ (Local Verifier Integrity):** Under what fault semantics does an internal NTT recovery verifier approve corrupted computational state when evaluating against in-place snapshots?
2. **$RQ_2$ (End-to-End Cryptographic Containment):** Under software-modeled transient and recurring faults, does outer Fujisaki-Okamoto re-encryption consistently prevent corrupt butterfly computations from producing accepted invalid shared secrets?
3. **$RQ_3$ (Overhead and Safe Abort):** What is the latency overhead and fail-stop reliability of dual-rail monitored NTT execution relative to clean baseline ML-KEM decapsulation?

This framing is defensible, mathematically precise, directly supported by raw trial evidence, and avoids any unverified claims of physical hardware immunity.
