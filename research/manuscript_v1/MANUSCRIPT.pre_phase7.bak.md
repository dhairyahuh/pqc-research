# Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software Study

**Draft v1 — conservative first draft, NOT a claim of publication readiness.** All quantitative
values are taken from the audited repository artifacts (see `CLAIMS_AND_EVIDENCE.md`); none are
invented. The study is **software-only**: it makes no claim of physical radiation tolerance,
electromagnetic/RF-link performance, persistent-storage resilience, flight qualification, or
general causal behaviour.

## 1. Abstract
We study how two classes of software-modelled faults — *logical-value* memory corruption during
ML-KEM-768 decapsulation and *channel* disturbances to the transmitted ciphertext/frame — affect
the correctness, safe-failure, and availability of a small key-establishment protocol, and how the
two classes **interact**. Using one real reference decapsulation path instrumented for both fault
classes, an independent correctness oracle (liboqs + a standalone SHAKE-256 rejection-key
recomputation), and a versioned fault contract that separates injection, detection, oracle verdict,
and terminal outcome, we run three campaigns: an isolated memory campaign (900 trials), an isolated
channel campaign (600 sessions), and a matched four-condition combined campaign (500 seeds × 4 =
2000 records). The combined campaign estimates a positive interaction contrast
Δ̂ = p11 − p10 − p01 + p00 = **+0.216** (paired-bootstrap 95% CI [+0.180, +0.252]) on a binary
session-completion endpoint, **conditional on a researcher-defined fault distribution F**. We show
this interaction is driven by a **masking mechanism**: a delivery-blocking channel fault prevents
the memory fault from ever activating in **40.6% (203/500)** of both-fault trials; masking is
explicitly *not* memory-fault recovery. The interaction is concentrated in persistent/blocking
channels (conditional Δ = +0.419 [+0.360, +0.477]) and is a per-seed structural identity of exactly
zero for transient channels. We report an internal reproducibility audit (not an external
replication). Zero silent data corruptions were observed in the memory campaign; we do **not**
interpret this as zero risk.

## 2. Introduction and research questions
Cryptographic software for constrained/space-oriented systems should fail safely when computation
or integrity checks are disturbed. We investigate a narrow, software-defensible question rather than
physical fault tolerance. Research questions:
- **RQ1 (memory).** Under a logical-value memory-fault model during decapsulation, how do detection,
  recovery, safe-failure, and end-to-end rejection behave, and is any silent data corruption
  observed in the sampled model?
- **RQ2 (channel).** Under a software channel model around ML-KEM key establishment, how are protocol
  outcomes (completion, malformed, loss, timeout, abort, retry-recovery) distributed, kept distinct
  from the cryptographic verdict?
- **RQ3 (interaction).** When both fault classes act on the same decapsulation, is there an
  interaction on session completion, what is its sign and mechanism, and how does it depend on the
  assumed fault distribution F?

## 3. Related work (verifiable sources only; comparative literature OUTSTANDING)
We use and cite only sources verifiable from the repository/environment:
- **FIPS 203 (ML-KEM)** — the standard the implementation under test targets (referenced throughout
  the in-tree sources). Exact citation string to be verified.
- **mlkem_native reference implementation** — the in-tree ML-KEM used as the system under test
  (`algorithms/source_ref/mlkem/`).
- **liboqs (Open Quantum Safe), version 0.16.0** — the independent oracle backend (version read at
  runtime from the installed library).
- **FIPS 202 (SHA-3/SHAKE)** — the XOF used for the independent rejection-key recomputation and the
  deterministic PRF.

> **OUTSTANDING:** a systematic literature review of PQC fault-injection and cross-layer
> fault studies, and verification of full bibliographic metadata, has **not** been performed in this
> draft and must be completed before submission (see `OPEN_ISSUES.md`). We make no novelty claim
> relative to unreviewed prior work.

<!-- MS-APPEND -->
## 4. Experimental methodology
**System under test (SUT).** The mlkem_native reference ML-KEM-768 with real Fujisaki–Okamoto
decapsulation; research fault hooks are compiled only under `-DMLKEM_RESEARCH_FAULT_HOOKS` and are
absent from clean/KAT builds (Makefile-verified). FIPS-203/204 known-answer tests pass.

**Independent oracle.** liboqs 0.16.0 supplies derandomized keygen/encaps/decaps; a standalone
SHAKE-256 recomputes the FIPS-203 implicit-rejection key J(z‖c). The oracle is independent of the
SUT's monitor and is used to assign the cryptographic verdict VALID / REJECT / NEITHER. The SHAKE
implementation was checked against Python `hashlib` on empty, "abc", a 200-byte (multi-block
absorb) and a 170-byte (multi-block squeeze) vector.

