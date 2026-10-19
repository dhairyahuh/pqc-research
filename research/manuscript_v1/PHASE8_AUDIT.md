# Phase 8 — Independent Scientific Integrity Audit (READ-ONLY)

**Role:** skeptical reviewer. **This is an in-repository audit, NOT external replication or peer
review.** No manuscript or existing file was modified; only this file was created. Scripts that are
non-destructive were run; everything else is manual inspection (both are distinguished in §10).

## 1. Executive verdict: **PASS WITH MAJOR CAVEATS**
Every quantitative claim in the manuscript was independently reproduced from the raw records (two
ways: the in-repo `independent_audit.py` and a fresh inline recomputation that imports neither the
campaign nor the audit script). No incorrect number, no fabricated citation, and no first-of-its-kind
or physical/causal overclaim were found. The manuscript's framing is conservative and its
limitations are disclosed. It is **not submission-ready**: the major caveats below (frame-relative
inference, no second independent KEM, logical-value-only memory faults, targeted-not-systematic
literature search, internal-only audit, and a residual six-vs-seven discrepancy in the *source
reports*) are correctly disclosed in the manuscript but materially bound what the paper can claim.

## 2. Method used to verify
- **Executed (this session):** `python3 research/phase2_4_report/audit/independent_audit.py` → exit 0,
  "AUDIT PASSED (0 discrepancies)"; plus a **fresh inline Python recomputation** reading only the raw
  JSONL (independent of both the campaign and the audit script); plus SHA-256 of the three raw files
  vs manifests; plus `grep` provenance of the six-vs-seven wording and the bootstrap unit in
  `combined_stats.py`.
- **Manual inspection (not re-executed here):** `combined_campaign.c`, `combined_stats.py`,
  `fault_contract.h`, `poly.c`, `tfib_ref.c`, `kem.c`, `Makefile`, and the Phase-6B bibliography.

## 3. Recomputed values (fresh inline recomputation; matches manuscript exactly)
- **Hashes:** phase2 `55ab1f57…`, phase3 `2cf7c29b…`, phase4 `d20c0ef5…` — all match manifests.
- **Phase 2:** N=900; activated=750; **SDC=0**; CLEAN 150 / RECOVERED 250 / SAFE_FAIL_DETECTED 350 /
  SAFE_FAIL_FO_CONTAINED 147 / INEFFECTIVE 3. ✓
