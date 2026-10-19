# Evidence Ledger — ML-KEM-768 Space-Resilience Research

Single source of truth for what is **actually established** in this checkout, versus what is
merely reported by prior agents. Every row carries an evidence status. Do not promote a row
to REPRODUCED/VERIFIED without recording the command and artifact that justifies it.

## Evidence taxonomy
- **VERIFIED** — directly inspected in source/binary this session.
- **REPRODUCED** — an experiment/test was re-run successfully here (command + artifact recorded).
- **REPORTED** — appears in a prior agent report; NOT independently reproduced here.
- **PROPOSED** — intended experiment/hypothesis, not yet evaluated.
- **FORMALLY VERIFIED** — documented proof or precisely-scoped formal-tool result.
- **EMPIRICALLY OBSERVED** — observed in a specific finite experiment (sampling bound applies).
- **PHYSICALLY VALIDATED** — measured on real relevant hardware. (NONE in this project.)
- **UNKNOWN** — insufficient evidence.

## Shared environment (E0)
- Host: Apple Silicon **arm64** (M1 / T8103), Darwin 27.0.0; **16 KiB** page size.
- Toolchain: Apple clang 21.0.0; Python 3.9.6 (scipy 1.13.1, numpy 2.0.2).
- Oracle backend: **liboqs 0.16.0** (/opt/homebrew), used via `*_derand` entry points.
- Repo: branch `space-resilience-framework`; working tree dirty with large unrelated untracked
  work (phases 2–18, `paper/`, many CSVs) — all preserved, nothing reset.
- Date established: 2026-10-10.

## Assurance tooling actually available (E1) — VERIFIED
- Present: clang **ASAN/UBSAN** (compile probe OK), clang **libFuzzer** (`-fsanitize=fuzzer`,
  built into clang), strict warnings, `nm`/`otool`, Python+scipy for statistics.
- **Absent**: cbmc, frama-c, cppcheck, clang-tidy, scan-build, infer, afl, valgrind, Java
  (so no TLA+/TLC without installing Java+tla2tools). Installing any of these = external
  resource / network action → requires user authorization before use.

---

## Ledger

### L1 — Historical commits exist — VERIFIED
Claim: SHAs `c1bfb15`, `4a2c4eb`, `673190d` (Step 2C-A), `55dd937` (phase17) exist here.
Method: `git cat-file -t`. Scope: identity only, says nothing about correctness of their content.

### L2 — FIPS 203/204 KATs pass — REPRODUCED (partial)
Claim: ML-KEM-512/768/1024 and ML-DSA-44/65/87 KATs (incl. tamper-reject) pass.
Method: `./bin/test_fips_kats` → "ALL ... VERIFIED SUCCESSFULLY", exit 0.
Artifact: stdout; source `tests/test_fips_kats.c` + `tests/kat_mlkem768.c` etc.
Scope/limit: ran the **prebuilt** binary; `tests/test_fips_kats.c` is modified in the working
tree, so the binary may not match current source. NEXT: clean `make test_fips_kats` rebuild and
re-run to upgrade this to a full REPRODUCED under recorded build flags.

### L3 — Independent oracle is third-party and correct — VERIFIED + REPRODUCED
Claim: oracle = liboqs 0.16.0 (keygen/encaps/decaps) + standalone SHAKE-256 for FO rejection;
independent of the in-tree ML-KEM under test.
Method: read `phase11_oracle/independent_oracle.c/.h`; ran `./test_independent_oracle` → 6/6
groups PASS (KAT, canonical implicit rejection, negative, boundary).
Scope/limit: trusts liboqs as reference; the embedded KAT "expected" vectors are trusted as NIST.

### L4 — Standalone SHAKE-256 correct — VERIFIED
Claim: `fips202_ref.c` SHAKE-256 matches the standard.
Method: compiled a harness, compared 4 vectors (empty, "abc", 200 B input [multi-block absorb],
170 B output [multi-block squeeze]) against Python `hashlib.shake_256` → all exact.

