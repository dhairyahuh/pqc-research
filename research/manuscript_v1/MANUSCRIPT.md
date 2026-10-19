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
session-completion endpoint, **conditional on a researcher-defined fault distribution F**. We find
this interaction is an instance of **fault masking** — an established dependability concept
(Avizienis et al. 2004; cf. derating/AVF, Mukherjee et al. 2003), not a mechanism we invent: a
delivery-blocking channel fault prevents the memory fault from ever activating in **40.6%
(203/500)** of both-fault trials. Masking here is explicitly *not* memory-fault recovery. The
interaction is concentrated in persistent/blocking channels (conditional Δ = +0.419 [+0.360,
+0.477]) and is a per-seed structural identity of exactly zero for transient channels. We report an
internal reproducibility audit (not an external replication), and our literature search was targeted
rather than systematic. Zero silent data corruptions were observed in the memory campaign; we do
**not** interpret this as zero risk.

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

### Contributions (conservatively stated)
We claim no first-of-its-kind result and no contribution is claimed novel merely because our
targeted search did not find a match. Our contributions are:
1. a reproducible, versioned **evidence-accounting workflow** for KEM fault experiments, in which
   detection/recovery/safe-fail are credited only against an independent oracle (building on the
   dependability outcome concepts of Avizienis et al. 2004 and statistical fault-injection practice);
2. a software **logical-value** memory-fault *resilience measurement* of ML-KEM-768 (a measurement,
   not an attack; the fault loci are those already studied adversarially by prior work);
3. an ML-KEM protocol emulator that **separates the cryptographic verdict from the protocol
   outcome** using standard network-impairment mechanisms (not a new channel model);
4. a **matched four-condition design** estimating a model-conditional interaction contrast between
   memory and channel faults — to our knowledge within the reviewed (non-systematic) literature a new
   crypto×channel pairing, though combined/interaction fault designs are themselves not new; and
5. the observation that, in this model, a channel fault **masks** the memory fault — an instance of
   established fault masking/derating (Avizienis et al. 2004; Mukherjee et al. 2003), reported with
   the caution that masking must not be scored as recovery.

## 3. Related work
This review is **targeted, not systematic**: it rests on a web search plus direct fetches of
authoritative hosts (IACR ePrint, NIST CSRC, author-hosted PDFs); IEEE Xplore, ACM DL, DBLP, and
Google Scholar were **not** queried as databases, so recall is incomplete and broader searches
remain outstanding (see `../literature_review_v2/SEARCH_LOG.md`). Every citation below maps to a
verified entry in §13; all cited items now carry Crossref- or host-verified bibliographic metadata
(the two methodology items previously marked *partial* were resolved in Phase 9).

**Fault attacks on lattice KEMs.** Precisely placed faults can break the CCA security of
Fujisaki–Okamoto (FO) based lattice KEMs: a single instruction-skip in the decapsulation decoding
step (Pessl and Prokop 2021), skipping the FO equality test (Xagawa et al. 2021), a ciphertext
bit-flip with a corrective fault that turns FO into a failure oracle (Hermelink et al. 2021),
extensions to masked Kyber (Delvaux 2022), and loop-abort faults in Keccak across all phases of
ML-KEM/ML-DSA (Wang et al. 2024, preprint); Ravi et al. (2022, preprint) survey the area. These are
**adversarial** attacks aimed at key recovery. Our study (as we interpret the contrast) differs in
intent and model: it *measures* resilience and availability under *logical-value* software faults
rather than mounting an attack, and does not extend this attack line.

**Defending the FO check.** Because the FO re-encryption/equality check is security-critical but not
functionally necessary, a faulty implementation can silently omit it; Glabush et al. (2025) propose
*verifiable decapsulation*, binding the check to functionality, motivated by a real HQC
implementation that omitted re-encryption unnoticed for 19 months. Our work is complementary and
operational: detection and recovery are credited only against an independent oracle.

**Dependability: masking and derating.** The fault→error→failure model and the notions of *masking*
and *error containment* are foundational (Avizienis et al. 2004), and *derating* / architectural-
vulnerability-factor analysis quantifies the fraction of faults that become user-visible errors
(Mukherjee et al. 2003). We rely on this directly: the outcome we label `MASKED_BY_CHANNEL` is a
cross-layer **instance** of established masking/derating, not a new mechanism.