- **Phase 3:** N=600; proto {EST 100, REC 200, ABORT 50, MALFORMED 100, LOST 100, TIMEOUT 50};
  crypto {VALID 350, REJECT 50, UNAVAILABLE 200}; **distinct `channel_class` = 8 incl CLEAN = 7 fault
  classes** (confirms the manuscript's "seven", and the "six" in the source reports is wrong). ✓
- **Phase 4:** 2000 records; 500 seeds; **0 duplicate (seed,condition)**; all seeds have the 4
  conditions; completion C00 1.000 / C10 0.480 / C01 0.564 / C11 0.260; **Δ=0.216**; masking
  **203/500**; excluded 0; inconclusive 0. ✓
- **Transient-channel structural identity:** stratum n=242, **max|dᵢ|=0**, mean dᵢ=0 — confirmed a
  per-seed identity, not a noisy near-zero. ✓
- **Bootstrap unit:** `combined_stats.py:29,36` resamples over `n = len(seeds)` — the **seed**, the
  correct independent unit. ✓

<!-- P8-APPEND -->
## 4. Findings by category (Critical / Major / Minor)
**No Critical findings** (no incorrect quantitative claim, overclaim, or fabricated citation).

**Audit A — Quantitative correctness.** All counts/denominators/condition-matching verified; no
missing records, no duplicate seeds, exclusions=0, inconclusive=0. *(Minor)* The six-vs-seven
discrepancy is correctly flagged in manuscript §6, but the **source reports still contain the wrong
"six"** (`REPORT.md:56`, `IMPLEMENTATION_LOG.md:94`) — a documentation inconsistency outside the
manuscript.

**Audit B — Statistical interpretation.** *(Major, disclosed)* Inference is **F-conditional**: p/Δ
are Monte-Carlo estimands over a researcher-defined uniform F; the CI is sampling uncertainty over F,
not physical/population uncertainty. The manuscript states this. The paired bootstrap resamples the
correct unit (seed). *(Minor)* The sensitivity statement "sign stable >0" is supported **only across
the tested 3×3 persistence grid** and is explicitly false in the transient stratum (Δ=0); the
manuscript says this. *(Minor)* The transient-stratum "structural identity" is a property of the
specific retry-budget/duration model; it would not necessarily hold under a different protocol
model — the manuscript could state this model-dependence more explicitly.

**Audit C — Cryptographic/experimental validity.** The manuscript correctly distinguishes
logical-value XOR vs physical corruption; structural vs persistent recovery; cryptographic rejection
vs protocol failure; masking vs recovery; oracle agreement vs general correctness; simulated vs real
channel. *(Major, disclosed)* **No second independent KEM** in the channel/combined arms (liboqs is
both KEM and oracle there); oracle agreement therefore is **not** proof of implementation
correctness — stated in §9. FO rejection, independent-oracle construction, and research-vs-production
hook gating match the code (manual inspection: `kem.c`, `independent_oracle.c`, `Makefile`).

**Audit D — Traceability.** See §5 table; every major claim maps to an artifact. No unsupported
quantitative claim found.

**Audit E — Literature/novelty.** The manuscript attributes masking/derating to Avizienis (2004) and
Mukherjee (2003); avoids first-of-its-kind claims; discloses the targeted (non-systematic) search;
tags partial citations ([partial] Leveugle, Sangchoolie) rather than promoting them. *(Major,
disclosed)* A systematic database search (IEEE Xplore/ACM/DBLP/Scholar) is still **not done**; the
cross-layer novelty for contribution D rests on incomplete recall. *(Minor)* Jepsen and liboqs lack
formal peer-reviewed citations (cited as tooling).

**Audit F — Reproducibility/integrity.** Datasets reproduce to recorded hashes; the internal audit
recomputes with 0 discrepancies. *(Major, disclosed)* The audit is **internal**, not external
replication. Git integrity intact (§9... see §8 below).

## 5. Claim-to-evidence table
Classes: **D** directly demonstrated · **MC** model-conditional inference · **A** assumption/design ·
**U** unsupported/needs more.

| Claim (manuscript) | Class | Evidence |
|---|---|---|
| Phase 2: 900 trials, 750 activated, 0 SDC, 600 detected | D | `phase2_mem_logical_v1/raw.jsonl`; fresh recompute + `independent_audit.py` |
| Phase 2 recovery is *structural* (logical-value) | D | code `poly.c:381-408`, `tfib_ref.c:93-122` (manual) |
| Phase 3: 600 sessions; proto/crypto breakdowns; 7 classes | D | `phase3_channel_v1/raw.jsonl`; fresh recompute |
| Phase 4: 2000 recs, 500 matched seeds, 4 conditions | D | `phase4_combined_v1/raw.jsonl`; 0 dup, all-4-conds verified |
| Completion 100/48.0/56.4/26.0% | D | fresh recompute |
| Δ̂ = +0.216 [+0.180,+0.252] | MC | `combined_stats.py` + independent bootstrap; F-conditional |
| Masking 203/500 = 40.6%; masked≠recovery | D (count) / A (interpretation) | raw `mem_injection_status`; status kept separate |
| Δ_persistent +0.419 vs Δ_transient 0 (structural identity) | D (identity) / MC (magnitude) | fresh recompute, max|dᵢ|=0 |
| Masking is an instance of established fault masking | D (attribution) | Avizienis 2004; Mukherjee 2003 (verified in BIBLIOGRAPHY v2) |
| Distribution F uniform; estimates conditional on F | A | `combined_campaign.c::run_seed`; PREREG + AMENDMENT v2 |
| "to our knowledge … new cross-layer pairing" | U (pending systematic search) | NOVELTY_AUDIT v2; SEARCH_LOG v2 |
| 0 SDC ≠ 0 risk | D (framing) | §1/§5 wording; finite-sample bound |
| No physical/RF/radiation/qualification | A (scope) | stated; no artifact claims otherwise |

<!-- P8-APPEND2 -->
## 6. Statistical & experimental validity assessment
- **Interaction contrast** Δ=p11−p10−p01+p00 is defined and computed correctly; p00 is degenerate
  (=1) so Δ is effectively driven by the three faulted conditions — a limitation, correctly noted.
- **Bootstrap** resamples seeds (the independent unit); the four conditions move together per
  resample, preserving pairing — appropriate for the deterministic-per-seed design.
- **Inferential language is justified only within F.** The manuscript consistently qualifies this;
  no population/physical inference is drawn. This is the right call given deterministic generation.
- **Limitations not resolvable from this experiment:** physical fault behaviour; persistent-storage
  resilience; real RF/network/flight performance; cross-platform generality; independence of the KEM
  implementation in the channel/combined arms; and the true (physical) fault distribution — all
  disclosed.

## 7. Inconsistencies / unsupported claims / unavailable artifacts
- **Inconsistency (documentation):** six-vs-seven in `REPORT.md:56` and `IMPLEMENTATION_LOG.md:94`
  vs the data's seven classes. Flagged in-manuscript; the source reports remain inconsistent. (I did
  not edit them — read-only audit.)
