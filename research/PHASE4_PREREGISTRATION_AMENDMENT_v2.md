# Phase 4 — Pre-registration AMENDMENT v2 (design-review revision)

Amends `PHASE4_PREREGISTRATION.md` (v1, **preserved unchanged**) BEFORE any confirmatory data.
No confirmatory run exists. Supersedes v1 only where stated; all else in v1 stands.
Companion exploratory evidence: 1000-seed temp draw (not persisted, not the 500-seed confirmatory).

## A. Primary claim (predefined) — supersedes v1's single-contrast framing
- **PRIMARY (mechanism):** *Under F, a delivery-blocking channel fault masks the memory fault
  (prevents it from reaching activation), yielding sub-additive combined session failure.* The
  interaction is **concentrated in persistent/blocking-channel scenarios and is ~0 when the
  channel fault is transient** (exploratory: conditional Δ = +0.39 for channel-PERSISTENT vs
  **+0.00** for channel-TRANSIENT; pilot: +0.60 vs +0.00). Supported by the masking accounting
  (§B) and the conditional-Δ strata.
- **SECONDARY (F-conditional average interaction):** Δ = p11−p10−p01+p00 as a Monte-Carlo
  estimand under F, with paired bootstrap CI, reported **together with its joint-weight
  sensitivity** (§C). Magnitude is explicitly F-dependent.
- We will **NOT** claim the interaction sign is *generally* robust. We will state only that Δ>0
  across the tested joint-weighting family (§C) AND that it is **zero in the transient-channel
  stratum**, so positivity is conditional on F placing mass on blocking/persistent channel faults.
- No causal or physical-probability claim. Frame-relative throughout.

## B. Masking vs recovery (new, mandatory reporting) — supersedes v1 reporting
`MASKED_BY_CHANNEL` is reported as a **distinct** memory-injection status, separate from
ACTIVATED / detected / recovered / safe-fail. A memory fault that never reaches its activation
point is **not** a recovered memory fault.
- **Masking-rate denominator = |C11| paired seeds** (memory armed AND channel armed). Masking
  rate = #MASKED_BY_CHANNEL / |C11|. (Masking cannot occur in C10, whose channel is clean.)
- **Endpoint contribution:** a masked trial's session-completion is governed by the **channel
  retry**, not by memory recovery — if the blocking channel fault was transient a clean retry may
  establish; if persistent it does not. Exploratory: established-among-MASKED = 126/423 vs
  established-among-ACTIVATED = 137/577 — different populations, reported separately. Masked
  completions are never attributed to the memory countermeasure.

## C. Joint-distribution sensitivity (new requirement) — exploratory results
Reweighting P(mem_duration=PERSISTENT)=wm and P(channel_persistent)=wc jointly over
{0.25,0.5,0.75}² (2×2 strata, coverage 227–281 seeds/cell, n=1000):

```
            wc=0.25  wc=0.50  wc=0.75
  wm=0.25   +0.051   +0.103   +0.154
  wm=0.50   +0.103   +0.206   +0.309
  wm=0.75   +0.154   +0.309   +0.463
```
Δ range over the joint grid: **[+0.052, +0.463]** — sign stable >0 across this family, magnitude
~9×. Conditional Δ: channel-PERSISTENT +0.39 (n=536), channel-TRANSIENT **+0.00** (n=464);
by config BASELINE/REF/META +0.20/+0.22/+0.21; blocking vs non-blocking channel +0.24/+0.17.
Tested ranges and the finding "sign does not change within this family, but vanishes in the
transient-channel stratum" are the pre-registered sensitivity statement. The confirmatory report
will reproduce this grid on the frozen 500-seed run.

<!-- AMEND-APPEND -->
## D. Estimand & uncertainty justification (why the paired bootstrap is valid here)
- **Matched scenario per seed:** all four conditions for seed `i` share the SAME drawn
  (keypair, message, F_mem params, F_chan params); only which faults are *active* is toggled
  (verified in `combined_campaign.c::run_seed` — one draw, four `run_condition` calls).
- **Seed = the independent sampling unit:** distinct seeds are i.i.d. draws from F; outcomes are
  deterministic given the seed's scenario, so the ONLY randomness is the across-seed draw. Hence
  the correct resampling unit is the seed, and the number of independent observations = number of
  distinct seeds (NOT replays, which are byte-identical and add no information — verified).
- **Why paired bootstrap:** because the four conditions are deterministic functions of the same
  seed, resampling seeds with replacement and recomputing all four condition means together
  propagates exactly the sampling variability of F into Δ, preserving the within-seed correlation.
  This is the appropriate (and only valid) uncertainty for Δ under this scheme. Ordinary binomial
  CIs treating condition-trials as independent are NOT used.
- **Inference is explicitly conditional on F.** p and Δ are properties of F; CIs quantify
  Monte-Carlo sampling uncertainty over F only.

## E. Freeze & audit trail
- v1 pre-registration preserved unchanged; this v2 amendment is recorded BEFORE confirmatory data.
- Analysis code revised to report masking + conditional strata (`combined_stats.py`) and the joint
  sensitivity (`combined_sensitivity.py`); pilot re-run after the change — PASS, 0 inconclusive,
  reproducible (`pilot.jsonl` SHA `d6fc82f5…`), pilot mechanism matches exploratory (conditional Δ
  PERSISTENT +0.60 / TRANSIENT +0.00).
- Confirmatory remains the UNRUN frozen 500-seed campaign → `raw.jsonl` (absent). No confirmatory
  data will be collected until explicit Gate-5 authorization.

