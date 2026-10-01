# Claim Reconciliation and Scientific Audit Matrix

## 1. Audit Context and Objectives

Phase 7C reported breakthrough claims regarding native ML-KEM fault resilience:
- Claim A: "100.0% fault detection across all 8 threat classes"
- Claim B: "100.0% autonomous recovery from internal faults"
- Claim C: "-44.3% overhead (44% faster than baseline decapsulation)"
- Claim D: "Preserves FIPS 203 constant-time implicit-rejection behavior"
- Claim E: "Complete elimination of external expected_ss runtime oracles"

This document provides a line-by-line reconciliation of these claims against empirical findings, disassembly analysis, and mathematical verification under adversarial testing.

---

## 2. Claim Disposition Matrix

| Claim from Phase 7C | Audit Finding | Verdict | Scientific Reconciliation |
| :--- | :--- | :--- | :--- |
| **Claim A: 100% Detection across 8 Classes** | Class 6 was hardcoded (`d6 = true`). `g_inv_zetas_layer7` had 11 zero elements. Common-mode ALU faults bypass dual-rail. Pre-CRC corruption bypasses CRC32. | **OVERSTATED / PARTIALLY DISPROVEN** | Detection is 100% against single-point transient SEUs tested in the standard harness, but fails against adversarial common-mode, pre-CRC, and correlated ALU faults. Class 6 was not empirically evaluated in 7C. |
| **Claim B: 100% Autonomous Recovery** | Equated fault detection with recovery. Persistent faults (Class 8) and input corruptions (Class 5) fail recovery 100% of the time. | **OVERSTATED** | Recovery is 100% for transient Single-Event Upsets (SEU). For persistent stuck-at faults and input corruptions, recovery rate is **0.0%** (safe rejection is 100.0%). |
| **Claim C: -44.3% Overhead (Faster than Baseline)** | Apple Silicon CPU frequency scaling artifact due to cold-start execution of baseline without warm-up loops. | **DISPROVEN (METHODOLOGICAL ARTIFACT)** | Native in-tree monitoring adds $+0.10\%$ overhead ($72.42\,\mu\text{s} \to 72.49\,\mu\text{s}$) when measured under identical warmed-up P-core conditions. Layered native wrapper adds $+0.40\%$. |
| **Claim D: Constant-Time Implicit Rejection** | Disassembly proves branchless inner execution, but wrapper retry unconditionally fires on `dec_reject`, doubling latency on invalid ciphertexts. | **QUALIFIED / VULNERABLE IN WRAPPER** | Core cryptographic pipeline is branchless and constant-time. However, the Phase 7C wrapper leaked ciphertext validity via a $2\times$ retry latency side-channel on invalid inputs. |
| **Claim E: Oracle-Free Runtime Architecture** | Fully verified in source code and binaries. No `expected_ss` or private test vectors are accessed during execution. | **CONFIRMED & VALIDATED** | True in-tree monitoring achieved. All decisions derive strictly from dual-rail comparisons, CRC32, and NTT parity/weighted checks. |

---

## 3. Detailed Technical Analysis of Reconciled Claims

### Reconciling Claim A: 100% Fault Detection
1. **The Class 6 Artifact:** In `phase7c_oracle_free_harness.c`, Class 6 was hardcoded:
   `d5 = true; tok6 = RESILIENCE_FAULT_TOKEN; d6 = true;`
   In Phase 7D, we replace this with active injection into the rail variables and ALU comparison flags. Under real injection, single-rail flips are 100% detected ($150/150$), but simultaneous symmetric corruption ($rail_1 \oplus \Delta == \sim(rail_2 \oplus \Delta)$) bypasses the barrier.
2. **The 117 vs 128 Element Zeta Table Bug:** The precomputed table in Phase 7B/7C had 11 missing elements defaulting to zero. In Phase 7D, restoring the full 128 elements restores intended mathematical coverage.
3. **Class 5 Pre-Invocation Boundaries:** CRC32 detects 100% of single-bit and burst errors occurring *after* checksum computation. However, an adversary with access to the bus prior to CRC generation or capable of recomputing the CRC achieves 0% detection by design. CRC32 provides integrity, not cryptographic authenticity.

### Reconciling Claim B: Autonomous Recovery vs Safe Rejection
In safety-critical space missions, treating persistent faults as "recovered" is fatal.
- Transient SEU: $R_D = 100\%$, $R_R = 100\%$, $R_S = 0\%$, $R_U = 0\%$.
- Persistent Stuck-At: $R_D = 100\%$, $R_R = 0\%$, $R_S = 100\%$, $R_U = 0\%$.
- Pre-Invocation Input: $R_D = 100\%$, $R_R = 0\%$, $R_S = 100\%$, $R_U = 0\%$.

### Reconciling Claim C: Performance and Overhead
The reported "negative overhead" was an artifact of macOS thread scheduling on Apple Silicon:
- Cold baseline (unwarmed, low clock state): $148.49\,\mu\text{s}$
- Warmed baseline (P-core, steady state): $72.42\,\mu\text{s}$
- Warmed native in-tree monitored (`mlk_kem_dec_monitored`): $72.49\,\mu\text{s}$ ($+0.10\%$)
- Warmed layered native (`decaps_layered_native`): $72.74\,\mu\text{s}$ ($+0.44\%$)
- Full duplicate execution (DMR): $145.22\,\mu\text{s}$ ($+100.5\%$)

Targeted layered resilience achieves $\mathbf{99.5\%}$ latency savings compared to DMR ($+0.44\%$ vs $+100.5\%$).

---

## 4. Readiness Assessment for Publication-Grade Evaluation

### Verdict: **CONDITIONALLY READY WITH CAVEATS**

The layered architecture represents a major, defensible contribution to post-quantum cryptographic engineering, provided the paper makes the following explicit scientific disclaimers:
1. **Never claim 100% universal fault resilience:** Scope detection guarantees strictly to the single-event upset (SEU) and single-instruction transient fault models.
2. **Acknowledge the CRC32 boundary:** Explicitly state that input integrity assumes a trusted hardware CRC engine or authenticated communication wrapper.
3. **Disaggregate recovery metrics:** Report transient recovery ($100\%$) and persistent safe-abort ($100\%$) as separate metrics.
4. **Publish corrected performance numbers:** Report true warmed-up overhead as $+0.10\%$ (in-tree) to $+0.44\%$ (wrapper), disclaiming the previous artifact.
5. **Document the retry timing side-channel:** Publish the finding and explain how decouple-on-reject remediates the vulnerability.
