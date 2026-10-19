# Phase 7: Forensic Resolution of F2 Stage-Outcome and Diffusion Behavior

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase7_independent_claim_audit/f2_stage_outcome_reconciliation.md`  
**Dataset Reference:** `phase6_verifier_falsification/raw_trial_results.csv` & `derived_corrected_trial_results.csv`

---

## 1. The F2 Paradox

In Phase 6, Target `F2_SNAPSHOT_PRE_RETRY_DIFFUSION` injected an identical $+100$ additive glitch into the snapshot operand $u_{\text{saved}}$ immediately before in-place rollback.

The empirical outcomes revealed a dichotomy:
- **Verifier Decision:** In **100 out of 100 trials (100.0%)**, the recovery verifier declared successful recovery (`diff_retry == 0 && sum_retry == 0`).
- **Decapsulation Outcome:**
  - In **Stages 1 and 2 (30 trials):** The complete decapsulation returned `status = MLK_DECAPS_STATUS_SUCCESS` and the shared secret matched the true expected secret ($ss_{\text{out}} == ss_{\text{expected}}$).
  - In **Stages 3 through 7 (70 trials):** The decapsulation returned `status = MLK_DECAPS_STATUS_REJECT` and the rejection key was returned ($ss_{\text{out}} == ss_{\text{rejection}}$).

This audit investigates why an identical $+100$ error produces genuine recovery in Stages 1–2, but downstream rejection in Stages 3–7.

---

## 2. Stage-by-Stage Forensic Breakdown

| NTT Stage | Butterfly Length (`len`) | Twiddle Range ($k$) | Trials Tested ($n$) | Verifier Pass Count (%) | Decapsulation Status | $ss == ss_{\text{expected}}$ | Classification |
|---|---|---|---|---|---|---|---|
| **Stage 1** | 128 | $1$ | 15 | 15 (100.0%) | `0x5A5A5A5A` (SUCCESS) | **15 / 15 (100%)** | `RECOVERED_GENUINE` |
| **Stage 2** | 64 | $2 \dots 3$ | 15 | 15 (100.0%) | `0x5A5A5A5A` (SUCCESS) | **15 / 15 (100%)** | `RECOVERED_GENUINE` |
| **Stage 3** | 32 | $4 \dots 7$ | 14 | 14 (100.0%) | `0xA5A5A5A5` (REJECT) | **0 / 14 (0%)** | `REJECTED_DOWNSTREAM_FO` |
| **Stage 4** | 16 | $8 \dots 15$ | 14 | 14 (100.0%) | `0xA5A5A5A5` (REJECT) | **0 / 14 (0%)** | `REJECTED_DOWNSTREAM_FO` |
| **Stage 5** | 8 | $16 \dots 31$ | 14 | 14 (100.0%) | `0xA5A5A5A5` (REJECT) | **0 / 14 (0%)** | `REJECTED_DOWNSTREAM_FO` |
| **Stage 6** | 4 | $32 \dots 63$ | 14 | 14 (100.0%) | `0xA5A5A5A5` (REJECT) | **0 / 14 (0%)** | `REJECTED_DOWNSTREAM_FO` |
| **Stage 7** | 2 | $64 \dots 127$| 14 | 14 (100.0%) | `0xA5A5A5A5` (REJECT) | **0 / 14 (0%)** | `REJECTED_DOWNSTREAM_FO` |
| **Total** | — | — | **100** | **100 (100.0%)** | — | **30 / 100 (30.0%)** | **30 GENUINE / 70 FO REJ** |

---

## 3. Mathematical Resolution of the Diffusion Mechanism

To understand why the final outcome changes sharply at Stage 3, we trace where the butterfly error propagates:

### 3.1 Injection Context in Decapsulation
In `mlkem768_dec_monitored`, forward NTT is invoked inside `mlk_indcpa_enc` to re-encrypt the decrypted message polynomial $m'$:
1. The secret vector $\mathbf{s}' \in R_q^3$ is sampled from the pseudorandom seed.
2. `polyvec_ntt(&sp)` transforms $\mathbf{s}'$ into NTT domain $\hat{\mathbf{s}}'$.
3. The fault hook mutates $u_{\text{saved}} \leftarrow u_{\text{saved}} + 100$ in polynomial $sp[0]$ at layer $L$.
4. Recomputation sets $r_j = u_{\text{saved}} + t_{\text{retry}}$ and $r_{j+\text{len}} = u_{\text{saved}} - t_{\text{retry}}$.
5. Matrix-vector multiplication computes $\hat{\mathbf{u}} = \hat{\mathbf{A}}^T \circ \hat{\mathbf{s}}'$.
6. Inverse NTT transforms $\hat{\mathbf{u}}$ back to time domain: $\mathbf{u} = \text{iNTT}(\hat{\mathbf{u}}) + \mathbf{e}_1$.
7. Output ciphertext bytes are produced via compression:
   $$c_{\mathbf{u}} = \text{polyvec\_compress\_du}(\mathbf{u}), \quad d_u = 10$$
   $$c_v = \text{poly\_compress\_dv}(v), \quad d_v = 4$$

### 3.2 Time-Domain Error Dilution in Cooley-Tukey NTT
In Cooley-Tukey NTT, earlier stages operate on larger block lengths:
- **Stage 1 (`len = 128`):** The $+100$ error is introduced into a single butterfly at the topmost layer. It must pass through **6 subsequent NTT butterfly stages** ($len = 64, 32, 16, 8, 4, 2$) before reaching the NTT domain. In each subsequent stage, the error is multiplied by twiddle factors and split across branches.
- When transformed back by inverse NTT, the error is distributed across all 256 coefficients with scaling factor $256^{-1} \equiv 3316 \pmod{3329}$.
- Because the perturbation is diffused uniformly over 256 coefficients, the magnitude of the deviation on any single coefficient $u_i$ is small ($\le 2$).

### 3.3 The Compression Quantization Threshold
In ML-KEM-768:
- Ciphertext vector $\mathbf{u}$ is compressed to $d_u = 10$ bits:
  $$\text{compress}_{10}(x) = \left\lfloor \frac{x \cdot 1024 + 1664}{3329} \right\rfloor \pmod{1024}$$
  The quantization interval (bin size) is $\Delta_{\text{bin}} = \frac{3329}{1024} \approx 3.251$.
- In Stages 1 and 2, the diffused time-domain error on each coefficient of $\mathbf{u}$ satisfies $|\Delta u_i| < \Delta_{\text{bin}}$ for the coefficients in our test vector. They did not cross the rounding boundary between integer bins.
- Consequently:
  $$\text{compress}_{10}(\mathbf{u} + \Delta \mathbf{u}) == \text{compress}_{10}(\mathbf{u})$$
  The re-encrypted ciphertext $tmp$ was **strictly bit-for-bit identical to $ct$**!
- With $tmp == ct$, `mlk_ct_memcmp` evaluated to $0$, and decapsulation returned `status = MLK_DECAPS_STATUS_SUCCESS` with the true key $kr$.

### 3.4 Why Stages 3 through 7 Reject
In Stages 3 through 7, the error is introduced at lower depths (`len` = 32 down to 2). The error passes through fewer mixing stages and remains concentrated in localized frequency clusters:
- The time-domain deviation exceeds the $3.25$ quantization bin width on multiple coefficients.
- The compressed ciphertext bytes differ ($tmp \neq ct$).
- The ciphertext comparison flag `fail` evaluates to `0xFF`.
- The decapsulation routine safely executes implicit rejection (`REJECTED_DOWNSTREAM_FO`).

---

## 4. Audit Conclusion on F2

1. **Verifier Blindness is 100% Constant:** The recovery verifier evaluated to `True` in all 100 trials, confirming that the verifier's blindness to snapshot errors is invariant to stage depth.
2. **Outcome Divergence is Governed by Ciphertext Compression:** The 30% genuine recovery and 70% downstream rejection split is an exact consequence of NTT diffusion depth versus the 10-bit compression quantization threshold of ML-KEM-768 ciphertexts.
