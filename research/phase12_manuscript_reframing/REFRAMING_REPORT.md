# Phase 12 — Reframing Report (WP2)

Revised manuscript: `research/manuscript_v1/MANUSCRIPT_v2.md` (SHA-256 `755356d9…`). Original
`MANUSCRIPT.md` (`0e37903d…`) and backups (`MANUSCRIPT.pre_phase7/9/12.bak.md`) preserved; raw data,
manifests, SUT, and prior reports unchanged.

## Verification method
Phase 1–4 numbers were **independently recomputed from the raw JSONL** by
`research/phase2_4_report/audit/independent_audit.py` this phase (AUDIT PASSED, 0 discrepancies) — not
merely checked against summaries. Per-arm crypto architecture was read directly from
`channel_campaign.py` (lines 35/41/48: liboqs keygen/encaps/decaps) and `combined_campaign.c`
(line 119 `mlkem768_dec_monitored` = mlkem_native; 211/212 liboqs; 122 standalone SHAKE).

## Material findings (verified)
- Numbers confirmed: Phase 2 (900/750/600/0-SDC; 150/250/350/147/3); Phase 3 (600; proto
  EST100/REC200/ABORT50/MALF100/LOST100/TIMEOUT50; crypto 350/50/200; **7 fault classes + clean**);
  Phase 4 (2000/500 matched; 100/48.0/56.4/26.0%; Δ̂ +0.216 [+0.180,+0.252]; masking 203/500;
  Δ_persist +0.419 vs Δ_transient 0 (max|dᵢ|=0); grid [+0.052,+0.471]).
- **Correction (important):** the prior claim "liboqs serves as both the channel/combined KEM and the
  oracle" is wrong for the **combined** arm — there the decapsulation under test is **mlkem_native**
  and liboqs supplies the reference, so the VALID verdict is cross-implementation. It is correct only
  for the **channel-only** arm (liboqs on both sides). v2 states independence **per arm**.
- **Confirmed structural drivers of Δ (per Phase 10):** p00≡1; channel applied before decapsulation
  (so delivery-blocking faults prevent memory-fault activation); Δ_transient≡0 by construction;
  Δ magnitude F-dependent (~9×). v2 presents these as model-derived, not empirical discoveries.
- **Phase 11:** the `__DATA_CONST` **model** prototype demonstrated corruption/consumption/restoration
  (128/128); the real `mlk_zetas` (`__TEXT,__const`) was **not** modified and no real persistent-
  storage campaign ran. v2 describes it as future work pending approval, not completed.

## Major framing changes in v2
1. Abstract + §8: interaction labelled **largely structural/model-conditional**, with a four-level
   claim split (observed / model-derived / interpretive / hypothesis); Δ̂ not presented as a property
   of ML-KEM-768.
2. §7/§9/§10(iv): **per-arm** KEM/oracle independence stated precisely (channel-only arm's VALID
   verdict is liboqs-vs-liboqs; combined arm is cross-implementation; no third implementation).
3. §10(i)/§12: persistent-storage described exactly per Phase 11 (model only; real table unchanged;
   future work pending approval + disassembly verification).
4. §10(v): clarified the robustness check is a deterministic ASAN/UBSAN driver, **not** coverage-
   guided fuzzing.
5. Masking consistently framed as **non-activation/masking**, explicitly **not** recovery/fault-
   correction/evidence-of-harmlessness; attributed to Avizienis 2004 / Mukherjee 2003.

## Title / "resilience"
The title ("Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment: A Reproducible Software
Study") **does not** use "resilience" and is adequately scoped; no rename needed. Body uses of
"resilience measurement" were retained only where they denote *measuring outcomes* (availability/
safe-fail), not withstanding real corruption; the structural/model-conditional caveats now bound them.

## Remaining concerns (not resolved here)
- The central empirical content is thin (methodology + structural interaction); a reviewer may still
  find the interaction largely definitional. v2 is honest about this but cannot manufacture novelty.
- Systematic literature search still outstanding (Phase 9); novelty for the cross-layer *pairing*
  remains OPEN.
- No real persistent-storage, physical, cross-platform, or external-replication evidence.
