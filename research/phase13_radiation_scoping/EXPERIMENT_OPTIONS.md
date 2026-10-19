# Phase 13 — Experiment Options (A–E), evaluated, not implemented

| Option | Scientific value | Feasibility (now) | New assumptions | Validation burden | Misinterpretation risk | What it could actually establish |
|---|---|---|---|---|---|---|
| **A.** Continue logical-value campaign with a more explicit software fault model | Low–Med (incremental) | High (software only) | Few | Low | Med — may look like "radiation" if not caged | A better-specified *software* model; **no** physical bridge |
| **B.** Approved `mlk_zetas` relocation + real persistent-storage arm | **Med–High** | Med (needs approval + disassembly; mechanism already shown feasible in `__DATA_CONST`, Phase 11) | Moderate (research-only relocation; verify codegen) | Med | Med — must not call it an SEU | Behavior under *genuine backing-store* corruption; the closest-yet software analogue; prerequisite for any device mapping |
| **C.** Memory/register-oriented injection model from published device/architecture evidence | High (first real step toward grounding) | **Low now** (needs a named device + its data + AVF-style mapping) | Many (device, structure residency, multiplicity, derating) | High | High if device data is thin | A device-grounded fault distribution — only if evidence exists |
| **D.** External hardware/radiation-testing collaboration for physical validation | **Highest** (only path to physical claims) | **Not feasible now** (no equipment/collaborator/device) | Many | Very High | High if extrapolated across devices | Actual device upset→software-error behavior under irradiation |
| **E.** Keep the paper strictly software-only; radiation mapping as a separate scoping/future-work | High (prevents overclaim) | High | None | Low | Low | Honest boundaries + a documented mapping/gap analysis (this phase) |

## Recommended staged path
**E now → B next → C only after securing device evidence → D for eventual physical validation.**
- **Now (E):** publish/review the current study as **software-only**, folding this scoping analysis
  into a future-work/limitations section (or a short separate scoping note). Do **not** attach a
  radiation claim.
- **Next defensible software experiment (B):** the approved persistent-storage arm. It is the most
  defensible increment because it replaces structural logical-value recovery with genuine
  backing-store corruption, and it is the natural substrate a later device mapping would target. It
  still must be labelled a *software* fault, **not** an SEU.
- **C/D are evidence-gated:** C requires a named target device and its measured upset data + an
  AVF/derating mapping for the ML-KEM workload; D requires beam/alpha access and collaborators. Do
  not pursue either until those prerequisites exist. No single experiment can establish radiation
  resilience.
