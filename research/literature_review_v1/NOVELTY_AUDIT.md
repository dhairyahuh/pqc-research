# Novelty Audit — Phase 6

Classifications: **(1) Strongly differentiated**, **(2) Potentially differentiated — further
searching needed**, **(3) Similar prior work exists — narrow the claim**, **(4) Not a defensible
novelty claim**. Per the brief, "not found in my searches" is treated as (2), never as proof of
originality. This audit is bounded by the non-systematic search (see `SEARCH_LOG.md`); no claim is
rated (1), because establishing strong differentiation requires a systematic review I did not do.

## A. Versioned reproducible fault-classification + evidence-accounting workflow
**Classification: (2) Potentially differentiated — further searching needed.**
Reasoning: fault-campaign frameworks and DOE are broad and long-established; what I did not find is
a *specific* reusable contract that (i) separates injection-status / detection / independent-oracle
verdict / terminal outcome as non-conflatable fields and (ii) makes "recovered" unreachable without
an independent VALID verdict, backed by a ledger + negative tests. Glabush et al. 2025/450 address
detectability of a *faulty FO implementation* by construction, which is adjacent but different (a
protocol-level countermeasure, not an experiment-accounting workflow). Recommended wording: "a
reproducible evidence-accounting workflow for fault experiments on KEMs," not "first/novel."

## B. Software-only logical-value memory-fault campaign for ML-KEM-768 with independent cross-checks
**Classification: (3) Similar prior work exists — narrow the claim.**
Reasoning: fault injection on Kyber/ML-KEM decapsulation (incl. NTT/decoding, FO equality test) is
well studied — Pessl & Prokop (TCHES 2021/064), Xagawa et al. (ASIACRYPT 2021/840), Hermelink et al.
(INDOCRYPT 2021/1222), Ravi et al. survey (2022/737). **Those are adversarial attacks** (physical or
instruction-skip faults aiming at key recovery). Our study is **non-adversarial resilience/
availability measurement** using *logical-value* faults with an independent-oracle resilience
taxonomy and an explicit 0-SDC sampling bound. Narrow to: "a software resilience *measurement* of
ML-KEM-768 under logical-value faults with independent-oracle verdicts," explicitly **not** a new
attack and **not** the first fault study of ML-KEM. Also narrow: recovery is *structural*.

## C. Isolated channel-disruption campaign with separate crypto and protocol outcomes
**Classification: (3) Similar prior work exists — narrow the claim.**
Reasoning: network-impairment emulation (loss/delay/dup/reorder/corruption) is mature (netem;
Jepsen for partitions/crashes). The contribution is the *integration* around ML-KEM with a protocol-
outcome taxonomy kept strictly separate from the cryptographic verdict, plus a *meaningful* (non-
tautological) retry. Narrow to: "an ML-KEM key-establishment protocol emulator that separates
cryptographic verdict from protocol outcome," not a new channel-fault model.

## D. Matched four-condition experiment estimating a model-conditional interaction contrast
**Classification: (2) Potentially differentiated — further searching needed.**
Reasoning: my searches found no matched 2×2 interaction design crossing *in-decapsulation
computation faults* with *channel/protocol faults* on a KEM, with a paired-bootstrap interaction
contrast and distribution-sensitivity. The nearest neighbor, "combined random fault + random
probing" (ePrint 2024/757), crosses physical fault with physical probing — not crypto-computation ×
network. This is promising but unverified-complete; keep as "to our knowledge, within the reviewed
literature" and commission a systematic search before any firmer claim.

## E. The MASKED_BY_CHANNEL mechanism (channel disruption prevents memory-fault activation; not recovery)
**Classification: (2) Potentially differentiated — further searching needed, with a concept caveat.**
Reasoning: the *general* notion of fault masking/derating (one condition preventing another fault
from being activated or observed) is a known dependability concept (e.g., logical/architectural
masking and SDC derating in soft-error literature) — so the *idea* of masking is not new, and I must
not claim it is. **Flag (outstanding):** I did not fetch a specific masking/derating citation this
session; the dependability-masking literature must be reviewed. What appears potentially new is the
*specific instantiation*: a transport/channel fault masking an in-decapsulation computation fault in
an ML-KEM session, and the methodological point that such masking must not be scored as memory-fault
recovery. Recommended wording: "we characterize a channel-masks-computation interaction and caution
against mislabeling it as recovery," explicitly acknowledging masking as a known general concept.

## Overall
No contribution is rated strongly differentiated on the current evidence. The defensible framing is
a **methodology + measurement + a specific cross-layer masking observation**, all software-only and
F-conditional. The strongest originality candidates (D, E) hinge on a systematic cross-layer search
that remains outstanding.
