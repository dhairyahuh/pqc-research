#!/usr/bin/env python3
"""Phase 3 statistics: protocol-outcome counts with denominators + Wilson 95% CIs,
crypto verdict as a separate dimension, and per-suite breakdown. Exits nonzero if any
INCONCLUSIVE record exists (gate)."""
import json, sys, math
from collections import Counter

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (p, max(0.0, c-h), min(1.0, c+h))

recs = [json.loads(l) for l in open(sys.argv[1])]
N = len(recs)
oc = Counter(r["protocol_outcome"] for r in recs)
cc = Counter(r["crypto_verdict"] for r in recs)
L = ["# Phase 3 channel-fault — outcome statistics\n",
     f"- total sessions: {N}", f"- INCONCLUSIVE: {oc.get('INCONCLUSIVE',0)} (gate: expect 0)\n",
     "## protocol_outcome (overall, Wilson 95% CI)"]
for k in sorted(oc):
    p, lo, hi = wilson(oc[k], N)
    L.append(f"- {k}: {oc[k]}/{N} = {p*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%]")
L.append("\n## crypto_verdict (SEPARATE dimension — not a protocol outcome)")
for k in sorted(cc): L.append(f"- {k}: {cc[k]}")
L.append("\n## per-suite protocol_outcome")
for s in sorted(set(r["suite"] for r in recs)):
    rs = [r for r in recs if r["suite"] == s]
    d = Counter(r["protocol_outcome"] for r in rs)
    L.append(f"- {s} (n={len(rs)}): " + ", ".join(f"{k}={v}" for k, v in sorted(d.items())))
L.append("\n_Note: no statistical-significance or causal claim; counts describe a deterministic "
         "software emulator. Not real radio-link behavior, space qualification, or radiation._")
report = "\n".join(L) + "\n"
open(sys.argv[2], "w").write(report)
print(report)
sys.exit(0 if oc.get("INCONCLUSIVE", 0) == 0 else 4)