**Network/protocol disruption.** Channel-impairment emulation — loss, delay, duplication,
reordering, corruption — is standard (Hemminger 2005), and distributed-systems fault testing such as
Jepsen injects partitions, crashes, and clock skew. We reuse these impairment *mechanisms* in a
deterministic in-process emulator around ML-KEM, separating the cryptographic verdict from the
protocol outcome and using a retry that redraws the channel so recovery is not tautological; the
channel model itself is not new.

**Combined and cross-layer faults.** Combined-fault formalisms exist for *physical fault × physical
probing* (ePrint 2024/757), dependability has long studied *multiple faults* (e.g. single-vs-multiple
bit-flip studies; Sangchoolie et al. 2022), and cross-layer post-quantum analyses consider
per-layer algorithm vulnerability (arXiv:2604.08480, preprint). Within the reviewed literature we did
not find a matched experiment crossing in-decapsulation crypto-computation faults with channel/
protocol faults on a KEM; we therefore present our combined design as, *to our knowledge within the
reviewed sources*, a new cross-layer pairing, while noting that combined/interaction fault designs
are not themselves new and that our search was not systematic.

> **OUTSTANDING before submission:** a systematic database search (IEEE Xplore/ACM DL/DBLP/Scholar)
> to settle the cross-layer novelty question; a reviewer should also confirm the Crossref-verified
> metadata against full texts; and the open issues in
> `OPEN_ISSUES.md` remain. No novelty claim here is to be read as established against unreviewed prior work.

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
> **Discrepancy (corrected in Phase 9):** two prose artifacts previously said "six fault classes"
> while listing seven (`research/phase2_4_report/REPORT.md`, `research/IMPLEMENTATION_LOG.md`); both
> were corrected to **seven fault classes + a clean control** to agree with the data and the
> specification (the raw records were not altered). This draft uses the data-grounded count of
> **seven**; see `OPEN_ISSUES.md` and `../phase9_literature_validation/CHANGELOG.md`.
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
clears on retry and the combined outcome equals the memory-only outcome. This identity is
**conditional on the fault model, transient-duration semantics, protocol implementation, and retry
budget**, and is not a general theorem about transient channel faults. The difference
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
overhead figures are not reproduced here; and (vii) the **literature search is targeted, not
systematic** — no IEEE Xplore/ACM DL/DBLP/Scholar database queries — with the items in
`OPEN_ISSUES.md` outstanding. (The two methodology citations previously marked unresolved —
Leveugle et al., DATE 2009; Sangchoolie et al., IEEE TDSC 2022 — were resolved to verified
bibliographic metadata via Crossref in Phase 9; full texts were not read.) The study establishes
none of radiation hardness, physical isolation, RF performance, flight qualification, or universal
causal behaviour.

## 11. Reproducibility and artifact availability
All three datasets reproduce byte-identically from their drivers and match recorded SHA-256 hashes
(`run_phase2.sh`, `run_phase3.sh`, `run_phase4_confirmatory.sh`; manifests under
`research/results/*/`). An **internal** audit (`research/phase2_4_report/audit/independent_audit.py`,
freshly written, not importing the campaign code) re-verified the hashes and recomputed every key
metric with 0 discrepancies. This is an internal reproducibility audit — **not** an external
replication or peer review. Exact commands, expected outputs, and hashes are in `REPRODUCIBILITY.md`.

## 12. Conclusion
Within an explicitly software-only, F-conditional frame, combined memory and channel faults interact
sub-additively on session completion. The mechanism is an **instance of established fault masking**
(Avizienis et al. 2004; derating/AVF, Mukherjee et al. 2003) — a channel fault masks the memory
fault (40.6% of both-fault trials) — concentrated in persistent/blocking channels and structurally
absent for transient ones; masking is not recovery. The contribution is a reproducible methodology
(fault contract, independent oracle, matched combined design, internal audit) plus a
mechanistically precise, honestly scoped interaction observation. It is a first draft, and we make
no first-of-its-kind claim: a systematic literature review, a physically motivated F, the
persistent-storage arm, a second independent KEM, and cross-platform replication remain to be done
before any stronger or publication-level claim.

