# Phase 12 — Final Review Checklist & Unresolved Questions

## Verdict for the revised manuscript (MANUSCRIPT_v2.md)
**Suitable only for another internal review, not yet for external submission.** The numbers,
framing, independence description, and limitations are now accurate and conservative, but the
scientific contribution remains modest (methodology + a largely-structural, F-conditional interaction)
and several external-evidence gaps remain open.

## Pre-submission checklist
- [x] All quantitative claims recomputed from raw (independent_audit) — 0 discrepancies.
- [x] Δ framed as model-conditional; structural drivers (p00≡1, pre-decaps channel, transient≡0) stated.
- [x] Masking framed as non-activation, explicitly not recovery; attributed to prior art.
- [x] Per-arm KEM/oracle independence corrected (channel-only = liboqs both sides; combined = cross-impl).
- [x] Persistent-storage described per Phase 11 (model only; real table unmodified; future work).
- [x] Robustness driver clarified as not coverage-guided fuzzing.
- [x] Targeted-not-systematic literature disclosure retained; no metadata→full-text upgrades.
- [x] In-text citations map to §13; no invented citations/DOIs.
- [x] Original + backups preserved; raw/manifests/SUT unchanged.
- [ ] **Systematic literature search** (IEEE Xplore/ACM DL/SpringerLink/USENIX/Scholar/DBLP).
- [ ] **Full-text** reading of key cited works (currently metadata-only).
- [ ] A **physically motivated or alternative F** reported in the main text (not only the grid).
- [ ] **Real persistent-storage arm** (needs approved `mlk_zetas` relocation + disassembly) — or keep as future work.
- [ ] **Cross-platform/compiler** replication.
- [ ] **External** reproduction by an independent party.
- [ ] Clean rebuild of campaign objects from source (vs prebuilt `.o`).

## Unresolved questions (candid)
1. Is the interaction anything more than definitional once the structural drivers are removed? A
   reviewer may argue not. The honest position: the value is the methodology + accounting, not a
   general mechanism.
2. Does a comparable interaction appear when both faults genuinely perturb the computation (real
   persistent-storage memory fault)? Unknown — requires the future arm.
3. Cross-layer *pairing* novelty: unresolved pending a systematic search.
4. Does relocating `mlk_zetas` to `__DATA_CONST` change codegen enough to confound a future real
   persistent-storage arm? Must be checked by disassembly before trusting results.

## Recommended next step
Internal review of MANUSCRIPT_v2.md focused on whether the contribution clears a venue's bar as a
*methodology/measurement* paper; in parallel, scope the systematic literature search (closes the
largest open item) before deciding on submission vs. the real persistent-storage arm.
