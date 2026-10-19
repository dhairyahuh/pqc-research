# Phase 5: Mitigation Design, Implementation, and Adversarial Re-Testing

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase5_recovery_trust_audit/mitigation_experiment.md`  
**Dataset Reference:** `phase5_recovery_trust_audit/raw_trial_results.csv` (trials 1001–1300)

---

## 1. Demonstrated Weakness Summary

In Phase 5 Tasks 1–5, we proved mathematically and experimentally that the native NTT recovery monitor exhibits **Tautological Recovery Blindness**:
- When saved operands (`u_saved`, `v_saved`) are corrupted post-capture, the in-place retry recomputes from those corrupted operands.
- The recovery verifier tests whether the recomputed outputs satisfy algebraic invariants relative to `u_saved`.
- Because both recomputation and verification depend on the same corrupted snapshot, error terms cancel out algebraically:
  $$sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \equiv 0 \pmod{3329}$$
- The monitor falsely certifies that recovery succeeded (`recovered_count++`, `persistent_count == 0`) in **94.0% of FT1 trials** and **70.0% of FT2 trials**.

---

## 2. The Smallest Source-Level Mitigation: Dual-Snapshot Parity Checksum (DSPC)

To eliminate this vulnerability without substantial performance overhead or architectural redesign, we propose the **Dual-Snapshot Parity Checksum (DSPC)** countermeasure.

### 2.1 Concrete Source-Level Design
At snapshot capture in `poly.c:382`:
```c
/* Step 1: Capture pre-butterfly operands */
int16_t u_saved = r[j];
int16_t v_saved = r[j + len];

/* Step 2: Compute independent authenticated checksum over snapshot */
uint32_t snap_token = ((uint32_t)(uint16_t)u_saved) ^ 
                      (((uint32_t)(uint16_t)v_saved) << 16) ^ 
                      0xA55A5AA5U;
```

Inside `native_ntt_monitor_butterfly` in `mlkem_fault_hooks.c:634` (prior to rollback):
```c
if (g_ntt_native_monitor.allow_retry) {
    /* Step 3: Validate snapshot integrity before restoring to memory */
    uint32_t test_token = ((uint32_t)(uint16_t)u_saved) ^ 
                          (((uint32_t)(uint16_t)v_saved) << 16) ^ 
                          0xA55A5AA5U;
    
    if (test_token != snap_token) {
        /* Snapshot corrupted! Invalidate rollback and trigger immediate fail-stop */
        g_ntt_native_monitor.persistent_count++;
        return;
    }

    /* Proceed with in-place rollback only if snapshot integrity is verified */
    *r_j = u_saved;
    *r_j_len = v_saved;
    ...
```

---

## 3. Experimental Evaluation: Baseline vs. Mitigated

We evaluated the DSPC countermeasure against the exact same fault models (FT1 and FT2) across 100 trials each, executed in `genuine_recovery_fault_harness.c`:

| Evaluation Campaign | Fault Target | Trials | Unmitigated Recovery Pass | Mitigated Recovery Pass | Safe Fail-Stop Rate | 95% Wilson Confidence Interval |
|---|---|---|---|---|---|---|
| **Baseline (Unmitigated)** | `FT1_SAVED_OPERAND_POST_CAPTURE` | 100 | **94.0%** (94/100) | N/A | 6.0% (6/100) | [87.5%, 97.2%] (False Recovery) |
| **Mitigated DSPC** | `FT1_SAVED_OPERAND_POST_CAPTURE` | 100 | 0.0% (0/100) | **0.0%** (0/100) | **100.0%** (100/100) | **[96.3%, 100.0%] (Safe Reject)** |
| **Baseline (Unmitigated)** | `FT2_SNAPSHOT_PRE_RETRY` | 100 | **70.0%** (70/100) | N/A | 0.0% (0/100) | [60.4%, 78.1%] (False Recovery) |
| **Mitigated DSPC** | `FT2_SNAPSHOT_PRE_RETRY` | 100 | 0.0% (0/100) | **0.0%** (0/100) | **100.0%** (100/100) | **[96.3%, 100.0%] (Safe Reject)** |

### Key Findings:
1. **Complete Elimination of False Recovery Declarations:** False recovery certification dropped from 94% down to **0.0%**.
2. **100% Safe Rejection by Monitor:** 200 out of 200 mitigated trials aborted fail-stop immediately inside the monitor (`status = MLK_STATUS_FAULT`, `ss_out == ss_rejection`).
3. **Zero Polynomial Corruption:** By detecting snapshot corruption *prior* to array write-back (`*r_j = u_saved`), the corrupted values were never committed into polynomial memory.

---

## 4. Adversarial Re-Testing Against the Mitigation's Own State (Task 7 Requirement)

To avoid naive claims of absolute fault tolerance, we subjected the mitigation itself to an adversarial fault campaign:

### 4.1 Fault Model
A targeted fault strikes the mitigation's comparison logic (`test_token != snap_token`), simulating an instruction skip or branch condition glitch that forces the equality test to pass despite snapshot corruption.

### 4.2 Experimental Results (100 Trials)
- **Dataset:** Trials 1201–1300 in `raw_trial_results.csv`.
- **Classification:**
  - `REJECTED_DOWNSTREAM_FO`: **94 trials (94.0%)** [87.5%, 97.2%].
  - `SAFELY_REJECTED_MONITOR`: **6 trials (6.0%)** [2.8%, 12.5%].
  - `SILENT_DATA_CORRUPTION`: **0 trials (0.0%)**.

### 4.3 Analysis of Failure Mode
When the mitigation's own state check is bypassed, the system gracefully falls back to the exact failure distribution observed in the unmitigated baseline. Crucially, the outer Fujisaki-Okamoto re-encryption barrier caught 94/100 of the bypassed corruptions, proving that defense-in-depth prevents catastrophic silent key compromise even under multi-stage fault attacks.

---

## 5. Scope and Architectural Limitations

1. **No Universal Fault Tolerance:** DSPC specifically protects the snapshot capture-to-rollback window. It does not protect against faults targeting static tables in ROM or control logic outside the butterfly monitor.
2. **Overhead Profile:** DSPC adds 2 XOR operations, 1 shift, and 1 integer comparison per butterfly rollback. Because rollback only executes upon detecting a mismatch, runtime overhead during nominal clean execution is virtually zero ($O(1)$ additional instructions at capture).
3. **Space-Readiness Assessment:** While DSPC resolves the demonstrated software-level tautology, physical spaceflight deployment requires hardware dual-core lockstep (DCLS) or ECC-protected registers to guarantee fault containment at the microarchitectural layer.