## 13. References (verified; see `../literature_review_v2/BIBLIOGRAPHY.md` for status tags)
Verification key: [Vf] host page fetched & confirmed; [Vl] confirmed from authoritative host
listing/record; [tool] software/standard; [pre] preprint; [partial] not confirmed on publisher page.

1. [Vf] NIST. *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard.* 2024-08-14.
   https://csrc.nist.gov/pubs/fips/203/final
2. [tool] NIST. *FIPS 202: SHA-3 Standard (incl. SHAKE).* 2015.
3. [tool] Open Quantum Safe, *liboqs* v0.16.0. https://openquantumsafe.org
4. [tool] *mlkem_native* reference ML-KEM (in-tree SUT, `algorithms/source_ref/mlkem/`).
5. [Vf] P. Pessl, L. Prokop. "Fault Attacks on CCA-secure Lattice KEMs." *IACR TCHES* 2021(2):37–60.
   DOI 10.46586/tches.v2021.i2.37-60; ePrint 2021/064.
6. [Vf] J. Hermelink, P. Pessl, T. Pöppelmann. "Fault-enabled chosen-ciphertext attacks on Kyber."
   *INDOCRYPT 2021*; ePrint 2021/1222.
7. [Vf] K. Xagawa, A. Ito, R. Ueno, J. Takahashi, N. Homma. "Fault-Injection Attacks against NIST's
   PQC Round 3 KEM Candidates." *ASIACRYPT 2021*; ePrint 2021/840.
8. [Vl] J. Delvaux. "Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber." *IACR
   TCHES 2022*; ePrint 2021/1622.
9. [Vf,pre] Y. Wang, J. Yu, S. Qu, X. Zhang, X. Li, C. Zhang, D. Gu. "Mind the Faulty Keccak: A
   Practical Fault Injection Attack Scheme Apply to All Phases of ML-KEM and ML-DSA." ePrint 2024/1522.
10. [Vf,pre] P. Ravi, A. Chattopadhyay, J. P. D'Anvers, A. Baksi. "Side-channel and Fault-injection
    attacks over Lattice-based Post-quantum Schemes (Kyber, Dilithium): Survey and New Results."
    ePrint 2022/737.
11. [Vf] L. Glabush, F. Günther, K. Hövelmanns, D. Stebila. "Verifiable Decapsulation: Recognizing
    Faulty Implementations of Post-Quantum KEMs." *CRYPTO 2025*; ePrint 2025/450.
12. [Vf] A. Avizienis, J.-C. Laprie, B. Randell, C. Landwehr. "Basic Concepts and Taxonomy of
    Dependable and Secure Computing." *IEEE Trans. Dependable and Secure Computing* 1(1):11–33, 2004.
    DOI 10.1109/TDSC.2004.2 (Crossref-verified).
13. [Vl] S. S. Mukherjee, C. Weaver, J. Emer, S. K. Reinhardt, T. Austin. "A Systematic Methodology
    to Compute the Architectural Vulnerability Factors for a High-Performance Microprocessor."
    *MICRO-36*, 2003, pp. 29–40. DOI 10.1109/MICRO.2003.1253181 (Crossref-verified).
14. [Vl] S. Hemminger. "Network Emulation with NetEm." *Linux Conf Au*, April 2005.
15. [tool] Jepsen (K. Kingsbury) — distributed-systems fault testing. https://jepsen.io
16. [Vl] "Formal Definition and Verification for Combined Random Fault and Random Probing Security."
    ePrint 2024/757.
17. [pre] "Post-Quantum Cryptographic Analysis of Message Transformations Across the Network Stack."
    arXiv:2604.08480 (2026).
18. [Vl] R. Leveugle, A. Calvez, P. Maistri, P. Vanhauwaert. "Statistical Fault Injection: Quantified
    Error and Confidence." *DATE 2009*, pp. 502–506. DOI 10.1109/DATE.2009.5090716 (Crossref-verified
    metadata; full text not read).
19. [Vl] B. Sangchoolie, K. Pattabiraman, J. Karlsson. "An Empirical Study of the Impact of Single
    and Multiple Bit-Flip Errors in Programs." *IEEE Trans. Dependable and Secure Computing*
    19(3):1988–2006, 2022. DOI 10.1109/TDSC.2020.3043023 (Crossref-verified metadata; full text not
    read).

