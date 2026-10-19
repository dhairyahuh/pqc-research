# Implementation Log — ML-KEM-768 Space-Resilience Research Extension

Chronological record of meaningful changes, commands, failures, and corrective actions.
Newest last. All work is additive under `research/`; no historical/tracked file was modified
(verified: the 7 pre-existing `M` files predate this work; Step 2C-A CSV SHA-256 unchanged).

## 2026-10-10 — Phase 0 (establish facts)
- Reproduced FIPS-203/204 KATs: `./bin/test_fips_kats` → PASS, exit 0 (prebuilt binary;
  clean rebuild still pending — see EVIDENCE_LEDGER L2).
- Reproduced Step 2C-A campaign byte-for-byte (SHA-256 `97ec6741…`, L5) and its aggregates (L6).
- Verified oracle independence + SHAKE-256 vs hashlib (L3/L4); audited runner/monitor internals
  (L7–L11).
- Feasibility spikes (L12/L13): `vm_protect`+write to `__TEXT,__const` → SIGBUS (exit 138),
  reproduced twice; to `__DATA_CONST` → feasible & reversible (write must use a laundered
  pointer, else `-O2` elides the const store).
- Tool inventory (E1): clang ASAN/UBSAN present; cbmc/frama-c/cppcheck/clang-tidy/afl/Java absent;
  **libFuzzer runtime absent** on this CLT-only clang (discovered in Phase 1, L23).
- Artifacts: `research/EVIDENCE_LEDGER.md`, `research/ARCHITECTURE.md`.

## 2026-10-10 — Phase 1 (fault-model contract + negative tests)
Added `research/fault_contract/`: `fault_contract.h` (schema+taxonomy+classifier+ledger,
header-only), `test_fault_contract.c`, `test_hook_gate.c`, `fuzz_fault_contract.c`,
`run_phase1_tests.sh`. Spec: `research/FAULT_MODEL_SPECIFICATION.md`.

Command: `research/fault_contract/run_phase1_tests.sh` (clang, `-Wall -Wextra -Werror
-Wconversion -Wshadow`, `-fsanitize=address,undefined`). Final: **PASS, overall exit 0**.
- [1/4] 17/17 contract invariants pass under ASAN/UBSAN (exit 0).
- [2/4] hook-gate compiles clean with hooks OFF (exit 0).
- [3/4] hook-gate correctly FAILS to compile with `-DMLKEM_RESEARCH_FAULT_HOOKS` (gate works).
- [4/4] robustness fuzz: 500,000 deterministic malformed records, no ASAN/UBSAN violation.

Failures encountered and fixed during Phase 1:
1. `2> >(flt)` process substitution → `/dev/fd/*` "Operation not permitted" under the sandbox.
   Fix: redirect compiler stderr to a log file and filter the file (no process substitution).
2. `-fsanitize=fuzzer` link error — `libclang_rt.fuzzer_osx.a` not shipped with Command-Line-
   Tools clang. Fix (honest alternative, per directive): dual front-end fuzz harness; falls back
   to a self-contained deterministic xorshift driver under ASAN/UBSAN. libFuzzer path retained
   for environments that have the runtime. Limitation recorded (L23).
3. **UBSAN caught a real contract defect**: reading `bool` struct fields populated from arbitrary
   fuzz bytes = "load of value N not valid for type 'bool'" (UB). Fix: all serialized flags are
   now `uint8_t` compared `!=0`, so byte-deserialized records are well-defined (L22). Re-ran: clean.
4. Taxonomy refinement: split `SAFE_FAIL` into `SAFE_FAIL_DETECTED` vs `SAFE_FAIL_FO_CONTAINED`
   so local-checker detection and downstream FO containment are never conflated (preserves the
   147-vs-350 Step 2C-A distinction). Updated classifier/tests; re-ran clean.

## Next (Phase 2, dependency-ready)
Memory-fault campaign on the contract, matched baseline/TFIB-Ref/TFIB-Meta, honest labels per
the migration table. Do NOT start the spatial campaign (separate 2C-B redesign). Audit & reuse
`experiments/system_model/spacecraft_protocol_sim.py` before any Phase-3 channel work.

## 2026-10-10 — Phase 2 (logical-value memory-fault arm) — COMPLETE
Added `research/fault_contract/{mem_campaign.c,compare_and_stats.py,run_phase2.sh}`,
`research/EXPERIMENTAL_PROTOCOL.md` (pre-registration, frozen before confirmatory),
`research/PERSISTENT_STORAGE_BLOCKER.md`; extended `fault_contract.h` with `fc_trial_consistent()`
+ tests. New dataset: `research/results/phase2_mem_logical_v1/{raw.jsonl,pilot.jsonl,
comparison_stats.md,manifest.json}`. No historical/tracked file modified.

