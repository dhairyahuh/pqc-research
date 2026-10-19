#!/usr/bin/env python3
"""Phase 3 — isolated channel-fault campaign (deterministic, replayable).

Implements research/PROTOCOL_FAULT_MODEL_SPEC.md v1. Drives DETERMINISTIC ML-KEM-768
via liboqs *_derand symbols (ctypes), with an independent SHAKE-256 rejection-key
cross-check. Channel faults act only on the wire message; memory faults (Phase 2) are
NOT involved. Protocol outcome and crypto verdict are recorded as separate dimensions.
No historical file is read or written; outputs go to research/results/phase3_channel_v1/.
"""
import ctypes, hashlib, json, os, struct, sys
from collections import Counter

PROTOCOL_SCHEMA_VERSION = 1
PK, SK, CT, SS, KSEED, ESEED = 1184, 2400, 1088, 32, 64, 32
RETRY_MAX = 2
DELIVERY_DEADLINE = 100  # logical time units

# ---- liboqs deterministic KEM via ctypes (verified symbols present) ----------
_LIB = next((p for p in ["/opt/homebrew/lib/liboqs.dylib", "/usr/local/lib/liboqs.dylib",
             "/usr/lib/liboqs.dylib"] if os.path.exists(p)), None)
if not _LIB: raise RuntimeError("liboqs.dylib not found")
_oqs = ctypes.CDLL(_LIB); _oqs.OQS_init()
U8 = ctypes.POINTER(ctypes.c_uint8)
for fn in ("OQS_KEM_ml_kem_768_keypair_derand", "OQS_KEM_ml_kem_768_encaps_derand",
           "OQS_KEM_ml_kem_768_decaps"):
    getattr(_oqs, fn).restype = ctypes.c_int

def _buf(n, init=None):
    b = (ctypes.c_uint8 * n)()
    if init is not None: b[:] = init
    return b

def kem_keypair(seed64: bytes):
    pk, sk = _buf(PK), _buf(SK)
    rc = _oqs.OQS_KEM_ml_kem_768_keypair_derand(pk, sk, _buf(KSEED, seed64))
    if rc != 0: raise RuntimeError("keypair_derand rc=%d" % rc)
    return bytes(pk), bytes(sk)

def kem_encaps(pk: bytes, seed32: bytes):
    ct, ss = _buf(CT), _buf(SS)
    rc = _oqs.OQS_KEM_ml_kem_768_encaps_derand(ct, ss, _buf(PK, pk), _buf(ESEED, seed32))
    if rc != 0: raise RuntimeError("encaps_derand rc=%d" % rc)
    return bytes(ct), bytes(ss)

def kem_decaps(ct: bytes, sk: bytes):
    if len(ct) != CT: raise ValueError("ct length")  # truncated ct cannot be decapsulated
    ss = _buf(SS)
    rc = _oqs.OQS_KEM_ml_kem_768_decaps(ss, _buf(CT, ct), _buf(SK, sk))
    if rc != 0: raise RuntimeError("decaps rc=%d" % rc)
    return bytes(ss)

def shake(data: bytes, n: int = 32) -> bytes:
    return hashlib.shake_256(data).digest(n)

def reject_key(sk: bytes, ct: bytes) -> bytes:
    """Independent FIPS-203 implicit-rejection key J(z||c)=SHAKE256(z||c,32); z=sk[-32:]."""
    return shake(sk[SK - SS:] + ct, SS)

def prf(domain: str, *ints, n: int = 64) -> bytes:
    ctx = domain.encode() + b"|" + b"|".join(struct.pack(">q", int(i)) for i in ints)
    return shake(ctx, n)

# <!-- CH-APPEND -->
# ---- frame + receiver pipeline (abstract 18-byte telecommand) -----------------
def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
    return crc

VALID_CMDS = {1: (0x10, 0x11, 0x12), 2: (0x20, 0x21), 3: (0x30, 0x31)}

def build_frame(seq, sub=1, op=0x10, p1=45, p2=60000):
    body = struct.pack(">4sHBBii", b"SPAC", seq, sub, op, p1, p2)
    return body + struct.pack(">H", crc16(body))