**Fault contract.** A versioned schema (`fault_contract.h`) records, as *separate* fields:
injection status (NOT_ARMED / INELIGIBLE / FAILED / ACTIVATED), monitor detection, oracle verdict,
and terminal outcome. The classifier makes RECOVERED reachable **only** when the oracle verdict is
VALID; a monitor's self-reported recovery is never sufficient. A ledger requires every scheduled
trial to be finalized exactly once.

**Determinism and sampling.** All inputs derive from SHAKE-256 PRFs keyed by a seed; distinct seeds
are independent draws, and re-running at the same seed is byte-identical (verified by SHA-256), so
replays add no information. "Memory faults" here are logical-value: a local copy of an NTT value is
XORed; the constant tables are never written. Consequently any "recovery" is **structural**
(recompute from a pristine snapshot/untouched reference) and must not be read as recovery from
persistent-storage corruption.

## 5. Phase 2: Logical-value memory fault campaign
Design: 18 suites × 50 = **900 trials** across BASELINE / TFIB-REF / TFIB-META and operational-
twiddle / reference-table / metadata-tag / checker-logic loci, transient and persistent. Each armed
trial XORs a local NTT value during the real decapsulation.
Results (recomputed from raw): **750 activated** faults; **600/750 locally detected**; terminal
outcomes CLEAN_COMPLETED 150, RECOVERED 250, SAFE_FAIL_DETECTED 350, SAFE_FAIL_FO_CONTAINED 147,
INEFFECTIVE 3; **0 silent data corruption**. We do not interpret 0/750 SDC as zero risk; it is a
finite-sample observation under this model. RECOVERED here is structural (see §4) — not persistent-
memory recovery.

## 6. Phase 3: Isolated channel fault campaign
Design: a deterministic protocol/channel emulator with an explicit state machine, an 18-byte frame,
a SHAKE-keyed tag, retry budget 2, and a logical delivery deadline. Retries **redraw** the channel,
so recovery is meaningful (not tautological). **12 suites × 50 = 600 sessions.** The channel fault
classes present in the data are **seven** — BIT_CORRUPTION, TRUNCATION, PACKET_LOSS, DELAY,
DUPLICATION, REORDER, INTERRUPTION — plus a CLEAN baseline (8 distinct `channel_class` values).
> **Discrepancy flagged (not resolved):** two prose artifacts say "six fault classes" while listing
> seven (`research/phase2_4_report/REPORT.md:56`, `research/IMPLEMENTATION_LOG.md:94`). The data and
> the specification enumerate seven. This draft uses the data-grounded count of **seven**; see
> `OPEN_ISSUES.md`.
Results (recomputed): protocol outcomes KEY_ESTABLISHED 100, RECOVERED_ON_RETRY 200,
MALFORMED_MESSAGE 100, MESSAGE_LOST 100, TIMEOUT_RETRY_EXHAUSTED 50, PROTOCOL_ABORT 50; cryptographic
verdict (separate dimension) VALID 350, REJECT 50, UNAVAILABLE 200. By construction a timeout/loss
carries no cryptographic verdict (no decapsulation), and a cryptographic rejection is never recorded
as a timeout.

## 7. Phase 4: Matched combined-fault experiment
**Why one path.** The isolated memory arm uses the C mlkem_native+hooks path; the isolated channel
arm used liboqs. These are different implementations, so a valid combined trial requires a **single**
decapsulation path carrying both faults. The coordinator therefore applies the channel fault to the
wire ciphertext *before* calling the instrumented `mlkem768_dec_monitored`, inside which the memory
fault acts. liboqs + SHAKE remain the independent oracle.
**Four matched conditions** per seed, evaluated on the *same* drawn scenario with faults toggled:
C00 (neither), C10 (memory only), C01 (channel only), C11 (both). **500 seeds × 4 = 2000 records.**
**Interaction contrast** Δ = p11 − p10 − p01 + p00 on the binary endpoint *key established within the
retry budget*. A **positive** Δ means the combined failure is **sub-additive** — the two faults
overlap/mask rather than add — because under this endpoint higher p = more completion.
**Distribution F** (assumed, researcher-defined): uniform over memory (config/locus/duration) ×
channel (class/persistence). All p and Δ are properties of F; they are Monte-Carlo estimands, not
physical probabilities.
<!-- MS-APPEND2 -->
## 8. Results and statistical analysis
**Per-condition completion** (N=500, paired-bootstrap 95% CI): p00 = 100.0%, p10 = 48.0%
[43.6, 52.4], p01 = 56.4% [52.0, 60.8], p11 = 26.0% [22.2, 30.0]. (p00 is degenerate at 1.)
**Interaction:** Δ̂ = **+0.216**, paired-bootstrap 95% CI **[+0.180, +0.252]**.