Design decision: did NOT fork/modify the historical `tfib_experiment_runner.c`. Built a parallel
runner reusing the identical crypto path + deterministic inputs, emitting v1 records classified
by `fc_classify()` — so the historical CSV/binary stay as the reproducibility anchor.

Commands & results (via `research/fault_contract/run_phase2.sh`):
- Phase 1 re-run (added consistency tests): PASS, exit 0.
- Build (`clang -O3 -std=c11 -Wall -Wextra` + tfib/oracle libs + liboqs): OK (cosmetic dylib
  version warning only).
- Pilot (5/suite=90): ledger 90/90, inconsistent 0; inspected per-trial records; byte-identical
  across two runs.
- Confirmatory (50/suite=900): ledger 900/900, inconsistent 0, INCONCLUSIVE 0.
- Reproducibility (G5): two runs byte-identical, raw.jsonl SHA `55ab1f57…`.
- Matched baseline (G4) + mapping: 0/900 crypto/alignment mismatches, 0 migration mismatches.
- Stats: detection among activated 600/750 (Wilson 95% CI [0.770,0.827]); SDC 0/750, 97.5%
  one-sided upper bound 0.491%.
All exit criteria gates G1–G5 PASS. Persistent-storage arm BLOCKED (documented).

Claims supported: the v1 contract integrates without changing real decapsulation behavior; the
historical results re-express exactly under the honest taxonomy (detected-fail-stop vs
FO-contained kept distinct). Claims NOT supported: persistent-storage recovery, physical/
radiation effects, zero SDC risk, any statistically significant superiority (design is
near-deterministic; descriptive only).

## Next (Phase 3, dependency-ready — not started)
Audit & reuse `experiments/system_model/spacecraft_protocol_sim.py` (read-only first); define a
protocol-outcome verdict separate from the ML-KEM oracle; keep channel faults separately
identifiable from memory faults; combined faults only after both isolated arms validate.

## 2026-10-10 — Phase 3 (channel-fault arm) — COMPLETE
Gate 0 audit (`research/PHASE3_PROTOCOL_AUDIT.md`): existing sim UNSUITABLE as-is (tautological
retry → SESSION_RECOVERED 1000/1000 in its committed output; only 1/6 fault classes;
non-replayable randomized KEM; no ledger). Not modified; preserved for traceability.
Gate 1 spec (`research/PROTOCOL_FAULT_MODEL_SPEC.md` v1): protocol outcome taxonomy separate from
crypto verdict; explicit precedence (timeout≠crypto-failure; crypto-reject≠timeout); state machine,
framing, meaningful-retry policy, timeout semantics; newly-introduced assumptions flagged.
Gate 2 harness (`research/channel_harness/channel_campaign.py`): deterministic ML-KEM via liboqs
`*_derand` (ctypes) + independent SHAKE-256 rejection check; 7 channel-fault classes (bit,
truncation, loss, delay/timeout, duplication, reorder, interruption) × transient/persistent + a
clean baseline (8 distinct `channel_class` values);
retries redraw the channel so recovery is genuine.
Gate 3 (`test_channel_contract.py`, `run_phase3.sh`): invariant tests PASS; pilot 60; confirmatory
600 (12×50), ledger balanced, 0 INCONCLUSIVE; reproducible (raw.jsonl SHA `2cf7c29b…`).

Commands: `research/channel_harness/run_phase3.sh` → PHASE 3 DRIVER: PASS (exit 0). Fixed a
manifest `working_tree_dirty` shell-quoting bug (reported false; now correctly true). A Gate-3
test was initially too strict (assumed MALFORMED ⇒ no decaps); corrected after confirming the
harness is right — REORDER legitimately yields crypto VALID + protocol MALFORMED (layer
separation), which the test now asserts positively.

Claims supported: a deterministic, fully-accounted channel/protocol emulator with meaningful
retry and strict protocol/crypto separation; recovery (200/600) is genuine channel clearing, not
tautology. NOT supported: real radio-link/radiation/space claims; statistical significance;
duplication/reorder realism beyond the abstract seq-window model.

## Phase 4 (combined faults) — dependencies BEFORE authorization
1. Phase 2 (memory, logical-value) validated ✓; Phase 3 (channel) validated ✓ — both isolated
   arms pass with separate, non-conflated taxonomies.
