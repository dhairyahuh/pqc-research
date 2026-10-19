# Phase 11 — Reproduce

Environment: Apple Silicon arm64, Darwin 27, Apple clang 21. No network, no new tools. The prototype
is self-contained (mach `vm_protect` via `<mach/mach.h>`); it does NOT link or modify mlkem_native.

## Run the isolated feasibility prototype
```bash
research/phase11_persistent_feasibility/run_feasibility.sh
```
Expected (deterministic): section check prints `(__DATA_CONST,__fc_tbl) external _table`; the run
prints `trials=128 consumed_changed=128/128 all_rb+restore+baseline_ok=1 no_cross_trial_contam=1`,
`exit=0`; and writes `RESULTS.csv` (128 rows; every row readback_changed=consumed_changed=
restored_ok=baseline_reproduced=1).

## Re-ground the platform facts (optional spikes, isolated to $TMPDIR)
- `__TEXT,__const` write → **SIGBUS (exit 138)** — the earlier failure's root cause.
- `__DATA_CONST` write via `vm_protect(RW)` + a laundered (separate-TU) pointer → effective and
  byte-restorable.
(The exact spike sources are reproduced in `FEASIBILITY_REPORT.md`; they were run from a temp dir and
not committed.)

## Scope
This reproduces the **mechanism** on a `__DATA_CONST` model table only. It does **not** reproduce a
persistent-storage fault on the real `mlk_zetas` (that remains `__TEXT,__const` and requires an
approved research-only relocation; see `DESIGN.md`). No radiation/physical claim.