### L5 — Step 2C-A campaign is deterministic & byte-reproducible — REPRODUCED
Claim: `tfib_experiment_runner` reproduces the committed CSV exactly.
Method: re-ran binary to a temp path; `diff` empty; SHA-256 identical =
`97ec674171e365d3ffca45821f13c7da316ada00135b889fde9036a0c9cff7e9`
for both the re-run and `tfib_experiments/phase2_step2c_trial_results.csv`.
Scope/limit: ran the existing binary, not a clean rebuild; determinism of liboqs `*_derand`
internals not inspected. Determinism of inputs is via SHAKE-256 PRF (`campaign_prf.h`).

### L6 — Step 2C-A aggregate counts — REPRODUCED (from CSV)
Claim/values (recomputed over 900 rows): 900 trials = 150 BASELINE + 400 TFIB_REF + 350
TFIB_META; fault_activated **750**, monitor_detected **600**, recovered **250**,
SAFE_FAIL_STOP **350**, LOCAL_BLIND_FO_CONTAINED **147**, INEFFECTIVE_FAULT_VALID **3**,
SDC **0**. Internally consistent (output_correct 403 + implicit_rejection 497 = 900).
Scope/limit: the raw `implicit_rejection` column (497) merges 350 detected-fail-stop + 147
FO-contained; use `outcome_class`, not that column, for any claim.

### L7 — All Step 2C-A injection is SYMBOLIC (local copies); const tables never mutated — VERIFIED
Method: `poly.c:381-408` (operand snapshot u_saved/v_saved taken BEFORE the fault hook at :388;
hook mutates a local `zeta_val`); `tfib_hooks.c:158-164`; `tfib_ref.c:49-61` (REF/SIMULTANEOUS
faults XOR a local `zeta_ref`); `tfib_meta.c`; both tables are `const` (`tfib_ref.c:5`,
`tfib_meta.c:4`) and are never written. Confirmed by subagent audit + my spot-checks.

### L8 — Recovery is tautological by construction — VERIFIED
Claim: on detection, operands are restored from pristine pre-fault snapshots and the repair
re-reads an untouched reference table (`tfib_ref.c:93-122`, repair at :98); persistent faults
can never count as recovered (:104-122, gated on `!persistent`). So `GENUINE_RECOVERY` (250)
demonstrates recompute-from-pristine-inputs, NOT recovery from real persistent memory corruption.
Interpretation limit — do NOT claim recovery from persistent corruption.

### L9 — Monitor couples into the FO decision — VERIFIED
Claim: `kem.c:486-494` forces `fail=0xFF` (implicit rejection) whenever the monitor's persistent
count > 0, bypassing the genuine dual-rail re-encryption check. So `SAFE_FAIL_STOP` for
persistent faults is partly the monitor acting on its own state. NUANCE: the 147
LOCAL_BLIND_FO_CONTAINED cases have `mon_det=false` ⇒ persistent count 0 ⇒ override does NOT
fire ⇒ their rejection is the genuine real-path FO re-encryption. The headline FO-containment
result survives; the fail-stop count is partly an artifact.

### L10 — SDC classification uses two independent oracles — VERIFIED
Claim: `runner.c:103-134`: `ss_match` vs liboqs valid-SS, `rej_match` vs standalone-SHAKE
rejection-SS; `SDC = !ss_match && !rej_match`. The 147/3 split (LOCAL_BLIND_FO_CONTAINED vs
INEFFECTIVE_FAULT_VALID) is decided by the REAL decapsulation output + status token, not
synthesized. Real FO path confirmed in `kem.c:402-519` (`mlkem768_dec_monitored`).

### L11 — Operational twiddle table is `static`, in `__TEXT,__const` — VERIFIED
Method: `nm -m bin`→ `_mlk_zetas` non-external (static) in `(__TEXT,__const)`; `_tfib_zetas_ref`
external, same section, start-to-start offset **448 bytes** (reproduces design worked example).
Consequence: a test accessor for `A_op` must be defined INSIDE the TU holding `zetas`
(`poly.c`), `#ifdef`-guarded — an edit to the SUT, not an external `extern` decl.

