# Protocol Fault-Model Specification v1 (Phase 3 channel-fault arm)

Gate 1 deliverable. Companion to the v1 memory-fault contract (FAULT_MODEL_SPECIFICATION.md).
Protocol outcomes are kept **strictly separate** from the cryptographic oracle verdict.
`PROTOCOL_SCHEMA_VERSION = 1`. Status: specification; implemented in Gate 2.

## 1. Scope & non-claims
Abstract software channel/protocol emulator. NOT CCSDS/ECSS, NOT real radio-link timing, NOT
space qualification, NOT physical radiation. "Timeouts/delays" are LOGICAL time steps, not RF
seconds. A modeled channel error is NEVER a memory fault (Phase 2) — the two arms stay separate.

## 2. Cryptographic verdict (reused, separate layer)
`fc_oracle_verdict ∈ {VALID, REJECT, NEITHER, UNAVAILABLE}` computed independently of the
countermeasure, exactly as Phase 2: VALID = decaps output == independent derand-encaps secret;
REJECT = output == independent `J(z||c)=SHAKE256(z||c,32)` rejection key; NEITHER = neither
(silent wrong-secret acceptance). This is the crypto layer only — it does NOT by itself decide the
protocol outcome.

## 3. Protocol outcome taxonomy (separate from §2)
| Outcome | Meaning |
|---|---|
| `KEY_ESTABLISHED` | session key agreed, frame parsed & verified, command accepted |
| `CRYPTO_KEY_MISMATCH` | KEM/MAC verification failed (crypto REJECT) — detected at crypto layer, no retry resolved it within budget |
| `MALFORMED_MESSAGE` | delivered bytes fail framing/parse (bad length, magic, truncation) |
| `MESSAGE_LOST` | message not delivered (loss/interruption) and not recovered |
| `TIMEOUT_RETRY_EXHAUSTED` | delivery deadline missed on every attempt (delay/loss driven) |
| `RECOVERED_ON_RETRY` | a later retransmission attempt succeeded (key established after ≥1 failed attempt) |
| `PROTOCOL_ABORT` | protocol safely terminated (fail-closed) after exhausting retries on a *crypto* mismatch |
| `INCONCLUSIVE` | harness/invariant failure (must be investigated; gate requires 0) |

Also recorded separately (never folded into the terminal outcome): injection_status
(Phase-2 contract), delivery_effect, crypto_verdict, retry_count, session_completed.

## 4. Precedence rules (deterministic; evaluated top-down)
1. Harness/invariant violation → `INCONCLUSIVE`.
2. If the FINAL attempt's message was not delivered at all (loss/interruption) → `MESSAGE_LOST`;
   if non-delivery was specifically a missed delivery deadline → `TIMEOUT_RETRY_EXHAUSTED`.
3. Else if the delivered bytes fail framing/parse → `MALFORMED_MESSAGE`.
4. Else evaluate the crypto verdict of the delivered attempt:
   - VALID → if this was attempt >1 after earlier failures → `RECOVERED_ON_RETRY`, else `KEY_ESTABLISHED`.
   - REJECT → retries remain? the next attempt is evaluated; if all exhausted → `PROTOCOL_ABORT`
     (safe fail-closed) and we also set `CRYPTO_KEY_MISMATCH` on the attempt record.
   - NEITHER → `KEY_ESTABLISHED` at protocol layer BUT crypto_verdict=NEITHER is flagged as a
     dangerous silent acceptance (SDC at the crypto layer); surfaced explicitly, never hidden.
**Mandated separations:** a TIMEOUT must NOT be recorded as a crypto failure (rule 2 precedes
rule 4); a crypto REJECT must NOT be recorded as a TIMEOUT (rule 4 only reached after delivery).

## 5. Session state machine
`INIT → ENCAPS → SEND(attempt a) → CHANNEL(a) → {DELIVERED | LOST} → PARSE → DECAPS+VERIFY →
{ESTABLISHED(terminal) | MISMATCH | MALFORMED} → (if not established and a<RETRY_MAX: a←a+1, SEND)
→ terminal`. Terminal states map to §3. One telecommand per session.

## 6. Framing, retry, timeout, termination (normative)
- **Wire message** = `KEM_ciphertext(1088B) || encrypted_frame(18B) || tag(32B)`. `tag` =
  `SHAKE256(ss || encrypted_frame, 32)` (a keyed XOF tag — a NEW assumption vs the old HMAC-SHA256
  sim; chosen so the independent SHAKE primitive covers both rejection-key and tag).
- **Frame** = the audited 18-byte telecommand (magic `SPAC`, seq, subsystem, opcode, 2×param, CRC16).
- **Retry policy:** up to `RETRY_MAX` retransmissions. **Each retry redraws an INDEPENDENT channel
  fault from the deterministic schedule** — so retries are MEANINGFUL (a persistently bad channel
  exhausts retries; a transient one clears). This is the key repair of the audited tautology.
- **Timeout:** each attempt has a logical delivery deadline `D`. A `delay` fault with latency > `D`,
  or a `loss`, consumes the attempt as a timeout. Reordering/duplication are resolved by the seq
  window + a dedup set.
- **Termination:** first attempt that reaches ESTABLISHED, else after `RETRY_MAX` attempts a
  terminal outcome per §4. Every session yields exactly one ledger record.

## 7. Channel fault classes (deterministic parameters from SHAKE-256 PRF)
bit_corruption · truncation/malformed_framing · packet_loss · delay(→timeout) · duplication ·
reordering · interruption(→retry_exhaustion). No-fault baseline = clean channel (must yield
`KEY_ESTABLISHED`, crypto VALID). Each scheduled trial records injection attempt, activation,
delivery effect, state transitions, crypto verdict, terminal outcome, retry count, completion.

## 8. Newly introduced assumptions (flagged, not presented as established)
(a) meaningful-retry channel redraw; (b) logical delivery deadline `D` (not RF timing);
(c) SHAKE-256 keyed tag instead of HMAC-SHA256; (d) single-command session; (e) independent
derandomized KEM via liboqs `*_derand` for replay. All are modeling choices for this abstract
emulator, documented here and in the manifest.
