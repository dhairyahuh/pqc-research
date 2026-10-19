# Master Claim-Evidence Classification Matrix

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Scope:** Formal Verification Status of All Research Claims (Phases 1–9)  

---

## 1. Classification Taxonomy

Every scientific claim is classified strictly into one of five evidentiary categories:
1. **Reproduced against production objects:** Demonstrated through execution of authentic compiled binaries (`bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`) without test stubs or metric overrides.
2. **Supported by source inspection only:** Derived analytically from C source or compiled assembly; mathematically verified but not dynamically perturbed in software.
3. **Demonstrated only in a software model:** Experimentally observed in a constructed test harness or software mock; represents a valid algorithmic model of the recovery arithmetic but does not run in production objects.
4. **Not reproduced:** Contradicted or disproven by independent audit execution.
5. **Inconclusive:** Insufficient data or contradictory experimental evidence.

---

## 2. Master Evidentiary Classification Matrix

| Research Claim | Evidentiary Status | Supporting Evidence & Files | Scope Qualifications & Boundaries |
| :--- | :---: | :--- | :--- |
| **Claim 1: Transient multiplier faults in forward NTT are 100% autonomously recovered via recomputation.** | **Reproduced against production objects** | [`production_path_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_path_reproduction.md)<br>[`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/raw_trial_results.csv) (Target F4: 100/100) | Valid for transient ALU faults during butterfly multiplication under `NTT_NATIVE_MONITOR_RECOMPUTED_T`. |
| **Claim 2: Persistent hardware faults are 100% safely detected and fail-stop rejected via implicit rejection.** | **Reproduced against production objects** | [`production_path_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_path_reproduction.md)<br>[`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/raw_trial_results.csv) (Target F5: 100/100) | Stuck-at faults cause persistent invariant failures, tripping line 486 of `kem.c` to enforce status `0xFFFFFFFF`. |
| **Claim 3: Clean decapsulation preserves full mathematical correctness across all 5,376 butterflies.** | **Reproduced against production objects** | [`production_path_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_path_reproduction.md)<br>[`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/raw_trial_results.csv) (Target F12: 100/100) | Zero false alarms observed in uncorrupted executions. |
| **Claim 4: Recovery verifiers relying on in-place saved snapshots exhibit algorithmic blindness under snapshot corruption.** | **Demonstrated only in a software model** | [`c_arithmetic_and_compiler_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/c_arithmetic_and_compiler_audit.md)<br>[`harness_vs_production_diff.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/harness_vs_production_diff.md)<br>(Targets F1, F2: 98% and 70%) | Production source does not provide hooks into stack-passed `u_saved`. Validated in software models sharing exact production arithmetic. |
| **Claim 5: Phase 6 claim that F4 exhibited false recovery was an artifact of an oracle reference collision bug.** | **Reproduced against production objects** | [`oracle_independence_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/oracle_independence_audit.md)<br>[`symbol_resolution_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/symbol_resolution_audit.md) | Disproven in Phase 7/8/9. Phase 6 compared Polynomial 0 against Polynomial 5. When indexed correctly, F4 is 100% genuine recovery. |
| **Claim 6: Outer Fujisaki-Okamoto re-encryption prevents Silent Data Corruption ($H_2$) across internal monitor failures.** | **Reproduced against production objects** | [`fo_and_dual_rail_claim_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/fo_and_dual_rail_claim_audit.md)<br>[`h1_h2_recalculation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/h1_h2_recalculation.md) (0/1,200 SDC) | Tested across 1,200 trials. Outer FO transform rejects invalid ciphertexts. Does not apply to primitives without FO loops. |
| **Claim 7: F2's 30% genuine recovery / 70% rejection split is caused by diffusion depth vs compression rounding.** | **Reproduced against production objects** | [`f2_causal_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_causal_audit.md)<br>[`f2_trace_evidence.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_trace_evidence.csv) | Verified by direct measurement: Stages 1–2 diffuse across $\ge 64$ coords (`ct == tmp`); Stages 3–7 diffuse across $\le 32$ coords (`ct != tmp`). |
| **Claim 8: FO conditional key selection is constant-time on AArch64 under Apple Clang.** | **Supported by source inspection only** | [`fo_and_dual_rail_claim_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/fo_and_dual_rail_claim_audit.md) | Assembly inspection confirms branchless `bic`/`and`/`orr` loop. Empirical timing distributions require dedicated hardware oscilloscope testing. |
| **Claim 9: Dual-Snapshot Parity Checksum (DSPC) provides robust mitigation against snapshot corruption.** | **Demonstrated only in a software model** | [`dspc_implementation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/dspc_implementation_audit.md) | DSPC does not exist in production code (`algorithms/source_ref/`). Vulnerable to correlated 2-bit linear collisions in software model. |
| **Claim 10: Clock glitch branch skips can bypass DSPC in physical hardware.** | **Demonstrated only in a software model** | [`dspc_implementation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/dspc_implementation_audit.md) (Target F10: 100%) | Construct software simulation of branch skip. Physical hardware feasibility not experimentally measured on physical silicon. |

---

## 3. Evidentiary Boundary Summary

- **Production-Verified Core:**  
  Autonomous transient recovery (F4), persistent fail-stop rejection (F5), clean baseline execution (F12), and outer Fujisaki-Okamoto re-encryption containment are **100% reproducible against the authentic compiled objects**.
- **Software-Modeled Recovery Blindness:**  
  Recovery-verifier blindness under corrupted operand snapshots (F1, F2) is **mathematically sound and verified in faithful software arithmetic models**, but has not been natively integrated into in-tree firmware hooks.
- **Physical Feasibility Boundaries:**  
  All branch skip and physical fault injection claims remain **software-constructed models** until validated on physical hardware (e.g., ARM Cortex-M4 testbed using laser or EMFI).
