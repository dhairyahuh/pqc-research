# Fault-Model Specification (v1) — ML-KEM-768 Space-Resilience Research

Status: Phase 1 implemented & tested (see [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md),
[EVIDENCE_LEDGER.md](EVIDENCE_LEDGER.md) L19–L23). Canonical schema + taxonomy for ALL
experiments (memory, channel, combined). Implemented header-only in
`research/fault_contract/fault_contract.h`.

## 1. Scope & non-claims
Software fault **simulation** only. A simulated phenomenon is never a physically observed one.
This spec confers no radiation-tolerance, physical-isolation, or flight-qualification meaning.

## 2. Fault-event schema (`fc_event_t`, `FC_SCHEMA_VERSION = 1`)
Versioned, byte-serializable (flags are `uint8_t`, not C `bool`, so records deserialized from
bytes have well-defined reads — a fuzz-surfaced requirement, L22). Fields:

| Field | Meaning |
|---|---|
| `schema_version` | must equal `FC_SCHEMA_VERSION`; checked by `fc_event_valid()` |
| `model_id`,`model_version` | fault-model identity + version |
| `target_component`,`target_id` | WHAT is corrupted (enum `fc_target_t`) + index |
| `phase`,`op_index` | logical phase / operation index at injection |
| `seed`,`event_index` | deterministic campaign seed + event index (replayable) |
| `location_kind`,`location`,`mask` | bit/byte/word/logical offset + corruption mask |
| `fault_class` | **CRITERION 1**: `LOGICAL_VALUE` vs `PERSISTENT_STORAGE` |
| `duration` | `TRANSIENT` / `PERSISTENT` |
| `combo_group` | `-1` standalone, else combined-fault group id |
| `armed`,`target_accessible`,`mutation_applied`,`target_actually_affected` | activation evidence |

### 2.1 CRITERION 1 — logical-value vs persistent-storage (the distinction the audit flagged)
- **`FC_CLASS_LOGICAL_VALUE`** — a value in a register/local copy is altered; the backing
  store is NOT changed. This is exactly what the *existing* Step 2C-A harness does
  (`*zeta_ptr ^= mask` on a local copy; const tables never written — EVIDENCE_LEDGER L7).
  An injector claiming this class must demonstrate the backing store is unchanged.
- **`FC_CLASS_PERSISTENT_STORAGE`** — the backing store itself is altered and subsequent reads
  observe it until repaired. On this platform real persistent-store mutation of constant tables
  is feasible only in `__DATA_CONST`, not `__TEXT,__const` (L12/L13); an injector claiming this
  class must show a post-write read-back change (`target_actually_affected`).

Every experiment MUST declare which class it implements and provide the activation evidence.

## 3. Injection status (`fc_injection_status`) — CRITERION 2, first-class
Derived purely from recorded evidence; a monitor can never promote these:
- `NOT_ARMED` (clean control) · `INELIGIBLE` (target inaccessible / cannot apply) ·
  `FAILED` (attempted, no read-back change) · `ACTIVATED` (applied AND target affected).
Ineligible/failed injections are reported as such and are **excluded from "activated"
denominators but retained in the trial ledger** (CRITERION 5).

## 4. Correctness verdict (`fc_oracle_verdict_t`) — CRITERION 3
The ONLY source of correctness truth is an INDEPENDENT oracle (liboqs + standalone SHAKE-256,
audited in EVIDENCE_LEDGER L3/L4): `VALID` / `REJECT` / `NEITHER` / `UNAVAILABLE`. The
countermeasure's own `monitor.*` claims are recorded but **untrusted** for correctness.

## 5. Terminal outcome taxonomy (`fc_outcome_t`) & classification
`fc_classify()` is a pure function of recorded facts. Matrix for an ACTIVATED fault:

| oracle \ detected | detected | not detected |
|---|---|---|
| VALID  | `RECOVERED` | `INEFFECTIVE` |
| REJECT | `SAFE_FAIL_DETECTED` | `SAFE_FAIL_FO_CONTAINED` |
| NEITHER | `SDC` | `SDC` |

Plus: `CLEAN_COMPLETED` (unarmed+VALID), `INELIGIBLE`, `INJECTION_FAILED`, `TIMEOUT`
(availability loss), `EXCLUDED` (requires a reason), `INCONCLUSIVE` (invariant violation).
**Enforced invariants** (tested, L21): `RECOVERED` is reachable ONLY with `oracle==VALID`
(a monitor claim can never produce it); `oracle==NEITHER` forces `SDC` regardless of claims;
detection is kept orthogonal so detected-fail-stop and FO-contained are never merged.

## 6. Trial accounting (`fc_ledger_*`) — CRITERION 5
Every started trial is finalized exactly once; `fc_ledger_check()` returns nonzero if
`started != finalized` or counters disagree (detects dropped/missing records). Ineligible,
failed, timed-out, SDC, and excluded trials are all first-class ledger entries — nothing is
silently dropped.

## 7. Determinism
All campaign inputs come from a deterministic SHAKE-256 PRF (`campaign_prf.h`); no
`rand()/time()/entropy` in audited code (L5/G). Event schedules are replayable from `seed` +
`event_index`.

## 8. Migration path for historical Step 2C-A data — CRITERION 7
Historical results are **not modified** (CSV SHA-256 unchanged, L5). New campaigns emit the v1
schema; the existing `outcome_class` column maps forward as:

| Step 2C-A `outcome_class` | v1 `fc_outcome_t` | caveat |
|---|---|---|
| `CLEAN_SUCCESS` | `CLEAN_COMPLETED` | — |
| `GENUINE_RECOVERY` | `RECOVERED` | recovery is structural in 2C-A (L8): logical-value fault + pristine snapshot + untouched reference; oracle-VALID held so the mapping is valid, but it is NOT recovery from persistent-storage corruption. |
| `SAFE_FAIL_STOP` | `SAFE_FAIL_DETECTED` | partly monitor-forced via `kem.c:486-494` (L9) |
| `LOCAL_BLIND_FO_CONTAINED` | `SAFE_FAIL_FO_CONTAINED` | genuine real-path FO rejection (monitor silent) |
| `INEFFECTIVE_FAULT_VALID` | `INEFFECTIVE` | perturbation absorbed; valid key preserved |
| (none observed) | `SDC` | 0/750 in 2C-A; sampling bound only |

A converter will be provided when the first v1 campaign runs; until then this table is the
documented, non-destructive mapping. The 2C-A fault class is uniformly `LOGICAL_VALUE`.

## 9. Open items this spec does NOT yet cover (tracked for later phases)
- Channel/protocol event sub-schema (Phase 3) — will extend `fc_target_t`/`phase` and add a
  protocol-outcome verdict separate from the ML-KEM oracle.
- Combined-fault interaction estimand (Phase 4) — Δ = p11−p10−p01+p00, pre-registered.
- Equivalence testing (TOST) and the spatial-layout redesign (separate 2C-B review).