**Estimand and uncertainty.** The seed is the independent sampling unit; the four conditions share
one matched scenario (one draw, faults toggled), so uncertainty uses a **paired bootstrap over
seeds** (resample seeds, recompute all four condition means together, 10 000 resamples, percentile
interval). An independently written auditor reproduced the CI as [+0.180, +0.252]. Ordinary
binomial intervals over condition-trials are *not* used, because repeated deterministic replays are
not independent observations.

**Masking mechanism (primary).** In C11, memory injection status is ACTIVATED 297 vs
MASKED_BY_CHANNEL 203, i.e. a masking rate of **203/500 = 40.6%** (denominator = the matched both-
fault condition). A masked trial is one where the channel blocked delivery so the memory fault never
reached its activation point; its session may still complete via a clean retry. Masked completions
(57/203) are therefore **channel-retry-driven and are not memory-fault recoveries**; activated
completions were 73/297. Masking is reported as a distinct status, never folded into
detected/recovered/safe-fail.

**Conditional interaction and the persistent-vs-transient difference.** Stratifying by channel
persistence: Δ_persistent = +0.419 [+0.360, +0.477] (n=258) vs Δ_transient = +0.000 (n=242). The
transient value is not a noisy near-zero: the per-seed interaction d_i is **identically 0** for
every transient-channel seed (max|d_i| = 0) — a structural identity, since a transient channel
clears on retry and the combined outcome equals the memory-only outcome. The difference
Δ_persistent − Δ_transient = +0.419 with a two-stratum bootstrap 95% CI [+0.360, +0.477] that
**excludes 0**; we therefore do not infer the difference merely from "one estimate positive, one
zero."

**Sensitivity to F.** Reweighting P(memory persistent) × P(channel persistent) jointly over the grid
{0.25, 0.50, 0.75}² (2×2 strata, ≥111 seeds/cell) yields Δ ∈ [+0.052, +0.471]: the **sign is stable
> 0 across the tested grid, but the magnitude varies ~9×**. We do **not** claim the estimate is
distribution-independent; outside the tested grid, and in particular in the transient-channel
stratum, the interaction can be zero.

Figures/tables (regenerated from the raw data by `make_figures.py`) are in
`research/phase2_4_report/figures/` and `.../tables/`.

## 9. Threats to validity
Determinism implies the CIs quantify Monte-Carlo sampling over the researcher-defined F, not
physical uncertainty; F's uniform weights are a modelling choice and the magnitude of Δ depends on
them. liboqs serves as both the channel/combined KEM and the oracle, so there is **no second
independent KEM** in those arms; the independent check is the SHAKE rejection recomputation plus the
protocol specification. The protocol is abstract (not CCSDS/ECSS); "time" is logical. Memory
"recovery" is structural (logical-value faults). p00 is degenerate. Single platform/compiler.

## 10. Limitations and scope
Explicitly disclosed: (i) **no validated persistent-storage memory-fault arm** — it is blocked
because writing the operational table's `__TEXT,__const` page faults (SIGBUS) on the test platform,
and is feasible only after a reviewed relocation to `__DATA_CONST`; (ii) **no physical radiation,
EM, glitch, or hardware experiments**; (iii) **no cross-platform/compiler replication**; (iv) **no
second independent KEM** in the combined experiment; (v) coverage-guided fuzzing used a deterministic
ASAN/UBSAN driver because the libFuzzer runtime was unavailable; (vi) earlier Step 2C-A timing/
overhead figures are not reproduced here. The study establishes none of radiation hardness, physical
isolation, RF performance, flight qualification, or universal causal behaviour.

## 11. Reproducibility and artifact availability
All three datasets reproduce byte-identically from their drivers and match recorded SHA-256 hashes
(`run_phase2.sh`, `run_phase3.sh`, `run_phase4_confirmatory.sh`; manifests under
`research/results/*/`). An **internal** audit (`research/phase2_4_report/audit/independent_audit.py`,
freshly written, not importing the campaign code) re-verified the hashes and recomputed every key
metric with 0 discrepancies. This is an internal reproducibility audit — **not** an external
replication or peer review. Exact commands, expected outputs, and hashes are in `REPRODUCIBILITY.md`.

## 12. Conclusion
Within an explicitly software-only, F-conditional frame, combined memory and channel faults interact
sub-additively on session completion, and the mechanism is channel masking of the memory fault
(40.6% of both-fault trials), concentrated in persistent/blocking channels and structurally absent
for transient ones. The contribution is a reproducible methodology (fault contract, independent
oracle, matched combined design, internal audit) plus a mechanistically precise, honestly scoped
interaction finding. It is a first draft: the comparative literature review, a physically motivated
F, the persistent-storage arm, a second independent KEM, and cross-platform replication remain to be
done before any stronger or publication-level claim.

