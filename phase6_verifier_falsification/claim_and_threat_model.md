# Phase 6: Threat Model and Independent Falsification Claims

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Target:** ML-KEM-768 (FIPS 203) Implementation  
**Artifact:** `phase6_verifier_falsification/claim_and_threat_model.md`

---

## 1. Primary Research Question & Formal Hypotheses

The central objective of Phase 6 is to independently test whether the ML-KEM-768 native butterfly recovery verifier can falsely declare successful recovery when its snapshot inputs or monitor state are corrupted, and whether such a false declaration can lead to end-to-end compromise.

To prevent confusion between component-level monitor failures and system-level cryptographic failures, we strictly separate the investigation into two distinct, independently testable hypotheses:

### Hypothesis 1 (H1: Component-Level Recovery-Verifier Blindness)
> **H1 Formulation:** Corrupting saved operands or recovery snapshots can cause the internal NTT/iNTT butterfly monitor to report successful recovery (`recovered_count > 0`, `persistent_count == 0`), even though the recomputed butterfly state differs from the correct fault-free computation ($u_{\text{retry}} \neq u_{\text{ref}} \lor v_{\text{retry}} \neq v_{\text{ref}}$).

### Hypothesis 2 (H2: End-to-End Silent Data Corruption)
> **H2 Formulation:** A false internal recovery report caused by snapshot or recovery-verifier corruption can cause an incorrect ML-KEM shared secret to be accepted as valid by the complete decapsulation procedure (`status == MLK_DECAPS_STATUS_SUCCESS` and $ss_{\text{out}} \neq ss_{\text{expected}}$).

### Independent Audit Rule
Evidence supporting H1 must NEVER be conflated with evidence supporting H2. H1 evaluates the local arithmetic invariant monitor; H2 evaluates the outer protocol defense (specifically the Fujisaki-Okamoto re-encryption transform and ciphertext comparator).

---

## 2. Threat Model & Physical Attacker Capabilities

We consider an adversary with physical or microarchitectural fault injection capabilities (e.g., focused laser fault injection, clock glitching, electromagnetic fault injection (EMFI), or cosmic ray / SEU disturbances in space-borne electronics).

### 2.1 Adversarial Capabilities
1. **Targeted Register Glitch:** The adversary can flip one or more bits in CPU general-purpose registers holding butterfly operands ($u, v$), intermediate products ($t$), or local snapshot copies ($u_{\text{saved}}, v_{\text{saved}}$).
2. **SRAM / Stack Memory Corruption:** The adversary can perturb values spilled onto the C call stack between operand capture and monitor verification.
3. **Monitor State Corruption:** The adversary can corrupt peripheral registers or memory variables representing monitor state (`persistent_count`, `allow_retry`, `mode`).
4. **Verifier Predicate / Control-Flow Glitch:** The adversary can skip or force branch instructions evaluating the verifier equations (`diff_retry == 0 && sum_retry == 0`).
5. **Mitigation State Corruption:** When countermeasures (such as DSPC) are deployed, the adversary can inject faults targeting the checksum token or the validation comparison.

### 2.2 Attack Constraints (No Artificial Wrapper Injections)
- The attacker cannot rewrite the compiled C source code at runtime.
- The attacker cannot arbitrarily set cryptographic return buffers in the test wrapper.
- All observed consequences must arise from genuine execution of the compiled ML-KEM cryptographic pipeline.

---

## 3. Cryptographic State Machine and Boundary Transitions

```
               [ Input Ciphertext ct, Secret Key sk ]
                                 │
                                 ▼
                     [ Inverse NTT in poly.c ]
                                 │
                   (Capture Snapshot: u_saved, v_saved)
                                 │
                   [ Butterfly Execution: r_j, r_j_len ]
                                 │
                  (Glitch / Fault Injection Window)
                                 │
                                 ▼
                   [ native_ntt_monitor_butterfly ]
                                 │
              ┌──────────────────┴──────────────────┐
        [Clean Pass]                          [Mismatch]
              │                                     │
              │                             (Rollback: *r_j = u_saved)
              │                                     │
              │                             [Recompute: u_new, v_new]
              │                                     │
              │                             [Recovery Verifier]
              │                                     │
              │                      ┌──────────────┴──────────────┐
              │                [Verifier PASS]               [Verifier FAIL]
              │                      │                             │
              │              (recovered_count++)            (persistent_count++)
              │                      │                             │
              │                      └──────────────┬──────────────┘
              ▼                                     ▼
        [Decryption Output]                   [Fail-Stop Gating in kem.c]
         (Message m')                         if (persistent_count > 0)
              │                                     fail = 0xFF;
              ▼                                     │
     [FO Re-encryption: c' = Enc(pk, m')]           ▼
              │                               [Dual-Rail Compare: ct vs c']
              └─────────────────────────────────────┬───────────────────────┘
                                                    │
                                      ┌─────────────┴─────────────┐
                               [fail == 0]                   [fail != 0]
                                      │                             │
                                      ▼                             ▼
                            [Output True Key kr]          [Output Rejection Key Krej]
                            (Status: SUCCESS)             (Status: REJECT or FAULT)
```

---

## 4. Failure Mode Definitions

| Failure Mode | Monitor Behavior | Decapsulation Behavior | Cryptographic Consequence |
|---|---|---|---|
| **Clean Execution** | `mismatches == 0` | `status == SUCCESS`, $ss == ss_{\text{expected}}$ | Pristine nominal operation. |
| **Genuine Recovery** | `recovered_count > 0` | `status == SUCCESS`, $ss == ss_{\text{expected}}$ | Transient fault cleanly corrected. |
| **Safe Monitor Abort** | `persistent_count > 0` | `status == FAULT`, $ss == ss_{\text{rejection}}$ | Persistent fault safely terminated fail-stop. |
| **Internal False Recovery (H1)** | `recovered_count > 0`, $u_{\text{retry}} \neq u_{\text{ref}}$ | Internal monitor falsely certifies corrupt state. | Component-level monitor blind to fault. |
| **Downstream FO Rejection** | Internal monitor deceived | `status == REJECT`, $ss == ss_{\text{rejection}}$ | Protocol outer barrier prevents compromise. |
| **Silent Data Corruption (H2)**| Internal monitor deceived | `status == SUCCESS`, $ss \neq ss_{\text{expected}}$ | **Catastrophic Failure**: Corrupted key accepted. |
