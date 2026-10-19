# Phase 4 — Pre-registration (Gate 1), frozen before confirmatory

Consistent with PHASE4_IDENTIFIABILITY_REVIEW.md. Frozen before any confirmatory data.
`COMBINED_SCHEMA_VERSION = 1`.

## Primary endpoint (binary, unambiguous)
`established = 1` iff the combined session reaches `KEY_ESTABLISHED` or `RECOVERED_ON_RETRY`
(the receiver obtained the correct shared secret — crypto verdict VALID — AND the telecommand
frame parsed) within the retry budget `RETRY_MAX = 2`; else `0`.

## Conditions (paired per seed; faults toggled on the SAME draw)
- `p00`: no memory fault, clean channel.
- `p10`: memory fault only (params ~ F_mem).
- `p01`: channel fault only (params ~ F_chan).
- `p11`: both.
Interaction contrast: **Δ = p11 − p10 − p01 + p00** (sub-/super-additivity of the two arms).

## Population, unit, sampling frame
Population = modeled trials under the pre-registered distribution **F** (F_mem × F_chan, defined
in the identifiability review). Unit of analysis = **the seed**, evaluated under all four
conditions (paired). **N = number of DISTINCT seeds = i.i.d. Monte-Carlo draws from F.** Replays
at the same master seed are byte-identical and contribute no information. `p_xy`/`Δ` are
properties of F (Monte-Carlo estimands), explicitly NOT physical fault probabilities.

## Analysis & uncertainty (frozen)
- `Δ̂ = mean_i (y11−y10−y01+y00)_i`; **95% CI by nonparametric bootstrap over seeds**, B = 10000,
  percentile method (`research/combined_harness/combined_stats.py`, frozen before confirmatory).
- Marginal `p_xy` reported with numerator/denominator and bootstrap (and Wilson, secondary) CIs.
- `p00` is expected degenerate (=1); reported as such.
- The bootstrap interval for Δ IS the interaction's own uncertainty; interaction is NOT inferred
  from "one pairwise difference significant, another not."

## Multiplicity
Exactly ONE primary contrast (Δ). Marginals/pairwise differences are secondary & descriptive →
no primary-test multiplicity inflation. No per-suite significance testing.

## Stopping rules
Fixed, pre-specified sizes; NO adaptive peeking or data-dependent stopping.
Pilot: `N_pilot = 20` seeds (×4 = 80 trials). Confirmatory: `N_conf = 500` seeds (×4 = 2000
trials). N chosen for bootstrap-CI stability over F, NOT as a power calc against a physical effect
(which would be meaningless for a researcher-defined F).

## Exclusion criteria (complete-case pairing)
A condition-trial is excluded if it is `INCONCLUSIVE` (harness/invariant error) or if an injection
that was supposed to be active is `INELIGIBLE`/`FAILED`. If ANY of a seed's four conditions is
excluded, the whole seed is dropped from the paired Δ analysis; the dropped-seed count is reported.
All trials (including excluded/ineligible/failed) are retained in the ledger — nothing dropped
silently.

## Event ordering / precedence (for the schema & classifier)
Channel acts on the wire ciphertext BEFORE decapsulation; the memory fault acts DURING
decapsulation. Terminal-outcome precedence (per attempt): non-delivery (loss/interruption) →
missed-deadline (delay→timeout) → malformed/parse failure → crypto verdict (VALID→established;
REJECT→mismatch→retry/abort; NEITHER→flagged silent-accept). A memory-induced implicit rejection
and a channel-induced implicit rejection are BOTH crypto REJECT, but the record keeps
`mem_activated`/`mem_detected` and `channel_effect` as SEPARATE fields — a channel fault is never
relabeled a memory fault, and a crypto rejection is never relabeled a timeout.

## Interpretation limits
Frame-relative, descriptive emphasis. No statistical-significance or causal claim beyond F.
Combined **logical-value** memory faults + **simulated** channel faults do NOT establish
persistent-storage resilience, physical radiation tolerance, real RF-link performance, or
spacecraft qualification. Memory faults remain logical-value only (persistent-storage arm BLOCKED).
