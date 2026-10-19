# BLOCKED: persistent-storage memory-fault arm & spatial-layout experiment

Status: **BLOCKED — not attempted in Phase 2.** Phase 2 delivered only the logical-value arm.
This note records the exact blocker and the separate design review required before any
research-build-only relocation or spatial campaign.

## The blocker (evidence)
- The operational twiddle table `_mlk_zetas` is `static` in **`__TEXT,__const`** (EVIDENCE_LEDGER
  L11, verified via `nm -m`).
- A genuine persistent-storage fault must write the backing store. On this M1/macOS,
  `vm_protect(RW|COPY)` + write to a `__TEXT,__const` object **terminates with SIGBUS**
  (L12, reproduced twice, exit 138) — `__TEXT` is code-signed.
- Writing is feasible & reversible only in **`__DATA_CONST`** (L13), and only with a laundered
  write pointer (a same-TU write to a `const` is elided at `-O2`).
- Therefore a persistent-storage arm requires **relocating `_mlk_zetas` into `__DATA_CONST`** —
  a change to the system-under-test build. That is explicitly deferred to a separate review.

## What the separate design review must resolve (before any relocation/spatial run)
1. **Research-build isolation**: relocation via a research-only build flag; the production/clean
   build (and KAT conformance) must remain byte-for-byte unaffected (regression-gated).
2. **Layout confounds**: moving the table changes neighbours. Define a fixed guard/padding object
   so the bytes adjacent to the op table are identical across variants except for the ref table
   (prior audit finding F9).
3. **Feasibility**: a `vm_protect` spike proving write+restore works for the relocated table AND
   that restoration leaves no cross-trial contamination (verify read-back + protection reset).
4. **Comparability**: show results remain comparable to the logical-value arm and to historical
   data — i.e. the only intended change is logical-value→persistent-storage, nothing else.
5. **Statistics**: the near-deterministic layout→outcome relationship means a stochastic power
   framework is likely mis-specified; use an equivalence (TOST) or descriptive design as argued
   in the earlier Step 2C-B review, not a non-significant difference test.
6. **Claims discipline**: still software-only; `__DATA_CONST` placement is NOT physical isolation
   or radiation hardness.

Until this review is approved, the persistent-storage / spatial-layout experiment stays BLOCKED.