### L12 — vm_protect write to `__TEXT,__const` → hard SIGBUS — REPRODUCED (BLOCKER)
Claim: on this M1/macOS, `vm_protect(RW|COPY)`+write to a `__TEXT,__const` object kills the
process with SIGBUS. Method: isolated spike, external-linkage const in `(__TEXT,__const)`;
exit 138 (=128+SIGBUS 10), reproduced twice, not catchable by a SIGBUS handler.
Consequence: the Step 2C-B spatial injector **as designed is infeasible** — the operational
table (always inside the blast interval) is in `__TEXT,__const`.

### L13 — vm_protect write to `__DATA_CONST` IS feasible and reversible — REPRODUCED
Claim: `vm_protect(mach_task_self, page, RW)` (kr=0) + write via a laundered pointer (writer in a
separate TU so the compiler cannot elide the `const` store) changes the value (orig 7→82) and
restoration + reset-to-RO succeed; no crash. Method: 2-TU spike `main4b.c`+`writer.c`.
Pitfall recorded: a same-TU write to a `const` object is elided at `-O2` (observed CHANGED=0),
so an honest injector MUST launder the write pointer. Consequence: feasible spatial injection
requires relocating `_mlk_zetas` to `__DATA_CONST` (research-build-only, documented) — which
also dissolves the "Variant A collocated in __TEXT,__const" design.

### L14 — Connor (1987) McNemar sample-size arithmetic is correct — VERIFIED
Method: recomputed N = (z₁₋α/₂√p_d + z₁₋β√(p_d−δ²))²/δ² with z=2.807/1.2816, δ=0.10:
p_d 0.10/0.15/0.20/0.30 → 162/246/329/496, matching the metrics doc exactly.
Scope/limit: arithmetic only. The INFERENCE is still defective (see L15).

### L15 — Equivalence-inference defect persists in 2C-B — VERIFIED
Claim: `acceptance_criteria.md` Outcome 2 still declares "H0 Supported" from McNemar `p ≥ 0.01`
and asserts a `[-0.05,0.05]` margin with NO TOST/CI equivalence procedure and NO equivalence
power analysis in `metrics_and_statistics.md`. A non-significant difference test ≠ equivalence.
Also: layout→outcome is near-deterministic given a fixed forward-anchored 512 B blast, so the
stochastic power apparatus is arguably mis-specified. NEXT: rewrite decision matrix + add TOST.

### L16 — Performance CPU-control methodology infeasible on target — VERIFIED
Claim: `threats_to_validity.md §3.2` relies on `pthread_setaffinity_np` and a "CPU frequency
governor" — neither exists / both are no-ops on macOS/Apple Silicon (no core pinning; QoS is a
hint only). TLB/cache rationale for a 256 B table is implausible. The ≤5% gate is an engineering
sanity check, not a controlled measurement. NEXT: rewrite with honest capability caveats.

### L17 — Step 2C-A timing figures — REPORTED (not reproduced)
Values 114.43 / 138.01 / 136.30 µs and +20.61% / +19.11% are prior-agent numbers; the benchmark
was NOT re-run this session. Do not cite as reproduced.

### L18 — Pre-existing protocol/channel sim exists — VERIFIED (not yet audited)
`experiments/system_model/spacecraft_protocol_sim.py` (323 lines, modified in working tree) and
`results/spacecraft_protocol_desync_results.json` exist. MUST be inspected and reused/improved
(not duplicated) for the Phase-3 channel emulator. Content/correctness: UNKNOWN pending audit.

