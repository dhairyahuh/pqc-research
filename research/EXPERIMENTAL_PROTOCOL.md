# Experimental Protocol (pre-registration) — Phase 2 logical-value memory-fault arm

Frozen BEFORE the confirmatory run. Companion: FAULT_MODEL_SPECIFICATION.md, EVIDENCE_LEDGER.md.

## Objective
Re-express the existing memory-fault campaign under the v1 fault contract, validate that the
contract integration preserves the real cryptographic behavior (matched baseline), and report
the outcome distribution with correct denominators and uncertainty. This is NOT a new causal
claim and NOT a superiority/equivalence test.

## Design
- Factors (same 18 suites as Step 2C-A): config ∈ {BASELINE, TFIB_REF, TFIB_META} × fault
  locus/duration. Fault class is uniformly **LOGICAL_VALUE** (a temporary local copy is XORed;
  const backing storage is never written). Fixed **N = 50 trials/suite = 900 total**.
- Deterministic inputs: SHAKE-256 campaign PRF (`campaign_prf.h`), identical to the historical
  runner; fault params `stage=(t%7)+1, butterfly=(t*17)%128, bit=(t%15)+1`.

## Recorded dimensions (kept strictly separate — never merged)
injection_status (NOT_ARMED/INELIGIBLE/FAILED/ACTIVATED) · monitor_detected · monitor_claimed_recovery ·
oracle_verdict (VALID/REJECT/NEITHER) · terminal_outcome (fc_outcome_t). Correctness is taken
ONLY from the independent oracle; monitor claims are untrusted.

## Endpoints (descriptive, with denominators + CIs)
1. Activation rate = ACTIVATED / armed.
2. Local detection rate = detected / ACTIVATED, per config.
3. Terminal-outcome distribution per config/suite.
4. SDC count and one-sided 97.5% Clopper–Pearson upper bound over activated trials.

## Exclusions & accounting
- INELIGIBLE / INJECTION_FAILED excluded from the "activated" denominator but retained in the
  ledger. EXCLUDED requires a reason. Every scheduled trial gets exactly one ledger record.

## Statistics
- Proportions with Wilson 95% CIs; SDC 0/n → exact Clopper–Pearson upper bound.
- **No superiority p-value and no equivalence claim.** The layout/locus→outcome relationship is
  largely deterministic per suite (an audit finding); inferential testing is deferred to a
  properly powered design (TOST etc., see earlier review). Differences are reported descriptively.

## Acceptance gates (all must pass; else STOP before accepting the dataset)
G1 ledger balanced (started==finalized, counters consistent); G2 zero `inconsistent` records;
G3 zero `INCONCLUSIVE` outcomes; G4 matched-baseline: for all 900 trials the new record's
`ss_match`, `rej_match`, `status` equal the historical CSV's `output_correct`,
`implicit_rejection`, `final_status`, and alignment keys match; G5 reproducibility: two runs
byte-identical (SHA-256).

## Scope / non-claims
Logical-value software fault only. Not persistent-storage corruption, not physical radiation,
not flight qualification. Zero observed SDC is not evidence of zero SDC risk.
