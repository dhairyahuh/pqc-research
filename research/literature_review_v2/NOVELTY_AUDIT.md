# Novelty Audit v2 — Phase 6B (conservative, with counterevidence)

Classifications: (1) Strongly differentiated · (2) Potentially differentiated — more search needed ·
(3) Similar prior work exists — narrow · (4) Not a defensible novelty claim. No item is rated (1):
search was non-systematic (`SEARCH_LOG.md`), and "not found" is never treated as proof of novelty.
Each contribution lists: **Lit establishes / Experiments establish / Appears differentiated /
Uncertain / Counterevidence / Recommended wording.**

## A. Versioned, reproducible fault-classification + evidence-accounting workflow
**Classification: (3)→(2) narrow.**
- Lit establishes: statistical fault-injection and campaign methodology are mature (Leveugle et al.,
  Statistical Fault Injection; FI-campaign EDA/surveys); dependability defines the outcome concepts
  (Avizienis et al. 2004 — detection, containment, recovery, masking).
- Experiments establish: a concrete contract that separates injection/detection/oracle-verdict/
  outcome and makes RECOVERED unreachable without an independent VALID verdict, with a ledger +
  negative tests.
- Appears differentiated: the *specific* oracle-gated, non-conflating accounting as a reusable
  artifact for KEM fault experiments.
- Uncertain: whether an equivalent contract exists in software-FI tooling I did not enumerate.
- **Counterevidence:** general FI frameworks and statistical-FI already formalize campaigns and
  confidence; the taxonomy of outcomes is Avizienis'. The workflow is an engineering synthesis, not
  a new concept.
- Recommended wording: "a reproducible, independent-oracle-gated evidence-accounting workflow,"
  citing Avizienis (concepts) and statistical-FI (campaign discipline).

## B. Software-only logical-value memory-fault campaign for ML-KEM-768 with independent cross-checks
**Classification: (3) narrow.**
- Lit establishes: extensive fault work on Kyber/ML-KEM decapsulation (Pessl & Prokop; Xagawa et al.;
  Hermelink et al.; Delvaux; Wang et al.; Ravi et al. survey) — including NTT/decoding and the FO check.
- Experiments establish: a non-adversarial *resilience measurement* under logical-value faults with
  independent-oracle verdicts and a 0-SDC sampling bound.
- Appears differentiated: the framing (resilience/availability measurement, not an attack) and the
  independent-oracle resilience taxonomy.
- Uncertain: whether prior resilience-measurement (vs attack) studies on ML-KEM exist that I missed.
- **Counterevidence:** the fault *loci* (NTT, decapsulation, FO) are all previously targeted; this is
  not the first fault study of ML-KEM and not a new attack surface.
- Recommended wording: "a software resilience measurement of ML-KEM-768 under logical-value faults
  (not an attack; recovery is structural)."

## C. Isolated channel-disruption campaign with separate cryptographic and protocol outcomes
**Classification: (3) narrow.**
- Lit establishes: channel-impairment emulation is standard (netem/Hemminger 2005); distributed
  fault testing (Jepsen) injects partitions/crashes/clock-skew with consistency checks.
- Experiments establish: an ML-KEM key-establishment emulator that separates crypto verdict from
  protocol outcome and uses a *meaningful* (channel-redrawing) retry.
- Appears differentiated: the crypto/protocol-verdict separation specific to a KEM session.
- **Counterevidence:** the channel fault classes and retry/timeout semantics are standard networking
  practice; nothing in the channel model itself is new.
- Recommended wording: "an ML-KEM protocol emulator separating cryptographic verdict from protocol
  outcome," citing netem/Jepsen as the impairment lineage.

## D. Matched four-condition experiment estimating a model-conditional interaction contrast
**Classification: (2) potentially differentiated — narrowed.**
- Lit establishes: multiple/combined-fault injection and interaction analysis exist in dependability
  (e.g., single-vs-multiple bit-flip studies; multi-pattern FI); 2^k/interaction designs are textbook.
- Experiments establish: a paired 2×2 (memory × channel) design on an ML-KEM session with an
  interaction contrast Δ, paired bootstrap over seeds, and distribution-sensitivity.
- Appears differentiated: the *specific pairing* of in-decapsulation crypto-computation faults with
  channel/protocol faults, which I did not find in the searched corpus.
- Uncertain: completeness — IEEE Xplore/ACM/DBLP/Scholar not queried as databases.
- **Counterevidence:** combined/interaction fault designs are not new in general (dependability has
  long studied multiple faults); "combined random fault + random probing" (ePrint 2024/757) crosses
  two *physical* fault channels. So the *design pattern* is not novel; only the crypto×channel pairing.
- Recommended wording: "to our knowledge within the reviewed literature, a matched crypto-computation
  × channel-fault interaction design," with the coverage caveat explicit.

## E. The MASKED_BY_CHANNEL observation
**Classification: (3) narrow — it is an application of established fault-masking, NOT a new principle.**
- Lit establishes: **fault masking / error containment** is foundational (Avizienis et al. 2004), and
  **derating / AVF** quantifies the fraction of faults that become user-visible errors (Mukherjee et
  al. 2003). A condition that prevents a fault from activating or being observed is textbook masking.
- Experiments establish: in C11, a delivery-blocking channel fault prevents the memory fault from
  activating in 40.6% of both-fault trials (203/500), and such masked outcomes must not be scored as
  memory-fault recovery.
- Appears differentiated: the *specific cross-layer instantiation* (a transport/channel fault masking
  an in-decapsulation computation fault in a KEM session) and the methodological caution against
  mislabeling masking as recovery.
- **Counterevidence (decisive on the concept):** masking/derating is a well-established dependability
  concept; the *idea* is not new. The novelty, if any, is the setting and the measurement caution.
- Recommended wording: "we observe a cross-layer instance of fault masking (sensu Avizienis;
  cf. derating/AVF, Mukherjee et al.) — a channel fault masking an in-decapsulation computation fault
  — and caution that it must not be scored as recovery." Do **not** present masking as a new mechanism.

## Overall
Conservative position: a **methodology + measurement + a specific cross-layer instance of a known
masking principle**, software-only and F-conditional. B/C/E are applications to be narrowed; A/D are
engineering/design syntheses that are at best "potentially differentiated." No strong-novelty claim
is defensible on current evidence.
