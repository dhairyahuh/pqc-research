# Master Claim-Evidence Classification Matrix (Phase 10)

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Re-classification of All Major Research Claims Across Phases 1–10  

---

## 1. Six-Tier Classification Taxonomy

To ensure strict evidentiary integrity, all research claims are classified into one of the following six categories:
1. **Reproduced against production execution:** Empirically verified by executing authentic compiled production objects (`bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`) with unambiguous trigger accounting and output validation.
2. **Supported by source inspection:** Formally verified through analysis of C source code or compiled machine disassembly, but lacking dynamic perturbation or empirical measurement.
3. **Demonstrated only in a software model:** Experimentally observed in a constructed test harness or software mock; mathematically sound, but not implemented in production objects.
4. **Not reproduced:** Attempted under documented experimental conditions, but failed to produce the claimed outcome.
5. **Contradicted:** Directly disproven or falsified by empirical audit evidence.
6. **Inconclusive:** Insufficient data or contradictory observations preventing a definitive verdict.

---

## 2. Master Claim Classification Table

| Research Claim | Final Classification | Evidentiary Basis & Deliverable Link | Defensible Research Boundary |
| :--- | :---: | :--- | :--- |
| **Claim 1: Transient butterfly multiplier faults are 100% autonomously recovered via recomputation.** | **Reproduced against production execution** | [`corrected_production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_production_reproducer.c)<br>[`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (`F4`: 100/100) | Valid for transient ALU faults during intermediate multiplication under `NTT_NATIVE_MONITOR_RECOMPUTED_T`. |
| **Claim 2: Recurring persistent butterfly faults are 100% safely detected and fail-stop rejected.** | **Reproduced against production execution** | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (`F5A`: 100/100) | Recurring bit-inversion across passes trips persistent counter, enforcing `0xFFFFFFFF` and canonical implicit rejection key. |
| **Claim 3: Hardware stuck-at-zero faults are 100% safely detected and fail-stop rejected.** | **Reproduced against production execution** | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (`F5B`: 100/100) | Clamping value to 0 via `FAULT_TYPE_FORCE_VALUE` trips persistent counter, safely returning canonical implicit rejection key. |
| **Claim 4: Clean baseline decapsulation executes with zero false alarms.** | **Reproduced against production execution** | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (`F12`: 100/100) | Correctly classified as `CLEAN_SUCCESS` across 5,376 butterflies per trial. |
| **Claim 5: Recovery verifiers relying on in-place saved snapshots exhibit algorithmic blindness.** | **Demonstrated only in a software model** | [`fault_hook_semantics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fault_hook_semantics.md)<br>[`h1_h2_revalidation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/h1_h2_revalidation.md) (`F1`: 98%, `F2`: 70%) | In-tree production code passes `u_saved` by value on stack without injection hooks. Validated in faithful software models. |
| **Claim 6: Phase 6 claim that F4 exhibited false recovery.** | **Contradicted** | [`symbol_resolution_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/symbol_resolution_audit.md)<br>[`h1_h2_revalidation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/h1_h2_revalidation.md) | Disproven. Artifact of a 1D reference table collision in Phase 6. When indexed correctly, F4 achieves 100% genuine recovery. |
| **Claim 7: Fujisaki-Okamoto re-encryption prevents Silent Data Corruption ($H_2$) across tested internal faults.** | **Reproduced against production execution** | [`fo_dual_rail_claim_boundary.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fo_dual_rail_claim_boundary.md)<br>[`h1_h2_revalidation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/h1_h2_revalidation.md) (0/1,300 SDC) | Tested across 1,300 trials in decapsulation. Outer FO transform rejects invalid ciphertexts. Does not apply to primitives without FO loops. |
| **Claim 8: F2's 30% genuine recovery / 70% rejection split is caused by diffusion depth vs compression quantization.** | **Demonstrated only in a software model** | [`f2_trace_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/f2_trace_audit.md)<br>[`f2_trace_evidence.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_trace_evidence.csv) | Verified in harness-level model: Stages 1–2 diffuse across $\ge 64$ coords (`ct == tmp`); Stages 3–7 diffuse across $\le 32$ coords (`ct != tmp`). Production-path wording withdrawn. |
| **Claim 9: FO conditional key selection is branchless on ARM64.** | **Supported by source inspection** | [`fo_dual_rail_claim_boundary.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fo_dual_rail_claim_boundary.md) | Disassembly of `bin/obj/mlkem768_inst.o` (`fea4-fed4`) confirms branchless `bic`/`and`/`orr` loop. Hardware timing distributions unmeasured. |
| **Claim 10: Dual-Snapshot Parity Checksum (DSPC) provides robust mitigation against snapshot corruption.** | **Demonstrated only in a software model** | [`dspc_implementation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/dspc_implementation_audit.md) | DSPC does not exist in production code (`algorithms/source_ref/`). Vulnerable to correlated 2-bit linear collisions in software model. |
| **Claim 11: Physical clock glitches can bypass DSPC via branch skipping.** | **Demonstrated only in a software model** | [`dspc_implementation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/dspc_implementation_audit.md) | Software simulation of branch skip. Physical hardware feasibility not experimentally measured on physical silicon. |
