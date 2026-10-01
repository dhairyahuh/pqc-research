# Phase 7J: Adversarial Fault Campaign Audit & Extended Verification

## 1. Audit of Phase 7I Experimental Dataset

Using the standalone audit tool `experiments/phase7j/audit_phase7i_analysis.py`, the raw trial records from Phase 7I (`results/phase7i/raw/phase7i_e2e_trials.json`, 1,400 records) were systematically verified:
- **Structural Integrity**: Exactly 1,400 contiguous records indexed from 0 to 1,399.
- **Duplicate IDs**: 0 duplicate trial IDs.
- **Missing IDs**: 0 missing trial records.
- **Transient Recovery**: Exactly 700 / 700 (100.0%) recovery on transient arithmetic classes (Wilson 95% CI: $[99.45\%, 100.00\%]$).
- **Undetected Corruptions**: Exactly 0 / 1,400 (0.00%, Wilson 95% CI: $[0.00\%, 0.27\%]$).
- **Audit Metric Output**: Recorded in `results/phase7j/processed/phase7j_audit_metrics.json`.

---

## 2. Extended Phase 7J Campaign (1,600 Empirical Trials)

To stress-test newly identified loci, multi-layer propagation, shadow register corruption, retry exhaustion, and concurrent faults, Phase 7J formulated and executed an **extended 16-class adversarial campaign** ($N = 100$ trials per class, 1,600 trials total).

### Results Breakdown across All 16 Threat Classes

| Class ID | Threat Class Description | Injected Locus / Perturbation | Trials | Recovered | Safe Reject | Benign | Undetected Corrupt | Recovery Rate (95% CI) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **J01** | Multi-Layer Forward Transient | Cooley–Tukey $t$ bit-flip (Layers 1–7) | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J02** | Multi-Layer Inverse Transient | GS intermediate $d$ bit-flip (Layers 1–7) | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J03** | Multi-Bit Forward Arithmetic | 2-bit flip in forward output register | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J04** | Multi-Bit Inverse Arithmetic | 2-bit flip in inverse output register | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J05** | Shadow Register Corruption | Perturbation of saved operand $u_{\text{saved}}$ | 100 | 0 | **100** | 0 | **0** | 0.0% (Safe Fail) |
| **J06** | Checker Recomputation Disturbance | Transient disturbance during diff recompute | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J07** | Twiddle Table Direct Bit-Flip | Corrupt constant twiddle table $\zeta$ | 100 | 0 | **89** | 11 | **0** | 0.0% (FO Caught) |
| **J08** | Modular Reduction Overflow | Additive error $u' > 3329$ | 100 | **99** | 0 | 1 | **0** | 99.0% [94.5, 99.8] |
| **J09** | Rollback / Retry-Path Fault | Secondary fault injected during retry | 100 | 0 | **100** | 0 | **0** | 0.0% (Bound Held) |
| **J10** | Correlated ALU + Checker Fault | Symmetric perturbation $(u'+\Delta, v'+\Delta)$ | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J11** | Concurrent Fwd + Inv Fault | Simultaneous transient in Fwd and Inv NTT | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] |
| **J12** | Persistent Stuck-at (Layer 1 Fwd) | Permanent stuck bit in early forward NTT | 100 | 0 | **100** | 0 | **0** | 0.0% (Safe Reject)|
| **J13** | Persistent Stuck-at (Layer 7 Inv) | Permanent stuck bit in late inverse NTT | 100 | 0 | **100** | 0 | **0** | 0.0% (Safe Reject)|
| **J14** | Public API Decaps (NULL Status) | Persistent fault under `mlkem768_dec(NULL)` | 100 | 0 | **100** | 0 | **0** | 0.0% (Krej Emitted)|
| **J15** | Pre-NTT Ciphertext Tampering | Single-byte flip in ciphertext input | 100 | 0 | **100** | 0 | **0** | 0.0% (FO Reject) |
| **J16** | Uncorrupted Negative Control | Clean decapsulation baseline | 100 | 0 | 0 | **100** | **0** | 100.0% Authentic |
| **Total**| **All 16 Extended Threat Classes** | **Complete Decapsulation Path** | **1600**| **899** | **589** | **112** | **0** | **0.00% Undetected** |

---

## 3. Analysis of Critical Adversarial Scenarios

### 3.1. Shadow Register Corruption (J05)
When the shadow variable holding the saved input operand is corrupted, the monitor triggers an invariant mismatch on the first butterfly calculation because $u' - (u_{\text{saved\_corrupt}} + v_{\text{saved}}) \neq 0$. When rollback restores $(u_{\text{saved\_corrupt}}, v_{\text{saved}})$ and re-executes the butterfly, the retry verification recomputes using the same corrupted shadow state and fails a second time. The monitor hits the single-retry limit ($N_{\text{retry}} = 1$), increments `persistent_count`, zeroizes both registers, and triggers fail-stop in `kem.c`.
- Result: **100% Safe Rejection** ($K == K_{\text{rej}}$). Zero corrupted key releases.

### 3.2. Retry-Path Second Faults (J09)
In J09, a transient fault occurs on the initial butterfly, triggering a legitimate rollback. However, a second transient fault is injected during the retry execution.
- The monitor enforces its strict retry bound: because the retry verification fails, the fault is classified as unrecoverable (`persistent_count++`). The butterfly registers are quenched, and implicit rejection is enforced downstream.
- Result: **100% Safe Rejection**. Proves the retry engine cannot enter an infinite loop.

### 3.3. Concurrent Forward and Inverse Transform Faults (J11)
When transient faults are injected into both the forward NTT in `indcpa_dec` and the inverse NTT in `indcpa_enc` within the same decapsulation:
- Both native monitors detect their respective invariant violations, roll back in place, and successfully recompute their coefficients.
- Result: **100% Autonomous Recovery** ($K == K_{\text{valid}}$).

### 3.4. Public API Fail-Stop Contract under NULL Pointer (J14)
When calling `mlkem768_dec(ss, ct, sk)` with `internal_status == NULL` under a persistent hardware fault:
- The function returns return code 0 (standard public API convention).
- The emitted shared secret $ss$ matches the deterministic implicit rejection key $K_{\text{rej}}(c_{\text{valid}}) = \text{SHAKE256}(z \parallel c_{\text{valid}})$ in **100 / 100 trials**.
- Valid shared key material is never released ($0 / 100$).