def parse_frame(pt: bytes, seq_window):
    """Returns 'OK' or a MALFORMED reason string. Separate from crypto verdict."""
    if len(pt) != 18: return "bad_length"
    magic, seq, sub, op, p1, p2, crc = struct.unpack(">4sHBBiiH", pt)
    if magic != b"SPAC": return "bad_magic"
    if not (seq_window[0] <= seq <= seq_window[1]): return "seq_out_of_window"
    if sub not in VALID_CMDS or op not in VALID_CMDS[sub]: return "bad_command"
    if sub == 1 and not (-180 <= p1 <= 180): return "param_oob"
    if not (0 <= p2 <= 3600000): return "param_oob"
    if crc != crc16(pt[:16]): return "crc_mismatch"
    return "OK"

def stream_xor(key: bytes, data: bytes) -> bytes:
    ks, blk = b"", 0
    while len(ks) < len(data):
        ks += hashlib.sha256(key + struct.pack(">I", blk)).digest(); blk += 1
    return bytes(a ^ b for a, b in zip(data, ks[:len(data)]))

# ---- channel model: returns (delivered_bytes|None, effect, latency) ----------
def channel_apply(wire: bytes, fclass: str, active: bool, pseed: bytes):
    """active=False -> clean pass-through. Deterministic per (fclass, pseed)."""
    if not active or fclass == "CLEAN":
        return wire, "DELIVERED", 1
    r = int.from_bytes(pseed[:8], "big")
    if fclass == "PACKET_LOSS":      return None, "LOST", 0
    if fclass == "INTERRUPTION":     return None, "LINK_DOWN", 0
    if fclass == "DELAY":            return wire, "DELAYED", DELIVERY_DEADLINE + 1 + (r % 50)
    if fclass == "TRUNCATION":       return wire[:len(wire) - (1 + r % 64)], "TRUNCATED", 1
    if fclass == "REORDER":          return wire, "REORDERED", 1   # seq-window handles staleness
    if fclass == "DUPLICATION":      return wire, "DUPLICATED", 1  # dedup handled by receiver
    if fclass == "BIT_CORRUPTION":
        ba = bytearray(wire); pos = r % CT; ba[pos] ^= (1 << ((r >> 8) & 7))  # flip in KEM ct
        return bytes(ba), "CORRUPTED", 1
    return wire, "DELIVERED", 1
# <!-- CH-APPEND2 -->
BASE_SEQ = 5020
# protocol outcomes (spec v1 §3)
KEY_ESTABLISHED="KEY_ESTABLISHED"; RECOVERED="RECOVERED_ON_RETRY"; ABORT="PROTOCOL_ABORT"
MALFORMED="MALFORMED_MESSAGE"; LOST="MESSAGE_LOST"; TIMEOUT="TIMEOUT_RETRY_EXHAUSTED"
MISMATCH="CRYPTO_KEY_MISMATCH"; INCONCLUSIVE="INCONCLUSIVE"

def _attempt(a, trial, sid, fclass, active, pk, sk, ss_ground, ct_clean, window, seq):
    """Process one transmission attempt. Returns (kind, crypto_verdict, effect)."""
    pseed = prf("chan", trial, sid, a, n=16)
    use_seq = (seq - 100) if (active and fclass == "REORDER") else seq      # stale on reorder
    enc = stream_xor(ss_ground, build_frame(use_seq))
    tag = shake(ss_ground + enc, SS)
    wire = ct_clean + enc + tag
    delivered, effect, latency = channel_apply(wire, fclass, active, pseed)
    if delivered is None:                       return ("LOST", None, effect)
    if latency > DELIVERY_DEADLINE:             return ("TIMEOUT", None, effect)
    if len(delivered) < CT + 18 + SS:           return ("MALFORMED", None, effect)
    ct2, enc2, tag2 = delivered[:CT], delivered[CT:CT+18], delivered[CT+18:CT+18+SS]
    ss_sc = kem_decaps(ct2, sk)
    verdict = "VALID" if ss_sc == ss_ground else ("REJECT" if ss_sc == reject_key(sk, ct2) else "NEITHER")
    if shake(ss_sc + enc2, SS) != tag2:         return ("MISMATCH", verdict, effect)   # MAC fail
    reason = parse_frame(stream_xor(ss_sc, enc2), window)
    if reason != "OK":                          return ("MALFORMED", verdict, effect)
    return ("ESTABLISHED", verdict, effect)