- **Partially verified citations:** Leveugle et al. (DATE 2009) and Sangchoolie et al. (TDSC) — not
  confirmed on publisher pages; correctly tagged [partial].
- **Unavailable/other:** no artifact was missing; all referenced raw files, manifests, scripts, and
  the audit script were present and runnable. No claim was found that lacked a traceable artifact,
  except the systematic-search-dependent novelty for contribution D (correctly hedged).

## 8. Action plan
**Required before submission**
1. Run a **systematic literature search** (IEEE Xplore/ACM DL/DBLP/Scholar); confirm or drop the two
   [partial] citations; re-assess the contribution-D cross-layer novelty with full recall.
2. Fix the **six-vs-seven** wording in `REPORT.md` and `IMPLEMENTATION_LOG.md` (or add an erratum)
   so the source reports agree with the data and the manuscript.
3. State the **model-dependence** of the transient-stratum structural identity explicitly.

**Strongly recommended**
4. Add a **second independent KEM** (or a non-liboqs reference) for the channel/combined arms to make
   "independent oracle" independent of the KEM there.
5. **Cross-platform/compiler** replication of all three campaigns.
6. Obtain **external** reproduction (currently the audit is internal only).
7. Motivate or vary **F** (the uniform weighting is arbitrary); report Δ under at least one
   defensible alternative F in the main text, not only the sensitivity grid.

**Future research (beyond this paper's scope)**
8. The **persistent-storage** memory-fault arm (after the reviewed `__DATA_CONST` relocation).
9. Any **physical** fault/radiation/RF validation (explicitly out of scope now).

## 9. Repository integrity check
- Git tracked status **before and after** this audit: identical — the same **7 pre-existing
  modifications** (`README.md`, `experiments/fault_injection/…`, `experiments/system_model/…`,
  `fault_injection/fault_models/…`, `results/phase7i/…`, `results/spacecraft_protocol_desync_results.json`,
  `tests/test_fips_kats.c`); HEAD `4a2c4eb`. No staging, commit, push, reset, clean.
- Only new file created: `research/manuscript_v1/PHASE8_AUDIT.md`. No manuscript/report/data/script
  modified. The audit script run is read-only (writes only to its own stdout; it does not touch
  tracked files or raw artifacts — it re-reads them).

## 10. Checks actually performed (executed vs manual)
**Executed this session:**
- `independent_audit.py` (exit 0, 0 discrepancies).
- Fresh inline Python recomputation of Phase 2/3/4 metrics from raw JSONL (independent of campaign +
  audit script).
- SHA-256 of the three raw datasets vs manifests.
- `grep` provenance of the six-vs-seven wording and of the bootstrap-unit lines in `combined_stats.py`.
- `git status` before and after.

**Manual inspection only (not re-executed in this audit):**
- Source reading of `combined_campaign.c`, `combined_stats.py`, `fault_contract.h`, `poly.c`,
  `tfib_ref.c`, `kem.c`, `Makefile`; the Phase-6B `BIBLIOGRAPHY.md`/`NOVELTY_AUDIT.md`; the manuscript
  and its revision/claims/open-issues files.
- **Not done:** rebuilding/rerunning the C campaigns or KAT suite; any external literature search;
  any external replication. Conclusions about build-time hook gating and FIPS KATs rely on code
  inspection and prior-session runs, not a Phase-8 re-run.

**Verdict reaffirmed: PASS WITH MAJOR CAVEATS** — numbers and framing are sound and honestly scoped;
the paper is a conservative draft, not submission-ready, pending §8 Required items.
