# Phase 17B: Targeted Manuscript Correction and Evidence Traceability

**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Branch:** `space-resilience-framework`  
**Phase:** Phase 17B (Final Manuscript Correction & Evidence Traceability Package)  
**Date:** October 2026  
**Audited Baseline:** `phase17a_verification/` and `phase16_targeted_evidence_closure/`

---

## 1. Overview and Purpose

This directory (`phase17b_corrected/`) contains the complete, corrected, and verified academic deliverables for the ML-KEM-768 fault-resilience research. 

Following the forensic integrity audit in Phase 17A, Phase 17B has:
1. Applied all bibliographic corrections, including the complete withdrawal of unverified citation P09 and substitution of P13 with Fritzmann et al. DATE 2019.
2. Narrowed novelty claims to acknowledge prior art in Cooley-Tukey hardware invariants (Paul et al. 2026) and classical common-mode failure theory.
3. Reconciled every numerical metric line-by-line against Phase 16 empirical manifests.
4. Excised all unsupported constant-time claims and mathematical SDC impossibility assertions.
5. Formally established threat-model boundaries (delineating non-adversarial radiation SEU from active SIFA attacks).

---

## 2. Directory Index and Deliverables

| Deliverable File | Description | Core Purpose & Contents |
|:---|:---|:---|
| [`manuscript_draft.md`](./manuscript_draft.md) | Revised Research Manuscript | Fully revised academic draft incorporating calibrated novelty framing, accurate citations, validated numbers, and explicit limitations. |
| [`references.md`](./references.md) | Corrected Bibliography | Cleaned, fully verified reference list with primary publisher DOIs, updated years/venues, and documented withdrawals. |
| [`claim_evidence_map.csv`](./claim_evidence_map.csv) | Claim-to-Evidence Matrix | Line-by-line mapping of all 14 major manuscript claims to raw source files, verification methods, statuses, and qualifications. |
| [`numerical_reconciliation.csv`](./numerical_reconciliation.csv) | Quantitative Metric Reconciliation | Full reconciliation of original Phase 17 draft values, verified values, data sources, discrepancies found, and final resolutions. |
| [`citation_change_log.md`](./citation_change_log.md) | Bibliographic Change Log | Comprehensive ledger of all bibliographic additions, substitutions (P13), corrections (P03, P04, P08, P10, P15), and withdrawals (P09). |
| [`limitations_and_validity.md`](./limitations_and_validity.md) | Threats to Validity Statement | Transparent declaration of experimental, statistical, implementation, threat-model, and microarchitectural boundaries. |
| [`revision_summary.md`](./revision_summary.md) | Substantive Revision Report | High-level summary of changes, unresolved future work items, and final supervisor review readiness verdict. |
| [`README.md`](./README.md) | Directory Guide and Reproduction Manual | Guide to reviewing artifacts, reproducing statistical calculations, and compiling source code. |

---

## 3. How to Reproduce Supported Calculations

### 3.1. Wilson Score Confidence Intervals
To compute the exact 95% Wilson score confidence intervals reported in the manuscript:

```python
import math

def wilson_score_interval(successes, total, z=1.95996):
    """Compute Wilson score interval for a binomial proportion."""
    if total == 0:
        return (0.0, 0.0)
    p = successes / total
    denom = 1 + (z**2) / total
    centre = (p + (z**2) / (2 * total)) / denom
    half_width = (z * math.sqrt((p * (1 - p) / total) + (z**2) / (4 * total**2))) / denom
    lower = max(0.0, centre - half_width)
    upper = min(1.0, centre + half_width)
    return lower * 100.0, upper * 100.0

# 1. Target F4 Genuine Recovery (100 / 100)
f4_low, f4_high = wilson_score_interval(100, 100)
print(f"Target F4 Recovery: [{f4_low:.1f}%, {f4_high:.1f}%]")
# Output: [96.3%, 100.0%]

# 2. Production SDC Rate (0 / 300 active fault trials)
sdc_low, sdc_high = wilson_score_interval(0, 300)
print(f"Production SDC: [{sdc_low:.2f}%, {sdc_high:.2f}%]")
# Output: [0.00%, 1.26%]

# 3. Targets F5A/F5B Fail-Stop Containment (200 / 200)
f5_low, f5_high = wilson_score_interval(200, 200)
print(f"Persistent Fail-Stop: [{f5_low:.1f}%, {f5_high:.1f}%]")
# Output: [98.1%, 100.0%]
```

### 3.2. Butterfly Operation Count Breakdown
The 9,856 butterfly count derives from the polynomial transform structure of ML-KEM-768 decapsulation ($k=3, n=256$):
- Each 256-coefficient polynomial NTT or InvNTT has 7 layers of 128 butterflies:
  $$\text{Butterflies per polynomial} = 7 \times 128 = 896$$
- Decapsulation and FO re-encryption execute 11 polynomial transforms:
  - 3 $\times$ InvNTT ($\mathbf{u}$) = $3 \times 896 = 2{,}688$
  - 3 $\times$ NTT ($\mathbf{s}$) = $3 \times 896 = 2{,}688$
  - 1 $\times$ InvNTT ($\mathbf{s}^T \mathbf{u}$) = $1 \times 896 = 896$
  - 3 $\times$ NTT ($\mathbf{r}$) in re-encryption = $3 \times 896 = 2{,}688$
  - 1 $\times$ InvNTT in re-encryption = $1 \times 896 = 896$
- Total = $11 \times 896 = 9{,}856$ butterfly operations.

### 3.3. Compiling and Running Production Fault Experiments
From the repository root:
```bash
# Clean previous builds
make clean

# Compile ML-KEM with native fault monitoring hooks enabled
make fault_experiment FAULT_HOOKS=1

# Run the automated fault test suite
./bin/fault_experiment
```

---

## 4. Final Review Status

**Status:** **READY FOR SUPERVISOR REVIEW**  
All identified integrity, bibliographic, and claim-traceability discrepancies have been resolved. The manuscript is mathematically grounded, bibliographically clean, and defensible under peer review.
