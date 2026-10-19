# Phase 12 — Changelog (MANUSCRIPT.md → MANUSCRIPT_v2.md)

New file: `research/manuscript_v1/MANUSCRIPT_v2.md` (`755356d9…`). Source `MANUSCRIPT.md`
(`0e37903d…`) unchanged. Backup `MANUSCRIPT.pre_phase12.bak.md` (`0e37903d…`). Phase 7/9 backups
untouched. No result number changed (verified by grep of result tokens; only wording/structure).

| Section | Change | Why | Status of change |
|---|---|---|---|
| §1 Abstract | Added "largely structural and model-conditional (p00≡1; channel before decaps; transient≡0 by construction); magnitude depends on F; not a property of ML-KEM-768" | Stop implying Δ is a system property | narrows claim |
| §7 (Phase 4) | Replaced "liboqs + SHAKE remain the independent oracle" with **per-arm** precise architecture (combined = mlkem_native decaps vs liboqs ref = cross-impl; channel-only = liboqs both sides) | Correct an inaccurate independence description | correctness fix |
| §8 Results | Added "Interpretation — structural/model-conditional" paragraph with the four-level claim split (observed / model-derived / interpretive / hypothesis) | Separate empirical from constructed; address Phase 10 | narrows/clarifies |
| §9 Threats | Rewrote the KEM/oracle-independence sentence to be **per-arm**; "no *third* independent KEM" | Correctness; was conflated | correctness fix |
| §10 Limitations (i) | Persistent-storage described per Phase 11 (model prototype only; real `mlk_zetas` unchanged in `__TEXT,__const`; future work pending approval + disassembly) | Match Phase 11 exactly; not "blocked"/"completed" | correctness fix |
| §10 (iv) | "no *third* independent KEM"; channel-only arm liboqs both sides | Align with §7/§9 correction | correctness fix |
| §10 (v) | Clarified the robustness driver is **not** coverage-guided fuzzing | Phase 1 limitation precision | clarification |
| §12 Conclusion | "largely structural, model-conditional … not a general property"; per-arm-qualified independent checks; persistent-storage not demonstrated on real SUT | Consistency with §8/§10 | narrows claim |

## Not changed
Title (already precise; no "resilience"); all counts, CIs, denominators, hashes; the seven-class
statement (already corrected in Phase 9); the targeted-not-systematic literature disclosure; §13
references.
