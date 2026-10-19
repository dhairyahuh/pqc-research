# Phase 4 — Design review & identifiability (Gates 0 & 2)

Decision gate. Must pass before any combined-fault confirmatory run. Companion:
PHASE4_PREREGISTRATION.md (Gate 1). Priority: identifiability and honesty over a result.

## Gate 0 — baseline revalidation (reproduced)
Reran both drivers; `raw.jsonl` byte-identical to recorded manifests:
- Phase 2 (`run_phase2.sh`): PASS; raw.jsonl SHA `55ab1f57…` (matches manifest).
- Phase 3 (`run_phase3.sh`): PASS; raw.jsonl SHA `2cf7c29b…` (matches manifest).
- Historical files untouched (7 pre-existing `M` only).

## Gate 0 — the central obstacle to a valid combined experiment
The two isolated arms are **not directly composable**:
- **Memory arm (Phase 2):** C `mlkem768_dec_monitored` (in-tree `mlkem_native` + TFIB hooks);
  fault = logical-value XOR of an NTT butterfly value *inside* decapsulation.
- **Channel arm (Phase 3):** Python + **liboqs**; fault = corruption/loss/… of the *wire*
  ciphertext, decapsulated by liboqs (no fault hooks).
These are **different ML-KEM implementations** and **different fault loci**. Naively combining
the two harnesses is invalid (two different decaps). A valid combined trial needs **one
decapsulation path carrying both faults**. Only the C path has memory-fault hooks, so the Phase-4
coordinator MUST be built on the C `mlkem768_dec_monitored` path, adding a channel + protocol
layer on the wire ciphertext around it. liboqs + standalone SHAKE remain the **independent
oracle** (as in Phase 2). The isolated runners are NOT modified.

## Gate 2 — can the design identify the interaction? (required review)
Both fault models are **deterministic given their seed/params** → replaying the same trial is
**repeatability, not independent observation**. Ordinary binomial CIs over replays would be
invalid (as the directive warns). Therefore:

### The sampling frame F (explicit, researcher-defined — NOT physical)
A trial = one draw indexed by seed `i`:
- keypair + message: derived deterministically from `i` (`*_derand` + PRF).
- memory-fault params `~ F_mem`: config ∈ {BASELINE, TFIB_REF, TFIB_META} (uniform); locus ∈
  {OP_TWIDDLE, REF_TWIDDLE, META_TAG, CHECKER_LOGIC} (uniform, REF/META only where applicable);
  duration ∈ {TRANSIENT, PERSISTENT} (uniform); butterfly `=(i*17)%128`; bit `=(i%15)+1`.
- channel-fault params `~ F_chan`: class ∈ {BIT_CORRUPTION, TRUNCATION, PACKET_LOSS, DELAY,
  DUPLICATION, REORDER, INTERRUPTION} (uniform); persistence ∈ {TRANSIENT, PERSISTENT} (uniform).
`p_xy = P_F[ key established within retry budget | condition xy ]`. **N = number of DISTINCT
seeds = number of i.i.d. Monte-Carlo draws from F.** Re-running the whole campaign at the same
master seed is byte-identical and adds **zero** information.

### What the numbers mean (stated plainly)
`p_xy` and `Δ` are properties of **F, a distribution we define**, not of physical fault rates.
CIs quantify **Monte-Carlo sampling uncertainty over F**, nothing more. Change F → change the
numbers. This is legitimate *only* with F pre-registered and reported as frame-relative.

### Paired design & uncertainty for Δ itself
Each seed `i` is evaluated under all four conditions on the SAME draw (faults toggled on/off),
yielding `(y00,y10,y01,y11)_i`. Per-seed interaction `d_i = y11 - y10 - y01 + y00`;
`Δ̂ = mean_i d_i`. **Uncertainty = nonparametric bootstrap over the N seeds** (resample seeds,
recompute Δ̂, 95% percentile interval) — this gives the interaction contrast's OWN uncertainty
and respects pairing. We do NOT infer interaction from "one pair significant, another not."
Note `p00 ≡ 1` (clean always establishes) → degenerate, zero-variance; Δ remains estimable.

### Identifiability decision
**IDENTIFIABLE as a Monte-Carlo estimand over the pre-registered F**, with a bootstrap CI over
distinct seeds — PROVIDED N distinct seeds are used (not replays) and claims stay frame-relative.
**NOT identifiable as a physical probability or a universal/causal effect.** If F is not accepted
as a meaningful sampling frame, the deliverable degrades to **descriptive scenario coverage**
(report per-condition counts and Δ̂ as a point description, no inferential claim). We will report
Δ̂ with its bootstrap CI AND explicitly label it frame-relative; we will not make significance or
causal claims beyond F. If the pilot shows the four conditions are (near-)deterministic constants
under F (so Δ̂ has negligible bootstrap variance and is just an arithmetic fact of the scenario
mix), we will say so and present it descriptively rather than dressing it as inference.