2. Define the interaction estimand in advance: Δ = p11 − p10 − p01 + p00 on a binary completion
   endpoint, pre-registered with CI method and multiplicity handling.
3. A combined schema that keeps memory-fault class and channel-fault class independently
   identifiable in every record (no merging of the two taxonomies).
4. Pilot + frozen confirmatory; honest handling of the near-deterministic structure (descriptive,
   not significance-claimed) unless a genuinely stochastic design is introduced.
Not started; awaiting authorization.

## 2026-10-10 — Phase 4 (combined faults) — audit→pre-reg→pilot DONE; confirmatory GATED
Gate 0 (`PHASE4_IDENTIFIABILITY_REVIEW.md`): revalidated Phase 2/3 (hashes match manifests).
Key obstacle: the two arms use different ML-KEM impls (C mlkem_native+TFIB vs Python liboqs) with
different fault loci → a valid combined trial needs ONE decaps path. Built the coordinator on the
C `mlkem768_dec_monitored` path with a channel+protocol layer; liboqs+SHAKE stay the oracle.
Gate 1 (`PHASE4_PREREGISTRATION.md`): binary endpoint (key established within retry budget), four
paired conditions, Δ=p11−p10−p01+p00, unit=seed, bootstrap-over-seeds CI, fixed N (pilot 20,
confirmatory 500), complete-case exclusions, frame-relative interpretation.
Gate 2 (design review): Δ identifiable ONLY as a Monte-Carlo estimand over a researcher-defined
fault distribution F; replays are repeatability, not independent obs; CIs are frame-relative, not
physical. If F rejected → descriptive only.
Gate 3 (`research/combined_harness/combined_campaign.c`): versioned combined schema with memory
and channel dimensions kept separate (mem_locus/duration/armed/activated/detected/injection_status
vs channel_class/persistent/armed/effect), crypto verdict, protocol outcome, endpoint, retry,
exclusions, provenance. Precedence enforced (non-delivery → timeout → malformed → crypto); a
channel fault is never relabeled a memory fault, a crypto reject never a timeout.
Gate 4 (`run_phase4_pilot.sh`): pilot 20×4=80, build -Werror clean, 0 INCONCLUSIVE, reproducible
(`pilot.jsonl` SHA `d6fc82f5…`). **Pilot found a real defect**: the first exclusion rule discarded
C11 cases where the channel blocked delivery so the memory fault could not activate — but that is a
legitimate channel-masks-memory interaction. Fixed → retained as `MASKED_BY_CHANNEL` (9/20 of C11),
exclusions now 0. Frozen analysis `combined_stats.py` (paired bootstrap over seeds).
Pilot (DESCRIPTIVE, n=20): p00 100%, p10 40%, p01 50%, p11 20%, Δ̂ +0.30.

STOP: confirmatory (500 seeds) NOT run — awaiting design-review sign-off per the mandatory gate.
Claims so far: a valid single-path combined harness with separated dimensions and a meaningful
masking interaction exists and is reproducible. NOT claimed: any confirmatory Δ, significance,
physical/RF/radiation/qualification meaning. Memory faults remain logical-value (persistent BLOCKED).

## 2026-10-10 — Phase 4 design-review v2 + Gate 5 CONFIRMATORY — COMPLETE
v2 amendment (`PHASE4_PREREGISTRATION_AMENDMENT_v2.md`, v1 preserved): primary claim = masking
mechanism; secondary = F-conditional Δ; joint-distribution sensitivity + masking-vs-recovery
separation added; `combined_stats.py` enriched; `combined_sensitivity.py` added; pilot re-run PASS.
Gate 5 (`run_phase4_confirmatory.sh`): recorded frozen-input hashes BEFORE execution; built -Werror;
ran 500 seeds×4=2000 trials → `raw.jsonl` (SHA `d20c0ef5…`), 0 inconclusive/excluded/dropped,
reproducible; ran frozen analysis + joint sensitivity; manifest `manifest_confirmatory.json`.
NO deviation from the frozen protocol/analysis after seeing outcomes.
Results: p00 100% / p10 48.0% / p01 56.4% / p11 26.0%; Δ̂ +0.216 [+0.180,+0.252]; conditional
channel-PERSISTENT +0.419 vs channel-TRANSIENT +0.000; masking 40.6% (203/500), masked≠recovered.
Primary (masking) SUPPORTED; secondary (F-conditional Δ>0) SUPPORTED as frame-relative; no
physical/causal claim. Phases 0–5 of the extension are complete within the authorized software scope.
