# Phase 7I: Adversarial Fault Injection Methodology

## 1. Threat Model & Injection Taxonomy

To rigorously evaluate end-to-end decapsulation resilience across both Forward NTT (Cooley-Tukey) and Inverse NTT (Gentleman-Sande) transforms, Phase 7I expands the adversarial threat model to **14 distinct fault classes** covering 1,400 independent trials (100 trials per class).

The threat taxonomy spans:
1. **Arithmetic Transform Faults (Forward & Inverse)**: Target intermediate registers, multipliers, adders, and output registers.
2. **Algebraic Parameter Corruption**: Target twiddle factors ($\zeta$).
3. **Correlated/Symmetric Invariant Evasion**: Target mathematical blind spots where perturbations cancel in single-rail checks.
4. **Pre-Transform & Systemic Attacks**: Target ciphertext inputs prior to NTT.
5. **Persistent Faults**: Single-event latchups (SEL) or stuck-at bits exceeding retry limits.
6. **Control-Flow & Comparator Faults**: Target Fujisaki-Okamoto re-encryption validation flags.
7. **Negative Controls**: Baseline uncorrupted execution to prove zero false-alarm rate.

---

## 2. Specification of the 14 Fault Classes

| Class ID | Threat Description | Injection Locus | Injected Perturbation Model | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **C01** | Forward Intermediate $t$ | Cooley-Tukey intermediate $t$ | Transient single-bit flip $(\oplus 0x0001)$ | Autonomous Recovery |
| **C02** | Forward Twiddle Factor $\zeta$ | Cooley-Tukey twiddle factor table | Transient bit corruption $(\oplus 0x0004)$ | Safe Reject / Benign |
| **C03** | Forward Output Register | Forward butterfly output register | Transient bit flip $(\oplus 0x0002)$ | Autonomous Recovery |
| **C04** | Inverse Intermediate Diff $d$ | Gentleman-Sande difference $(v - u)$ | Transient single-bit flip $(\oplus 0x0001)$ | Autonomous Recovery |
| **C05** | Inverse Twiddle Factor $\zeta$ | Gentleman-Sande twiddle factor | Transient bit corruption $(\oplus 0x0004)$ | Safe Reject / Benign |
| **C06** | Inverse Adder Output $u'$ | Gentleman-Sande $u' = \text{barrett}(u + v)$ | Transient single-bit flip $(\oplus 0x0001)$ | Autonomous Recovery |
| **C07** | Inverse Multiplier Output $v'$ | Gentleman-Sande $v' = \text{fqmul}(d, \zeta)$| Transient single-bit flip $(\oplus 0x0002)$ | Autonomous Recovery |
| **C08** | Inverse Symmetric Perturbation | Add equal $\Delta = +17$ to $u'$ and $v'$ | Correlated multi-register offset | Autonomous Recovery |
| **C09** | Inverse Anti-Symmetric Perturb. | Add $+\Delta$ to $u'$ and $-\Delta$ to $v'$ | Dual-rail cancellation probe | Autonomous Recovery |
| **C10** | Pre-NTT Input Corruption | Ciphertext polynomial $c$ | Single-byte flip prior to NTT | Safe Rejection |
| **C11** | Persistent Stuck-at (Forward) | Forward butterfly multiplier | Stuck-at bit $(\text{retry} \to \text{failure})$ | Safe Rejection |
| **C12** | Persistent Stuck-at (Inverse) | Inverse butterfly difference | Stuck-at bit $(\text{retry} \to \text{failure})$ | Safe Rejection |
| **C13** | FO Decision Gate Perturbation | FO equality flag `fail` | Perturb compare flag during verification | Safe Rejection |
| **C14** | Uncorrupted Negative Control | None (Clean execution) | None (0 faults injected) | Benign (Authentic Key)|

---

## 3. Outcome Classification Definitions

Every execution trial is classified into exactly one of four rigorous, mutually exclusive categories based on the decapsulated shared secret $K$:

1. **RECOVERED ($R_{\text{rec}}$)**:
   - The native monitor detected an invariant violation, successfully rolled back register state from local shadow registers, retried the butterfly operation, and completed decapsulation.
   - The emitted shared secret exactly equals the golden reference key: $K == K_{\text{valid}}$.
2. **SAFE_REJECT ($R_{\text{rej}}$)**:
   - The system encountered an unrecoverable fault (persistent fault, ciphertext tampering, or unmonitored twiddle corruption) and safely triggered the implicit rejection contract.
   - The emitted shared secret equals the deterministic rejection key: $K == K_{\text{rej}}$. No private key material is exposed.
3. **BENIGN_EQUIV ($R_{\text{ben}}$)**:
   - The injected fault was algebraically annihilated (e.g. modular equivalent reduction, unselected polynomial branch, or negative control baseline).
   - Emitted key equals $K_{\text{valid}}$ without triggering monitor retry.
4. **UNDETECTED_CORRUPT ($R_{\text{und}}$)**:
   - **CRITICAL FAILURE**: The system produced an unauthenticated, corrupted key ($K \neq K_{\text{valid}} \wedge K \neq K_{\text{rej}}$) without triggering safe rejection.
   - Any non-zero count of $R_{\text{und}}$ constitutes a failure of the fault resilience architecture.

---

## 4. Deterministic Execution and Traceability

- **Seed Determinism**: Each trial seeds pseudorandom generation using $\text{seed} = (\text{class\_idx} \times 1000) + \text{trial\_idx}$, ensuring complete reproducibility.
- **Trial Logging**: Every individual trial outputs a JSON record containing `trial_id`, `fault_class`, `stage`, `butterfly`, `status`, `recovered`, `mismatches`, and `outcome` to `results/phase7i/raw/phase7i_e2e_trials.json`.