def run_session(trial, sid, name, fclass, persistent):
    seed64 = prf("kem.kp", trial, n=KSEED); seed32 = prf("kem.enc", trial, n=ESEED)
    pk, sk = kem_keypair(seed64); ct_clean, ss_ground = kem_encaps(pk, seed32)
    seq = BASE_SEQ + (trial % 10); window = (seq - 2, seq + 32)
    armed = (fclass != "CLEAN")
    first_effect, last = None, None
    terminal, crypto = None, "UNAVAILABLE"
    attempts = 0
    for a in range(RETRY_MAX + 1):
        attempts += 1
        active = armed and (persistent or a == 0)
        kind, verdict, effect = _attempt(a, trial, sid, fclass, active, pk, sk, ss_ground, ct_clean, window, seq)
        if a == 0: first_effect = effect
        last = (kind, verdict, effect)
        if kind == "ESTABLISHED":
            crypto = verdict
            terminal = RECOVERED if a > 0 else KEY_ESTABLISHED
            break
        crypto = verdict or crypto
    if terminal is None:                         # exhausted without establishing (precedence §4)
        k = last[0]
        terminal = {"LOST": LOST, "TIMEOUT": TIMEOUT, "MALFORMED": MALFORMED,
                    "MISMATCH": ABORT}.get(k, INCONCLUSIVE)
        crypto = last[1] or crypto
    # injection status (Phase-2 contract concept)
    inj = "NOT_ARMED" if not armed else ("ACTIVATED" if first_effect not in (None, "DELIVERED") else "FAILED")
    completed = terminal in (KEY_ESTABLISHED, RECOVERED)
    return {
        "trial_id": trial, "suite": name, "channel_class": fclass,
        "persistent": int(persistent), "schema_version": PROTOCOL_SCHEMA_VERSION,
        "injection_status": inj, "first_delivery_effect": first_effect or "NONE",
        "crypto_verdict": crypto, "retry_count": attempts - 1,
        "protocol_outcome": terminal, "session_completed": int(completed),
    }

SUITES = [
    ("CLEAN_BASELINE", "CLEAN", False),
    ("BIT_CORRUPTION_TRANSIENT", "BIT_CORRUPTION", False),
    ("BIT_CORRUPTION_PERSISTENT", "BIT_CORRUPTION", True),
    ("TRUNCATION_TRANSIENT", "TRUNCATION", False),
    ("TRUNCATION_PERSISTENT", "TRUNCATION", True),
    ("PACKET_LOSS_TRANSIENT", "PACKET_LOSS", False),
    ("PACKET_LOSS_PERSISTENT", "PACKET_LOSS", True),
    ("DELAY_TRANSIENT", "DELAY", False),
    ("DELAY_PERSISTENT", "DELAY", True),
    ("DUPLICATION", "DUPLICATION", True),
    ("REORDER_PERSISTENT", "REORDER", True),
    ("INTERRUPTION_PERSISTENT", "INTERRUPTION", True),
]

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "research/results/phase3_channel_v1/raw.jsonl"
    per = int(sys.argv[3]) if (len(sys.argv) > 3 and sys.argv[2] == "--pilot") else 50
    os.makedirs(os.path.dirname(out), exist_ok=True)
    started = finalized = 0
    outc, cryptoc = Counter(), Counter()
    tid = 0
    with open(out, "w") as f:
        for sid, (name, fclass, persistent) in enumerate(SUITES):
            for _ in range(per):
                started += 1
                rec = run_session(tid, sid, name, fclass, persistent)
                finalized += 1; outc[rec["protocol_outcome"]] += 1; cryptoc[rec["crypto_verdict"]] += 1
                f.write(json.dumps(rec) + "\n"); tid += 1
    ledger_ok = (started == finalized == sum(outc.values()))
    inconclusive = outc.get(INCONCLUSIVE, 0)
    print("trials=%d finalized=%d ledger_ok=%s inconclusive=%d" % (started, finalized, ledger_ok, inconclusive))
    for k in sorted(outc): print("  %-26s %d" % (k, outc[k]))
    print("  crypto:", dict(cryptoc))
    print("wrote", out)
    return 0 if (ledger_ok and inconclusive == 0) else 3

if __name__ == "__main__":
    sys.exit(main())


