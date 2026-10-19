# Phase 12 — Claim / Evidence Matrix (for MANUSCRIPT_v2.md)

Status: `VERIFIED` (recomputed from raw / read in code) · `MODEL-CONDITIONAL` (holds under F/model) ·
`INTERPRETIVE` (explanation of why) · `UNSUPPORTED` (not claimed / would need new evidence) ·
`FUTURE WORK`.

| Claim | Status | Evidence | Permitted wording |
|---|---|---|---|
| Phase 2: 900 trials, 750 activated, 600 detected, 0 SDC; 150/250/350/147/3 | VERIFIED | `phase2_mem_logical_v1/raw.jsonl`; `independent_audit.py` | state as measured counts |
| 0-SDC one-sided 95% bound is finite-sample, not zero risk | VERIFIED (framing) | §1/§5 | "no SDC observed in the sampled model; not evidence of zero risk" |
| Phase 2 recovery is structural (logical-value), not persistent recovery | VERIFIED | `poly.c:381`,`tfib_ref.c:93-122` | "structural recovery (recompute from pristine snapshot)" |
| Phase 3: 600 sessions; 7 fault classes + clean; proto/crypto breakdowns | VERIFIED | `phase3_channel_v1/raw.jsonl` (8 distinct `channel_class`) | "seven fault classes plus a clean control" |
| Phase 3 VALID verdict is liboqs-vs-liboqs (not impl-independent) | VERIFIED | `channel_campaign.py:35/41/48` | state per-arm; only SHAKE rejection is independent there |
| Phase 4: 2000 records, 500 matched seeds, 4 conditions | VERIFIED | `phase4_combined_v1/raw.jsonl` | as measured |
| Completion 100/48.0/56.4/26.0% | VERIFIED | fresh recompute | with CIs |
| Δ̂ = +0.216 [+0.180,+0.252] (paired bootstrap over seeds) | MODEL-CONDITIONAL | `combined_stats.py`; audit | "conditional on F/model; not a property of ML-KEM-768" |
| p00 ≡ 1; channel acts before decaps; Δ_transient ≡ 0 by construction | VERIFIED (model-derived) | `combined_campaign.c`; audit max|dᵢ|=0 | present as structural, not discovery |
| Δ magnitude F-dependent (grid [+0.052,+0.471]) | VERIFIED (model) | `combined_sensitivity`; audit | show sensitivity prominently |
| Masking 203/500 = 40.6%; masked completions channel-retry-driven | VERIFIED (count) + INTERPRETIVE | raw `mem_injection_status`,`established` | "non-activation/masking under the execution path; not recovery" |
| Masking = instance of established fault masking/derating | INTERPRETIVE (attributed) | Avizienis 2004; Mukherjee 2003 (metadata-verified) | "an instance of a known concept, not new" |
| Combined arm is cross-implementation (mlkem_native decaps vs liboqs ref) | VERIFIED | `combined_campaign.c:119/211/212/122` | state precisely; no third impl |
| Reproducible: byte-identical datasets, matching hashes, internal audit | VERIFIED | manifests; `independent_audit.py` | "internal audit, not external replication" |
| Persistent-storage mechanism feasible on a `__DATA_CONST` model | VERIFIED | `phase11.../RESULTS.csv` (128/128) | "model prototype only" |
| Persistent-storage on real `mlk_zetas` | FUTURE WORK | `mlk_zetas` in `__TEXT,__const` (SIGBUS); not modified | "not demonstrated; pending approval" |
| Cross-layer design novelty | UNSUPPORTED pending systematic search | Phase 9 (targeted search) | "to our knowledge within the reviewed sources" |
| Radiation / RF / flight resilience | UNSUPPORTED | none | explicitly disclaim |
