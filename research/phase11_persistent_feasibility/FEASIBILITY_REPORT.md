# Phase 11 — Persistent-Storage Fault Feasibility Report

**Decision: CONDITIONAL GO.** The injection *mechanism* (persistent corruption of a `__DATA_CONST`
const table, consumed by a separate computation, then verifiably restored) is **demonstrated feasible
and safe in isolation on this platform** (128/128 trials). The **real ML-KEM arm is NO-GO as-is**
because the operational table lives in `__TEXT,__const` (code-signed) and faults on write (SIGBUS);
it becomes feasible **only after an approved, research-only relocation** of the table to
`__DATA_CONST` plus disassembly verification. No radiation claim is made.

Distinguish three things this phase kept separate: a **logical-value** fault (XOR of a local copy —
the existing campaigns), a **virtual-memory mapping** (the read-only image page), and the **actual
shared backing storage** (`mlk_zetas` bytes the NTT reads every call). Only the last is
"persistent-storage"; the existing campaigns do **not** test it.

## Evidence: what was inspected vs executed
- **Source-inspected:** `algorithms/source_ref/mlkem/src/zetas.inc:17` —
  `static MLK_ALIGN const int16_t mlk_zetas[128]` (auto-generated; "do not modify directly");
  reads at `poly.c:447` (`mlk_zetas[k++]`, forward NTT), `:546` (inverse), `:292` (basemul) — all
  **runtime-indexed memory loads**, not per-call copies or constant folds. The logical-value hook
  mutates a **local** `int16_t zeta_val` (`poly.c:381`, `tfib_hooks.c`), never the table.
- **Binary-inspected:** `nm -m` → `_mlk_zetas` is **non-external (static), (`__TEXT,__const`)**.
- **Executed (this session, isolated spikes to $TMPDIR):** writing `__TEXT,__const` → **SIGBUS, exit
  138** (reproduced); writing `__DATA_CONST` via `vm_protect(RW)` + a laundered (separate-TU) pointer
  → **effective and restorable** (orig 7 → 82 → 7).
- **Executed prototype:** `run_feasibility.sh` (RESULTS.csv) — 128 trials on a `__DATA_CONST` model
  table: readback_changed 128/128, **consumed_changed 128/128** (separate-TU checksum moved),
  restored_ok 128/128, baseline_reproduced 128/128, **no cross-trial contamination**, exit 0.

## Answers to the eight feasibility questions
1. **SIGBUS root cause:** the previous attempt wrote `__TEXT,__const`. On arm64 Darwin that is the
   code-signed, read/execute `__TEXT` segment; `vm_protect` to writable on a signed `__TEXT` page is
   refused and the write faults (W^X + code-signing/library validation). Reproduced (exit 138).
2. **Persistent state vs mapped image?** `mlk_zetas` is a read-only mapped **image** section AND is
   **genuine persistent operational state**: the NTT reads it from memory on every invocation
   (`poly.c:447/546/292`). It is not "data that merely stays unchanged for one call." The existing
   logical-value fault never touches it.
3. **Can the approach change consumed bytes?** On `__DATA_CONST`: **yes** — demonstrated (128/128
   consumed_changed via an independent reader TU). On the real table in `__TEXT,__const`: **no**
   (SIGBUS). So feasible **only after relocation** to `__DATA_CONST`.
4. **Confounds from relocation/protection change:** relocating a `static const` **auto-generated**
   table alters binary layout and possibly codegen/addressing; it must be a **research-only** build
   (e.g. `#ifdef`/section override) so production + FIPS-KAT builds are byte-unchanged, and
   **disassembly must confirm the NTT still loads from the symbol** (not an optimizer-made copy).
   `const` semantics also require a laundered write. Real confound risk → verify before trusting.
5. **Reliable restoration?** Yes — golden snapshot + per-trial restore + read-back + re-protect RO;
   demonstrated byte-for-byte (restored_ok 128/128).
6. **Verification of restore/read-back/contamination:** per-element read-back == orig; independent
   checksum returns to baseline each trial; final full-table checksum == initial (no_contam = 1).
7. **Smallest safe prototype:** the isolated `__DATA_CONST` model used here — no SUT change, no
   manipulation of a code-signed segment.
8. **Conclusive negative result:** for the **unmodified** SUT, the real arm is **NO-GO** (SIGBUS on
   `__TEXT,__const`). A further NO-GO would be: after relocation, disassembly shows the NTT consumes a
   copy (corruption not consumed), or relocation breaks the KATs — either kills the real arm.

## Limitations / unresolved
- The prototype is a **model** (synthetic `__DATA_CONST` table + synthetic reader), proving the
  mechanism — **not** the real decapsulation. It does not by itself validate the real arm.
- The real arm needs: (a) **approval** to relocate `mlk_zetas` (auto-generated SUT source) under a
  research-only guard; (b) disassembly proof the NTT reads the relocated symbol; (c) proof the
  production/KAT build is unchanged. None performed this phase (kept production untouched).
- Still software-only; no persistent-storage result on the real SUT; **no radiation meaning**.
