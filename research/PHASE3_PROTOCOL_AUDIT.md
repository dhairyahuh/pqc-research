# Phase 3 Gate 0 — Audit of the existing protocol simulator (read-only)

Target: `experiments/system_model/spacecraft_protocol_sim.py` (323 lines, tracked, modified in
working tree) + deps `algorithms/oqs_wrapper.py`, `fault_injection/fault_models/fault_definitions.py`,
`fault_injection/scheduler/scheduler.py`, `fault_injection/injector/engine.py`, output
`results/spacecraft_protocol_desync_results.json`. **No file was modified in this audit.**
Callers: none — the sim is standalone (`main()` only; no other module imports it).

## 1. Modeled protocol, formats, state transitions
- Abstract spacecraft-ground telecommand model (explicitly NOT CCSDS/ECSS; disclaimed in-source).
- Frame: 18 bytes — magic `"SPAC"`, uint16 seq, subsystem id, opcode, 2×int32 params, CRC16-CCITT.
- Receiver pipeline: length → magic → seq-window → subsystem/opcode dict → param bounds → CRC16 → execute.
- "Encryption" = SHA-256 keystream XOR; optional HMAC-SHA256 tag (authenticated mode).
- Per-trial flow: keypair → encaps → build+encrypt+MAC frame → inject **ciphertext** bit-flip →
  decaps → compare keys → branch. Essentially stateless except a retry loop.

## 2. Real ML-KEM vs model
Uses **liboqs** ML-KEM-768 via a ctypes wrapper (`oqs_wrapper.MLKEM`) — the standard *randomized*
`OQS_KEM_keypair/encaps/decaps`. This is the SAME family as our independent oracle, so there is
**no second independent KEM** in the channel layer; the KEM is real but not cross-checked here.
The in-tree `mlkem_native`/TFIB path is NOT exercised (correct — channel faults act on ciphertext
bytes + protocol logic, not NTT internals).

## 3. Retry / timeout / interruption / error semantics — **DEFECTIVE**
- **Tautological retry (critical):** on auth failure the retry does `encaps(sc_pk); decaps(retry_ct)`
  with **no fault injected** on the retry (lines 232-238). A clean ML-KEM round-trip always
  matches, so recovery is **guaranteed** on retry 1. Confirmed by the committed output:
  authenticated = SESSION_RECOVERED **1000/1000**, SESSION_ABORTED **0**. Retry-exhaustion is
  effectively unreachable. The recovery/abort metrics are artifacts, not evidence.
- **No real timeout/loss/delay/duplication/reordering/truncation:** none are modeled. The only
  fault is a single ciphertext bit-flip (`inject_seu_bit_flip`). `detection_latency_us` is just
  wall-clock of the decaps call — a performance number, not a protocol timeout.
- Unauthenticated mode: wrong key → garbage plaintext → fails magic → FORMAT_REJECTED (1000/1000).

## 4. Randomness, seed control, replay, accounting — **PARTIALLY DEFECTIVE**
- Fault schedule is deterministic (`DeterministicScheduler`, SHA-256-seeded `random.Random`).
- BUT KEM keypair/encaps use liboqs' **randomized** entry points → the ciphertexts/keys differ
  every run; the campaign is **not byte-replayable** (a Phase-2 gate-level requirement).
- Accounting: only 7 outcome counters + first 5 sample records; **no per-trial ledger**, no
  ineligible/failed/excluded accounting, no injection-activation evidence.

## 5. Shortcuts that bias availability / fault effects
- Tautological retry inflates "availability"/recovery to 100%.
- Outcome taxonomy conflates layers: sequence-window failures are labelled `FORMAT_REJECTED`;
  the ONLY accept path returns `GARBLED_PAYLOAD_ACCEPTED` (success and "garbled-accept" merged);
  `AUTHENTICATION_FAILURE` mixes crypto-layer detection with protocol reaction.
- Single fault class only; bit-flip always lands "activated" (no ineligible/loss branch).

## 6. Verdict & smallest defensible repair
**Unsuitable for Phase 3 as-is** (tautological recovery, missing 5 of 6 fault classes, no
timeout/loss model, non-replayable KEM, no ledger). It is NOT lightly repairable in place, and
it is tracked+pre-existing work I must not overwrite. **Smallest defensible path:** build a NEW
versioned harness under `research/` that (a) reuses the *good* parts — the 18-byte frame, CRC16,
receiver pipeline shape, deterministic-seed idea; (b) drives **deterministic** ML-KEM via the
liboqs `*_derand` symbols (verified present) through ctypes, with SHAKE-256 PRF seeds and an
independent rejection-key recomputation `J(z||c)` as a crypto cross-check; (c) implements a real
channel model (6 fault classes) with a **meaningful** retry (retries redraw from the channel, so
a persistently bad channel exhausts retries); (d) uses the v1 fault-contract ledger + a NEW,
separate protocol outcome taxonomy (Gate 1). The existing sim/results are preserved untouched for
traceability.
