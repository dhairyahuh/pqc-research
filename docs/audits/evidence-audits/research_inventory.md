# Research Inventory and Authoritative Baseline

**Project Title:** Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment  
**Repository State:** Git Branch `space-resilience-framework`, Commit `55dd937cbad66b24e5c2c0b89b78fa776801913c`  
**Authoritative Baseline:** Post-Phase 18 Verified Codebase and Datasets  
**Date:** October 2026  

---

## 1. Source Code Inventory

| Component | Source Path | Role & Functions |
|:---|:---|:---|
| **KEM Top-Level** | `algorithms/source_ref/kem/kem.c` | Top-level `crypto_kem_dec()`, FIPS 203 Section 7.3 implicit rejection, dual-rail ciphertext comparison (`mlk_ct_memcmp` & `mlk_ct_memcmp_reverse`). |
| **CPA Decapsulation & Re-encryption** | `algorithms/source_ref/cpa/indcpa.c` | Decapsulation (`mlk_indcpa_dec`) with 3 Forward NTTs on ciphertext $\mathbf{u}$ and 1 Inverse NTT on recovered polynomial; Re-encryption (`mlk_indcpa_enc`) with 3 Forward NTTs on sample $\mathbf{r}$, 3 Inverse NTTs on candidate $\mathbf{u}'$, and 1 Inverse NTT on candidate $v'$. |
| **Polynomial Transforms** | `algorithms/source_ref/cpa/poly.c` | Forward Cooley-Tukey NTT (`mlk_poly_ntt`) and Inverse Gentleman-Sande NTT (`mlk_poly_invntt`), instrumented with `MLK_CHECK_BUTTERFLY_CT` and `MLK_CHECK_BUTTERFLY_GS`. |
| **Fault Resilience Engine** | `algorithms/source_ref/cpa/mlkem_fault_hooks.c` | Butterfly snapshot creation (`u_saved`, `v_saved`, `zeta_saved`), algebraic invariant checks, bounded retry loop ($\le 2$ retries), rollback restoration, and containment escalation (`fail = 0xFF`, `status = 0xFFFFFFFF`). |
| **Headers & Constants** | `algorithms/source_ref/include/` | Data structures, polynomial formats, twiddle tables, and API exports (`kem.h`, `poly.h`, `indcpa.h`). |

---

## 2. Authoritative Datasets and Raw Experimental Records

| Dataset File | Trials | Target Models | Status / Origin | Primary Metrics |
|:---|:---:|:---|:---:|:---|
| `phase18_audit/raw_production_trials.csv` | 400 | F12 (Control), F4 (Transient Multiplier), F5A (Persistent Multiplier), F5B (Force-Value Zero) | Authoritative (Fresh Phase 18 Reproduction) | F12: 100/100 Success<br>F4: 100/100 Recovered ($K_{\text{valid}}$)<br>F5A: 100/100 Aborted ($K_{\text{rej}}$)<br>F5B: 100/100 Aborted ($K_{\text{rej}}$)<br>Production SDC: 0/300 ($[0.00\%, 1.26\%]$ CI) |
| `phase16_targeted_evidence_closure/h1_activation_audit.csv` | 600 | H1 Standalone Verifier Blindness (6 vulnerable targets) | Authoritative (Phase 16 Cleanroom) | Verifier False-Pass Rate: 94.0% to 100.0% ($591 / 600 = 98.5\%$) |
| `phase14_f4_f5_audit/raw_f4_f5_production_trials.csv` | 400 | F12, F4, F5A, F5B Historical Baseline | Authoritative Historical Record | Identical outcomes matching Phase 18 fresh run |
| `results/phase7i/processed/phase7i_e2e_results.json` | 2,000 | Benchmark timing: Baseline, Monitored, Software DMR | Authoritative Performance Record | Latency: $110.77\,\mu\text{s}$ (Base), $129.51\,\mu\text{s}$ (Mon), $260.68\,\mu\text{s}$ (DMR) |

---

## 3. Discrepancy Reconciliation Ledger

To prevent silent errors or narrative drift, the following authoritative resolutions have been established:

1. **Transform Call Graph Narrative:**
   - *Draft Error:* Claimed decapsulation runs Inverse NTT on $\mathbf{u}$ and Forward NTT on $\mathbf{s}$.
   - *Authoritative Finding:* Decapsulation runs **Forward NTT** on $\mathbf{u}$ (`mlk_polyvec_ntt(b)` at `indcpa.c:609`). The secret key $\hat{\mathbf{s}}$ is pre-transformed in NTT form in the decapsulation key blob and is **never transformed**. Re-encryption executes 3 Forward NTTs on $\mathbf{r}$, 3 Inverse NTTs on $\mathbf{u}'$, and 1 Inverse NTT on $v'$. Total: exactly 11 transforms ($6\text{ Forward} + 5\text{ Inverse}$) = $9{,}856$ butterflies.
2. **GS Invariant Implementation:**
   - *Draft Derivation:* $r_0 + \zeta r_1 \equiv 2u \pmod q$.
   - *Implementation Form:* To eliminate expensive modular inversions in software, `mlkem_fault_hooks.c` verifies $r_0 \equiv u + v \pmod q$ and $r_1 \equiv (v - u) \cdot \zeta \pmod q$. Both forms are mathematically equivalent in $\mathbb{Z}_q$.
3. **Twiddle Factor Blindness:**
   - The monitor and butterfly load the identical scalar `zeta_val`. Arithmetic verification cannot detect twiddle table corruption. Outer FO re-encryption detects and contains twiddle faults.
4. **Target F5B Semantics:**
   - Target $F5B$ ($t \leftarrow 0$) is an abstract software debug hook forcing a local C variable to zero. It does not model physical silicon stuck-at faults.
5. **Side-Channel Claims:**
   - Branching in the recovery path prevents claiming certified constant-time security under fault conditions without TVLA or dudect machine-code validation.
