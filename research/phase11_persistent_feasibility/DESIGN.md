# Phase 11 — Design (feasibility prototype + the real-arm plan requiring approval)

## Implemented now (isolated, safe, no SUT change)
Files (all new, in `research/phase11_persistent_feasibility/`):
- `reader.c` — separate TU: `fc_checksum` (reads every table element at runtime so the value cannot
  be constant-folded → proves consumption), plus laundered `fc_poke`/`fc_peek`.
- `proto.c` — a `__DATA_CONST,__fc_tbl` const `int16_t[128]` MODEL table (same size/const/alignment
  character as `mlk_zetas`, deliberately **relocated** to a writable-after-`vm_protect` section);
  per-trial vm_protect(RW) → laundered poke → read-back → consume (checksum) → restore → read-back →
  re-protect(RO); fails closed on any mismatch; writes `RESULTS.csv`.
- `run_feasibility.sh` — builds (reader TU separate), prints the section placement, runs.

Why this is safe: it never touches `mlkem_native`, campaign code, raw data, or manifests; it does not
manipulate a code-signed `__TEXT` page; build artifacts go to a temp dir.

## NOT implemented (requires approval) — the real-arm plan
To test persistent corruption of the **actual** `mlk_zetas` during real decapsulation, the following
SUT changes would be needed and are **held for approval**:
1. **Research-only relocation** of `mlk_zetas` from `__TEXT,__const` to `__DATA_CONST`, guarded so it
   is active ONLY in a dedicated research build (e.g. `#if defined(MLK_RESEARCH_PERSIST_FAULT)` around
   a `__attribute__((section("__DATA_CONST,__mlk_zetas")))` variant), leaving the auto-generated
   `zetas.inc` and the production/KAT builds byte-identical. Files that would change: a research-only
   overlay/header (NOT `zetas.inc` directly if avoidable) + the research build recipe.
2. A **test-build accessor** for `&mlk_zetas` (the symbol is `static`), compiled in the same TU, so
   the harness can resolve the runtime address (as in the earlier Step 2C-B design).
3. **Disassembly verification** (`otool -tV`) that `mlk_ntt`/butterfly loads come from the relocated
   `mlk_zetas` symbol, so corruption is genuinely consumed.
4. A persistent-fault campaign reusing the Phase-2 input PRF + the independent oracle, recording for
   each trial: which coefficient, read-back change, decapsulation output vs clean baseline, FO
   verdict, and byte-for-byte restoration — with the same honesty guards (masking≠recovery; a write
   is not "activated" unless read-back changed; a crypto effect is not claimed unless output differs
   and the clean baseline reproduces).

## Acceptance criteria (for the real arm, when approved)
Intended bytes change (read-back); the NTT consumes them (output differs for coefficients that affect
the exercised path; unchanged otherwise — not forced per trial); differences measured vs a
reproducible clean baseline; restoration verified byte-for-byte; no cross-trial contamination;
production/KAT build unaffected. Otherwise BLOCKED/INCONCLUSIVE, documented.
