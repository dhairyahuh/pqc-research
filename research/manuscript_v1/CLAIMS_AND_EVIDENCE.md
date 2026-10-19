# Claims and Evidence Mapping — Manuscript v1

Each manuscript claim → exact artifact(s), script, and result field. Numbers were recomputed from
raw records by `research/phase2_4_report/audit/independent_audit.py` (AUDIT PASSED, 0 discrepancies)
and `research/phase2_4_report/make_figures.py`. Categories: OBS = directly observed/recomputed;
MODEL = F-conditional estimate; ASSUMP = model assumption; UNSUP = explicitly not claimed.

| Manuscript claim | Cat | Evidence (path / field) |
|---|---|---|
| Oracle = liboqs 0.16.0 + standalone SHAKE-256; SHAKE matches hashlib (4 vectors) | OBS | `tfib_experiments/phase11_oracle/{independent_oracle.c,fips202_ref.c}`; EVIDENCE_LEDGER L3/L4 |
| Clean/KAT builds exclude fault hooks | OBS | `Makefile` (kat objects lack `-DMLKEM_RESEARCH_FAULT_HOOKS`); EVIDENCE_LEDGER L19 |
| Phase 2: 900 trials, 750 activated, 0 SDC | OBS | `research/results/phase2_mem_logical_v1/raw.jsonl`; audit "Phase2" checks |
| Phase 2: detected 600/750; RECOVERED 250 / SAFE_FAIL_DETECTED 350 / SAFE_FAIL_FO_CONTAINED 147 / INEFFECTIVE 3 / CLEAN 150 | OBS | same raw; `terminal_outcome`, `monitor_detected`, `injection_status` |
| Phase 2 recovery is structural (logical-value), not persistent-memory | OBS | code `poly.c:381-408`, `tfib_implementation/tfib_ref.c:93-122`; EVIDENCE_LEDGER L8 |
| Phase 3: 600 sessions; outcomes EST100/REC200/MALF100/LOST100/TIMEOUT50/ABORT50 | OBS | `research/results/phase3_channel_v1/raw.jsonl`; audit "Phase3" checks |
| Phase 3: crypto verdict VALID350/REJECT50/UNAVAILABLE200 (separate dim) | OBS | same raw; `crypto_verdict` |
| Phase 3: seven fault classes + clean (NOT six) | OBS | raw distinct `channel_class` = 8 incl CLEAN; `PROTOCOL_FAULT_MODEL_SPEC.md:67-69`; see OPEN_ISSUES |
| Phase 4: 500 seeds × 4 = 2000; each seed 4 matched conditions; 0 excluded/inconclusive | OBS | `research/results/phase4_combined_v1/raw.jsonl`; audit "Phase4" checks |
| Phase 4 completion 100.0/48.0/56.4/26.0% | OBS | same raw; `established` by `condition`; `tables/table_phase4_conditions` |
| Δ̂ = +0.216, paired-bootstrap 95% CI [+0.180,+0.252] | MODEL | `combined_stats.py`; audit independent bootstrap; `tables/table_interaction` |
| Masking 203/500 = 40.6% of C11; masked≠recovery; est-among-masked 57/203 vs activated 73/297 | OBS | raw `mem_injection_status`,`established`; audit "masking"; `figures/fig4_masking.png` |
| Δ_persistent +0.419 [+0.360,+0.477]; Δ_transient = 0 (per-seed identity, max|d_i|=0) | OBS/MODEL | audit conditional + structural-identity checks; `tables/table_interaction` |
| Δ_persistent − Δ_transient = +0.419 [+0.360,+0.477], excludes 0 | MODEL | audit two-stratum bootstrap difference test |
| Joint-weight sensitivity Δ ∈ [+0.052,+0.471], sign stable >0, magnitude ~9× | MODEL | audit joint grid; `combined_sensitivity.py`; `tables/table_sensitivity` |
| F = uniform over memory × channel factors; estimates conditional on F | ASSUMP | `research/PHASE4_PREREGISTRATION.md`, `..._AMENDMENT_v2.md`; `combined_campaign.c::run_seed` |
| Internal reproducibility (byte-identical reruns; matching hashes) | OBS | manifests `research/results/*/manifest*.json`; audit hash checks |
| No physical/RF/radiation/qualification/causal claim | UNSUP | stated throughout; nothing in artifacts supports otherwise |
| No persistent-storage arm; no second independent KEM; no cross-platform replication | UNSUP | `research/PERSISTENT_STORAGE_BLOCKER.md`; EVIDENCE_LEDGER L12/L13/L23 |
