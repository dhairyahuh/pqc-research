# Open Issues — Manuscript v1

Unresolved items, flagged (not silently reconciled). None of these were "fixed" by editing
historical artifacts.

## Flagged discrepancies in source artifacts
1. **Phase 3 fault-class count: "six" vs seven (NOT resolved).** Two prose artifacts say
   "six fault classes" while parenthetically listing seven:
   - `research/phase2_4_report/REPORT.md:56` — "six fault classes (bit, truncation, loss,
     delay/timeout, duplication, reorder, interruption)" → the list has 7 items.
   - `research/IMPLEMENTATION_LOG.md:94` — "6 channel-fault classes (…)" with 7 items.
   The specification (`research/PROTOCOL_FAULT_MODEL_SPEC.md:67-69`) and the raw data both have
   **seven** classes (BIT_CORRUPTION, TRUNCATION, PACKET_LOSS, DELAY, DUPLICATION, REORDER,
   INTERRUPTION) plus CLEAN (8 distinct `channel_class` values; 12 suites). Likely origin: the
   Phase-3 brief bundled "duplication and reordering" and "interruption and retry exhaustion" into
   single bullets. The manuscript uses the **data-grounded count = seven** and flags the prose
   mismatch. The historical REPORT.md/IMPLEMENTATION_LOG.md were left unchanged.

## Scientific / evidentiary gaps (must address before submission)
2. **Comparative literature review NOT done.** No PQC fault-injection / cross-layer prior-work
   survey; no verified bibliographic metadata beyond standards/implementations actually used
   (FIPS 203, FIPS 202, mlkem_native, liboqs 0.16.0). No novelty claim is made.
3. **F is researcher-defined and uniform** — arbitrary. All p/Δ are conditional on F; Δ magnitude
   varies ~9× over the tested persistence-weight grid. A physically/operationally motivated F is
   needed for any population-level statement.
4. **No validated persistent-storage memory-fault arm** (BLOCKED: `__TEXT,__const` write SIGBUSes;
   feasible only after a reviewed `__DATA_CONST` relocation). Memory results are logical-value only.
5. **No second independent KEM** in the channel/combined arms (liboqs is both KEM and oracle there);
   the independent check is the SHAKE rejection recomputation + protocol spec, which is weaker than
   an independent KEM cross-check.
6. **No physical experiments** (radiation/EM/glitch) and **no cross-platform/compiler replication**
   (single arm64/clang/liboqs environment).
7. **Audit is internal, not external.** `independent_audit.py` is a freshly-written in-repo
   recomputation; it is not an external replication or peer review and must not be described as one.
8. **Step 2C-A timing/overhead figures not reproduced** in this work (EVIDENCE_LEDGER L17).
9. **p00 is degenerate (=1)**; the interaction contrast is driven by the three faulted conditions.
10. **libFuzzer runtime unavailable**; robustness used a deterministic ASAN/UBSAN driver.

## Interpretation guards verified present
- Zero observed SDC is reported as a finite-sample observation, never as zero risk.
- Channel masking is reported as a distinct status, never as memory-fault recovery.
- Transient-channel Δ=0 is reported as a per-seed structural identity, not a tested null.