### L19 — Clean/production builds do not enable research fault hooks — VERIFIED
Method: read `Makefile`. The conformance/interop objects `mlkem768_kat.o` (:34-35),
`mlkem512.o`, `mlkem1024.o`, `mldsa*.o`, and `mlkem768.o` are built **without**
`-DMLKEM_RESEARCH_FAULT_HOOKS`; the flag appears only on `*_inst.o`/`*_instrumented.o`/
`*_fault_hooks.o` used by campaign/experiment binaries. So `test_fips_kats`/`test_interop`
(the clean baselines) are hook-free. Regression-guarded by `test_hook_gate.c` (L20 step 3).

### L20 — Phase 1 fault-contract suite passes — REPRODUCED
Claim: the canonical fault contract enforces its invariants under strict warnings + ASAN/UBSAN.
Method: `research/fault_contract/run_phase1_tests.sh` → "PHASE 1 SUITE: PASS (overall exit=0)".
Breakdown: 17/17 invariant checks (exit 0); hook-gate compiles clean (hooks off) and FAILS to
compile with hooks on; robustness fuzz 500k inputs clean. Flags: `-std=c11 -Wall -Wextra
-Werror -Wconversion -Wshadow -fsanitize=address,undefined`.

### L21 — Contract enforces non-conflation + oracle-gated recovery — VERIFIED (tested)
`fc_classify()` (header-only, `fault_contract.h`): `RECOVERED` reachable only with
`oracle==VALID`; `oracle==NEITHER`→`SDC` regardless of monitor claims; ineligible/failed
injections cannot become "activated"; detected-fail-stop vs FO-contained kept distinct; a
dropped trial is caught by `fc_ledger_check()`. All asserted by `test_fault_contract.c`.

### L22 — Fuzz-surfaced UB fixed: serialized flags must be `uint8_t`, not `bool` — REPRODUCED
The deterministic robustness driver under UBSAN caught "load of value N not valid for type
'bool'" when records are populated from arbitrary bytes. Fixed by making all serialized flags
`uint8_t` compared `!=0`. Re-ran: 500k inputs, zero violations. (A genuine defect found & fixed
by the harness, not a cosmetic change.)

### L23 — libFuzzer runtime unavailable on this host — VERIFIED (limitation)
`clang -fsanitize=fuzzer` fails to link: `libclang_rt.fuzzer_osx.a` not present (Command-Line-
Tools clang, not full Xcode). CORRECTS the earlier E1 note that implied libFuzzer was usable.
Mitigation: deterministic standalone fuzz driver under ASAN/UBSAN (coverage-guided libFuzzer
remains available if the runtime is later installed — an external-resource decision).

### L24 — Phase 2 v1 memory-fault campaign reproduces the real crypto path exactly — REPRODUCED
Claim: a new contract-integrated runner (`research/fault_contract/mem_campaign.c`, links the same
`mlkem768_inst.o` + `libtfib.a` + oracle, same deterministic PRF inputs) reproduces the real
decapsulation behavior of the historical campaign for all 900 matched trials.
Method: `research/fault_contract/run_phase2.sh` → matched-baseline comparison
(`compare_and_stats.py` vs `tfib_experiments/phase2_step2c_trial_results.csv`): **0 crypto/
alignment mismatches, 0 migration-mapping mismatches** on 900/900 joined trials. Historical CSV
untouched (SHA `97ec6741…`). Artifacts: `research/results/phase2_mem_logical_v1/{raw.jsonl,
comparison_stats.md,manifest.json}`; raw.jsonl SHA `55ab1f57…`, reproducible across two runs (G5).

### L25 — Phase 2 outcome distribution + bounds (v1 taxonomy) — EMPIRICALLY OBSERVED
Over 900 trials (750 activated): CLEAN_COMPLETED 150, RECOVERED 250, SAFE_FAIL_DETECTED 350,
SAFE_FAIL_FO_CONTAINED 147, INEFFECTIVE 3, **SDC 0**, INCONCLUSIVE 0. Local detection among
activated = 600/750 = 0.80 (Wilson 95% CI [0.770, 0.827]). SDC 0/750: one-sided 97.5%
Clopper–Pearson upper bound **0.491%** (the 95% one-sided bound is 0.399%). Scope: logical-value
software faults only; 0 observed SDC is NOT evidence of 0 SDC risk. Recovery remains structural
per L8 (logical-value + pristine snapshot + untouched reference), not persistent-storage recovery.

