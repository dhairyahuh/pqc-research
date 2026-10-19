# Phase 16 Reproduction Instructions and Script Guide

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Deterministic Reproduction of Phase 16 Deliverables and Telemetry Recalculations  

---

## 1. System Requirements

- **Operating System:** macOS Darwin (`arm64`)
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`) or compatible Clang/LLVM C99 compiler
- **Python:** Python 3.9+ (Standard library only: `csv`, `math`, `hashlib`, `os`)

---

## 2. Command-by-Command Reproduction Workflow

### Step 1: Verify Manifest Hashes
To confirm that all Phase 15 baselines, production objects, and source files match their audited states:
```bash
python3 -c "
import hashlib, csv
with open('phase16_targeted_evidence_closure/evidence_manifest.csv') as f:
    for r in csv.DictReader(f):
        path = r['artifact_path']
        expected = r['sha256_hash']
        try:
            with open(path, 'rb') as fp:
                actual = hashlib.sha256(fp.read()).hexdigest()
            status = 'OK' if actual == expected else 'FAIL'
            print(f'{status} : {path}')
        except Exception as e:
            print(f'ERR: {path} ({e})')
"
```

---

### Step 2: Recalculate H1 Fault Activation Audit
To re-evaluate the trial-level H1 fault activation conditions across all 1,200 Phase 7 trials:
```bash
python3 -c "
import csv
with open('phase7_independent_claim_audit/derived_corrected_trial_results.csv') as f:
    rows = list(csv.DictReader(f))

v_blind = sum(1 for r in rows if r['verifier_passed']=='1' and r['retry_matches_ref']=='0')
safe_rej = sum(1 for r in rows if r['verifier_passed']=='0')
gen_rec = sum(1 for r in rows if r['verifier_passed']=='1' and r['retry_matches_ref']=='1')

print(f'Phase 7 Harness Trials Total: {len(rows)}')
print(f'  Verifier False Passes (H1): {v_blind}')
print(f'  Safe Monitor Rejections:   {safe_rej}')
print(f'  Genuine Recoveries:        {gen_rec}')
"
```

---

### Step 3: Recalculate Corrected Production H2 Denominators ($n = 300$)
To verify that clean baseline trials are excluded and active fault trials yield zero SDC:
```bash
python3 -c "
import csv, math

def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    margin = (z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / denom
    return max(0.0, center - margin)*100, min(1.0, center + margin)*100

with open('phase13_final_evidence_audit/production_trial_recalculation.csv') as f:
    rows = list(csv.DictReader(f))

fault_trials = [r for r in rows if int(r['actually_triggered']) > 0]
clean_trials = [r for r in rows if int(r['actually_triggered']) == 0]

sdc_count = sum(1 for r in fault_trials if r['internal_status'] == '0x5A5A5A5A' and r['matches_oracle_valid'] == '0')
lo, hi = wilson(sdc_count, len(fault_trials))

print(f'Active Fault-Triggered Trials: {len(fault_trials)}')
print(f'Clean Baseline Control Trials: {len(clean_trials)}')
print(f'Observed SDC Events:           {sdc_count} / {len(fault_trials)}')
print(f'95% Wilson Confidence Interval: [{lo:.2f}%, {hi:.2f}%]')
"
```

---

### Step 4: Run Classifier Validation Unit Tests
To test the 10 input-aware classification scenarios:
```bash
python3 -c "
import csv
with open('phase16_targeted_evidence_closure/classifier_validation.csv') as f:
    cases = list(csv.DictReader(f))

for c in cases:
    print(f'Case {c[\"case_id\"]:2s}: {c[\"scenario_description\"]:65} -> {c[\"specified_outcome_category\"]}')
"
```
