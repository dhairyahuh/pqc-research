# Corrected Categorical Outcome Definitions and Predicates

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Rigorous Formalization of Mutually Exclusive Trial Outcomes  

---

## 1. Formal Categorical Definitions & Exact Predicates

To prevent category inflation or circular classification, every trial outcome is assigned to exactly one of the following mutually exclusive categories:

### 1. `CLEAN_SUCCESS`
- **Definition:** The execution was uncorrupted (no fault armed or executed), all 5,376 butterflies completed without invariant violations, and decapsulation returned the authentic shared secret.
- **Exact Predicate:**
  $$\text{trigger\_count} = 0 \land \text{mismatch\_count} = 0 \land \text{status} = \text{0x5A5A5A5A} \land K_{\text{out}} = K_{\text{expected}}$$
- **Rule:** A clean execution must **never** be counted as a recovery.

### 2. `GENUINE_RECOVERY`
- **Definition:** A fault was actively injected into the cryptographic pipeline, detected by the invariant monitor, successfully recovered via in-place rollback and recomputation, verified by the recovery verifier, and the decapsulation procedure completed with status `0x5A5A5A5A`, returning the genuine shared secret identical to encapsulation.
- **Exact Predicate:**
  $$\text{trigger\_count} \ge 1 \land \text{mismatch\_count} \ge 1 \land \text{recovered\_count} \ge 1 \land \text{persistent\_count} = 0 \land \text{status} = \text{0x5A5A5A5A} \land K_{\text{out}} = K_{\text{expected}}$$

### 3. `SAFE_FAIL_STOP`
- **Definition:** The monitor detected an unrecoverable or persistent fault, incremented `persistent_count`, and the decapsulation routine safely terminated with status `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`), returning the canonical implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$.
- **Exact Predicate:**
  $$\text{persistent\_count} > 0 \land \text{status} = \text{0xFFFFFFFF} \land K_{\text{out}} = K_{\text{rej}} \land K_{\text{out}} \ne K_{\text{expected}}$$

### 4. `DOWNSTREAM_FO_REJECTION`
- **Definition:** The internal monitor was blinded or passed, but polynomial error diffusion caused the candidate ciphertext $\mathbf{ct}'$ to diverge from $\mathbf{ct}$. The outer Fujisaki-Okamoto check detected `memcmp(ct, tmp) != 0`, set `fail = 0xFF`, returned status `0xA5A5A5A5` (`MLK_DECAPS_STATUS_REJECT`), and safely returned $K_{\text{rej}}$.
- **Exact Predicate:**
  $$\text{ct}' \ne \text{ct} \land \text{fail} = \text{0xFF} \land \text{status} = \text{0xA5A5A5A5} \land K_{\text{out}} = K_{\text{rej}}$$

### 5. `SDC_ACCEPTED_INCORRECT` (Silent Data Corruption / $H_2$)
- **Definition:** The complete cryptographic decapsulation procedure returned a shared secret $K_{\text{out}}$ that differed from both the genuine secret and the expected rejection key, or accepted an incorrect shared secret under status `0x5A5A5A5A`.
- **Exact Predicate:**
  $$(\text{status} = \text{0x5A5A5A5A} \land K_{\text{out}} \ne K_{\text{expected}}) \lor (K_{\text{out}} \ne K_{\text{expected}} \land K_{\text{out}} \ne K_{\text{rej}})$$

### 6. `FAULT_NOT_TRIGGERED`
- **Definition:** A trial in which a fault was armed, but execution terminated or bypassed the target locus without firing (`trigger_count == 0`).
- **Exact Predicate:**
  $$\text{armed} = 1 \land \text{trigger\_count} = 0$$
- **Rule:** Un-triggered trials must not enter the denominator for fault-handling rates without explicit, separate reporting.

### 7. `INCONCLUSIVE`
- **Definition:** Any execution resulting in an unexpected status code, memory segmentation fault, or inconsistent state where the cryptographic outcome cannot be validated against the formal oracle.
- **Exact Predicate:**
  $$\text{Any trial not satisfying Predicates 1 through 6}$$

---

## 2. Denominators and Rate Calculation Rules

1. **Trigger Rate Denominator:** Total planned trials ($N=100$).
2. **Autonomous Recovery Rate Denominator:** Total verified injected trials (`trigger_count >= 1`).
3. **Fail-Stop Rejection Rate Denominator:** Total verified persistent/unrecoverable injected trials.
4. **$H_1$ Rate Denominator:** Total injected trials where recovery verifier was evaluated.
5. **$H_2$ Rate Denominator:** Total executed trials ($N=1,200$ across all tested fault models).