### L26 — Persistent-storage / spatial arm remains BLOCKED — VERIFIED (blocker)
Not attempted. Op table in `__TEXT,__const` (L11) → persistent-store write is infeasible
(SIGBUS, L12); feasible only after relocating to `__DATA_CONST` (L13), a research-build change
deferred to a separate design review. See `research/PERSISTENT_STORAGE_BLOCKER.md`.

### L27 — Existing protocol simulator audited; unsuitable as-is — VERIFIED
`experiments/system_model/spacecraft_protocol_sim.py` (read-only). Defects: **tautological retry**
(clean retry always succeeds → committed output shows authenticated SESSION_RECOVERED 1000/1000,
SESSION_ABORTED 0); only 1 of 6 required channel-fault classes (ciphertext bit-flip); no
loss/truncation/delay/timeout/dup/reorder model; **non-replayable** (liboqs randomized keygen/
encaps); no per-trial ledger; conflated taxonomy. Uses liboqs KEM (no second independent KEM).
See `research/PHASE3_PROTOCOL_AUDIT.md`. Preserved untouched.

### L28 — Phase 3 channel-fault harness: deterministic, validated, reproducible — REPRODUCED
New harness `research/channel_harness/channel_campaign.py` drives DETERMINISTIC ML-KEM-768 via
liboqs `*_derand` (ctypes) + independent SHAKE-256 rejection check; implements the v1 protocol
spec with a **meaningful** retry (retries redraw the channel). `run_phase3.sh`: Gate-3 invariant
tests PASS (incl. timeout≠crypto-failure, crypto-reject≠timeout, protocol/crypto separation,
meaningful-retry recovery, full accounting, determinism); confirmatory 600 sessions (12 suites×50),
ledger balanced, **0 INCONCLUSIVE**; reproducible (raw.jsonl SHA `2cf7c29b…`, two runs identical).
Artifacts: `research/results/phase3_channel_v1/{raw.jsonl,pilot.jsonl,stats.md,manifest.json}`.

### L29 — Phase 3 outcome distribution (protocol vs crypto kept separate) — EMPIRICALLY OBSERVED
600 sessions: KEY_ESTABLISHED 100, RECOVERED_ON_RETRY 200, MALFORMED_MESSAGE 100, MESSAGE_LOST
100, TIMEOUT_RETRY_EXHAUSTED 50, PROTOCOL_ABORT 50 (Wilson 95% CIs in `stats.md`). Crypto verdict
(separate dim): VALID 350, REJECT 50, UNAVAILABLE 200. Recovery (200) is genuine (transient
channel clears on retry), NOT the audited tautology. Scope: abstract software emulator; logical
time; NOT real radio-link, radiation, or space qualification; no significance/causal claim.

### L30 — Phase 4 Gate 0: baselines revalidated; a single-path combined harness is required — VERIFIED
Reran both drivers: Phase 2 raw.jsonl `55ab1f57…`, Phase 3 raw.jsonl `2cf7c29b…` (match manifests).
**Obstacle:** the memory arm (C `mlkem_native`+TFIB) and channel arm (Python liboqs) are different
ML-KEM implementations with different fault loci; they cannot be naively combined. A valid combined
trial requires ONE decaps path carrying both faults → the Phase-4 coordinator is built on the C
`mlkem768_dec_monitored` path with a channel+protocol layer around it; liboqs+SHAKE stay the
independent oracle. Isolated runners unchanged. See `research/PHASE4_IDENTIFIABILITY_REVIEW.md`.

