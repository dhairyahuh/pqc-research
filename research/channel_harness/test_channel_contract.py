#!/usr/bin/env python3
"""Phase 3 Gate 3 — negative/invariant tests for the channel protocol harness.
Exit 0 iff every invariant holds. Verifies the SPEC precedence rules, not just that
the campaign runs. Run under the system python3 (deterministic; no network)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import channel_campaign as C

fails = 0
def chk(cond, msg):
    global fails
    print(("  ok  : " if cond else "  FAIL: ") + msg)
    if not cond: fails += 1

def session(name, fclass, persistent, n=5):
    return [C.run_session(i, 99, name, fclass, persistent) for i in range(n)]

# 1. timeout must NOT be recorded as a cryptographic failure
for r in session("DELAY_P", "DELAY", True):
    chk(r["protocol_outcome"] == C.TIMEOUT, "persistent delay -> TIMEOUT_RETRY_EXHAUSTED")
    chk(r["crypto_verdict"] == "UNAVAILABLE", "timeout has NO crypto verdict (not a crypto failure)")

# 2. a cryptographic rejection must NOT be recorded as a timeout
for r in session("BIT_P", "BIT_CORRUPTION", True):
    chk(r["protocol_outcome"] == C.ABORT, "persistent bit-corruption -> PROTOCOL_ABORT")
    chk(r["crypto_verdict"] == "REJECT", "crypto mismatch recorded as REJECT, not TIMEOUT")

# 3. invalid/malformed message is a protocol-parse failure, crypto unavailable
for r in session("TRUNC_P", "TRUNCATION", True):
    chk(r["protocol_outcome"] == C.MALFORMED, "persistent truncation -> MALFORMED_MESSAGE")
    chk(r["crypto_verdict"] == "UNAVAILABLE", "truncated frame never reaches decaps")
chk(C.parse_frame(b"\x00" * 10, (0, 9999)) == "bad_length", "short frame -> bad_length")
chk(C.parse_frame(b"XXXX" + b"\x00" * 14, (0, 9999)) == "bad_magic", "wrong magic -> bad_magic")

# 4. no retry after a terminal success; retry_count bounded by RETRY_MAX
for r in session("CLEAN", "CLEAN", False):
    chk(r["protocol_outcome"] == C.KEY_ESTABLISHED and r["retry_count"] == 0,
        "clean channel establishes on first attempt, 0 retries")
for r in session("LOSS_T", "PACKET_LOSS", False):
    chk(r["protocol_outcome"] == C.RECOVERED and 1 <= r["retry_count"] <= C.RETRY_MAX,
        "transient loss recovers on a later attempt (meaningful retry, not tautological)")

# 5. complete accounting: every scheduled session yields exactly one record
recs = session("MIX", "BIT_CORRUPTION", True, n=17)
chk(len(recs) == 17, "every scheduled session produces exactly one ledger record")

# 6. protocol/crypto separation is consistent. Non-delivery (lost/timeout) means no
#    decaps happened -> crypto UNAVAILABLE. MALFORMED may legitimately carry crypto VALID
#    (REORDER: valid ciphertext, but stale sequence rejected by the protocol) but never REJECT.
all_recs = []
for nm, fc, p in C.SUITES:
    all_recs += session(nm, fc, p, n=6)
bad = [r for r in all_recs if r["protocol_outcome"] in (C.LOST, C.TIMEOUT)
       and r["crypto_verdict"] != "UNAVAILABLE"]
chk(not bad, "non-delivery (lost/timeout) carries NO crypto verdict (separation holds)")
badm = [r for r in all_recs if r["protocol_outcome"] == C.MALFORMED and r["crypto_verdict"] == "REJECT"]
chk(not badm, "a protocol parse failure is never mislabeled as a crypto REJECT")
chk(any(r["protocol_outcome"] == C.MALFORMED and r["crypto_verdict"] == "VALID" for r in all_recs),
    "reorder shows crypto VALID + protocol MALFORMED (crypto/protocol layers kept separate)")
bad2 = [r for r in all_recs if r["protocol_outcome"] in (C.KEY_ESTABLISHED, C.RECOVERED)
        and r["crypto_verdict"] != "VALID"]
chk(not bad2, "established/recovered sessions always have crypto VALID (no silent accept)")
bad3 = [r for r in all_recs if r["protocol_outcome"] == C.ABORT and r["crypto_verdict"] != "REJECT"]
chk(not bad3, "aborts are driven by a crypto REJECT, never by VALID")

# 7. determinism: two runs of the same session are identical
a = C.run_session(3, 1, "BIT_CORRUPTION_PERSISTENT", "BIT_CORRUPTION", True)
b = C.run_session(3, 1, "BIT_CORRUPTION_PERSISTENT", "BIT_CORRUPTION", True)
chk(a == b, "deterministic: identical inputs -> identical record")

print("== %s (%d failures) ==" % ("FAILED" if fails else "PASSED", fails))
sys.exit(1 if fails else 0)