### L31 — Phase 4 Gate 2: interaction identifiable only as a frame-relative Monte-Carlo estimand — VERIFIED (design decision)
Both fault models are deterministic given seed → replays are repeatability, not independent obs.
Δ = p11−p10−p01+p00 is identifiable ONLY under an explicit researcher-defined fault distribution F
(F_mem×F_chan, pre-registered), with N = DISTINCT seeds as i.i.d. draws and a **paired bootstrap
over seeds** for Δ's own uncertainty. p/Δ are properties of F, NOT physical probabilities; CIs are
Monte-Carlo uncertainty over F. If F is rejected, the result degrades to descriptive scenario
coverage. Pre-registered in `research/PHASE4_PREREGISTRATION.md`.

### L32 — Phase 4 Gate 4 pilot: harness validated; masking defect found & fixed — REPRODUCED
Pilot (20 seeds × 4 = 80), `run_phase4_pilot.sh`: build `-Werror` clean, 0 INCONCLUSIVE, 0 excluded,
reproducible (`pilot.jsonl` SHA `d6fc82f5…`). **Defect found by the pilot:** the initial exclusion
rule discarded C11 trials where the channel blocked delivery so the memory fault never activated —
but that is a legitimate **channel-masks-memory interaction**, not an injection failure. Fixed:
such cases are retained as `MASKED_BY_CHANNEL` (9/20 of C11); true injection failures (decaps ran,
fault did not fire) would be the only exclusions (0 observed). Pilot (DESCRIPTIVE, n=20): p00 100%,
p10 40%, p01 50%, p11 20%, Δ̂ +0.30. **Confirmatory NOT run — gated on design-review sign-off.**

### L33 — Phase 4 design-review v2: joint sensitivity + masking semantics — EMPIRICALLY OBSERVED (exploratory)
Amendment `PHASE4_PREREGISTRATION_AMENDMENT_v2.md` (v1 preserved). Exploratory 1000-seed temp draw
(NOT the 500-seed confirmatory): overall Δ̂ +0.21 [+0.184,+0.245]. **Joint reweighting** of
P(mem PERSISTENT)×P(channel PERSISTENT) over {0.25,0.5,0.75}²: Δ ∈ [+0.052,+0.463], **sign stable
>0 across the family**, magnitude ~9×. **Conditional Δ: channel-PERSISTENT +0.39 vs
channel-TRANSIENT +0.00** → the interaction is a persistent/blocking-channel **masking** effect,
absent for transient channels. Masking rate 423/1000 = 42.3% of C11; established-among-MASKED
126/423 vs ACTIVATED 137/577 (masked completion is channel-retry-driven, NOT memory recovery).
Primary claim predefined = masking MECHANISM; Δ under F = secondary, F-conditional. `combined_stats.py`
updated to report masking + conditional strata; pilot re-run PASS (SHA unchanged). Confirmatory still
absent (gated).

### L34 — Phase 4 CONFIRMATORY (500 seeds × 4, frozen) — REPRODUCED / EMPIRICALLY OBSERVED
`run_phase4_confirmatory.sh` (frozen-input hashes recorded pre-execution; no protocol/analysis change
after). 2000 trials, 0 inconclusive, 0 excluded, 0 dropped; reproducible raw.jsonl SHA `d20c0ef5…`.
Per-condition P(established): C00 100%, C10 48.0% [43.6,52.4], C01 56.4% [52.0,60.8], C11 26.0%
[22.2,30.0]. **Δ̂ = +0.216 [paired-bootstrap 95% +0.180,+0.252].** Conditional: channel-PERSISTENT
Δ=+0.419 (n=258) vs channel-TRANSIENT Δ=**+0.000** (n=242). Joint grid Δ∈[+0.052,+0.471], sign
stable>0. **Masking (primary): 203/500 = 40.6% of C11**; established-among-MASKED 57/203 vs
established-among-ACTIVATED 73/297 (masked ≠ recovered; masked completion is channel-retry-driven).
Primary (masking mechanism) SUPPORTED; secondary (F-conditional Δ>0) SUPPORTED as frame-relative.
No physical/RF/radiation/qualification/causal claim. Artifacts in `research/results/phase4_combined_v1/`.

