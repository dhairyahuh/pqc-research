#!/usr/bin/env python3
"""Independent audit of Phases 2-4. Recomputes every key metric DIRECTLY from the raw
JSONL records with freshly-written logic (does NOT import the campaign's own stats code),
verifies dataset hashes against manifests, and flags any discrepancy. Exit nonzero if any
check fails. Frame-relative; no physical/causal claim."""
import json, hashlib, sys
import numpy as np

ROOT = "research/results"
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def jsonl(p): return [json.loads(l) for l in open(p)]
FAIL = 0
def check(name, cond, detail=""):
    global FAIL
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" :: {detail}" if detail else ""))
    if not cond: FAIL += 1

print("== dataset hash verification vs manifests ==")
MAN = {
 "phase2": (f"{ROOT}/phase2_mem_logical_v1/raw.jsonl", f"{ROOT}/phase2_mem_logical_v1/manifest.json"),
 "phase3": (f"{ROOT}/phase3_channel_v1/raw.jsonl", f"{ROOT}/phase3_channel_v1/manifest.json"),
 "phase4": (f"{ROOT}/phase4_combined_v1/raw.jsonl", f"{ROOT}/phase4_combined_v1/manifest_confirmatory.json"),
}
for name, (raw, man) in MAN.items():
    rec = json.load(open(man))["outputs"]["raw.jsonl"]
    check(f"{name} raw.jsonl hash == manifest", sha(raw) == rec, sha(raw)[:16])

print("\n== Phase 2 (memory, logical-value) recomputed from raw ==")
p2 = jsonl(MAN["phase2"][0])
from collections import Counter
oc2 = Counter(r["terminal_outcome"] for r in p2)
act = [r for r in p2 if r["injection_status"] == "ACTIVATED"]
check("Phase2 N=900", len(p2) == 900, str(len(p2)))
check("Phase2 activated=750", len(act) == 750, str(len(act)))
check("Phase2 SDC=0", oc2.get("SDC", 0) == 0)
check("Phase2 RECOVERED=250", oc2.get("RECOVERED") == 250, str(oc2.get("RECOVERED")))
check("Phase2 SAFE_FAIL_DETECTED=350", oc2.get("SAFE_FAIL_DETECTED") == 350, str(oc2.get("SAFE_FAIL_DETECTED")))
check("Phase2 SAFE_FAIL_FO_CONTAINED=147", oc2.get("SAFE_FAIL_FO_CONTAINED") == 147, str(oc2.get("SAFE_FAIL_FO_CONTAINED")))
check("Phase2 INEFFECTIVE=3", oc2.get("INEFFECTIVE") == 3, str(oc2.get("INEFFECTIVE")))
det = sum(1 for r in act if r["monitor_detected"] == 1)
check("Phase2 detected-among-activated=600", det == 600, str(det))

print("\n== Phase 3 (channel) recomputed from raw ==")
p3 = jsonl(MAN["phase3"][0])
oc3 = Counter(r["protocol_outcome"] for r in p3)
check("Phase3 N=600", len(p3) == 600, str(len(p3)))
exp3 = {"KEY_ESTABLISHED":100,"RECOVERED_ON_RETRY":200,"MALFORMED_MESSAGE":100,
        "MESSAGE_LOST":100,"TIMEOUT_RETRY_EXHAUSTED":50,"PROTOCOL_ABORT":50}
for k,v in exp3.items(): check(f"Phase3 {k}={v}", oc3.get(k)==v, str(oc3.get(k)))
check("Phase3 no INCONCLUSIVE", oc3.get("INCONCLUSIVE",0)==0)
# AUDIT-APPEND
print("\n== Phase 4 (combined) independent reconstruction from raw ==")
p4 = jsonl(MAN["phase4"][0])
seeds = {}
for r in p4: seeds.setdefault(r["seed"], {})[r["condition"]] = r
C = ("C00","C10","C01","C11")
check("Phase4 2000 records", len(p4) == 2000, str(len(p4)))
check("Phase4 500 seeds", len(seeds) == 500, str(len(seeds)))
check("Phase4 every seed has 4 matched conditions",
      all(set(d) == set(C) for d in seeds.values()))
check("Phase4 no excluded", sum(r["excluded"] for r in p4) == 0)
check("Phase4 no INCONCLUSIVE", sum(r["protocol_outcome"]=="INCONCLUSIVE" for r in p4) == 0)
ids = sorted(seeds)
Y = {c: np.array([seeds[s][c]["established"] for s in ids], float) for c in C}
p = {c: Y[c].mean() for c in C}
delta = p["C11"] - p["C10"] - p["C01"] + p["C00"]
for c in C: print(f"    {c} P(est)={p[c]*100:.1f}%")
check("Phase4 p00==1.0", p["C00"] == 1.0)
check("Phase4 Delta_hat ~= +0.216", abs(delta - 0.216) < 1e-3, f"{delta:+.4f}")

# masking (denominator = |C11| = 500)
c11 = [seeds[s]["C11"] for s in ids]
masked = [r for r in c11 if r["mem_injection_status"] == "MASKED_BY_CHANNEL"]
activ  = [r for r in c11 if r["mem_injection_status"] == "ACTIVATED"]
check("Phase4 masking 203/500", len(masked) == 203, f"{len(masked)}/{len(c11)}")
check("Phase4 masked+activated==500", len(masked)+len(activ) == 500)
em = sum(r["established"] for r in masked); ea = sum(r["established"] for r in activ)
print(f"    established among MASKED={em}/{len(masked)}  among ACTIVATED={ea}/{len(activ)}")

# per-seed interaction d_i and conditional strata (channel persistence is per-seed)
d = {s: seeds[s]["C11"]["established"] - seeds[s]["C10"]["established"]
        - seeds[s]["C01"]["established"] + seeds[s]["C00"]["established"] for s in ids}
P = [s for s in ids if seeds[s]["C11"]["channel_persistent"] == 1]
T = [s for s in ids if seeds[s]["C11"]["channel_persistent"] == 0]
dP = np.mean([d[s] for s in P]); dT = np.mean([d[s] for s in T])
maxabsT = max(abs(d[s]) for s in T)
check("Phase4 conditional Delta_persistent ~= +0.419", abs(dP - 0.4186) < 2e-3, f"{dP:+.4f} n={len(P)}")
check("Phase4 transient interaction is a per-seed structural identity (all d_i==0)",
      maxabsT == 0, f"max|d_i|={maxabsT}, mean={dT:+.4f}")

# independent paired bootstrap for Delta (fresh RNG; expect agreement w/ recorded CI to ~0.005)
rng = np.random.default_rng(424242); n = len(ids); B = 10000
idx = rng.integers(0, n, size=(B, n))
bd = Y["C11"][idx].mean(1) - Y["C10"][idx].mean(1) - Y["C01"][idx].mean(1) + Y["C00"][idx].mean(1)
lo, hi = np.percentile(bd, 2.5), np.percentile(bd, 97.5)
print(f"    independent bootstrap Delta 95% CI = [{lo:+.4f}, {hi:+.4f}] (recorded [+0.180,+0.252])")
check("Phase4 bootstrap CI agrees with recorded (~0.005)", abs(lo-0.180)<6e-3 and abs(hi-0.252)<6e-3)

# #3 difference test: Delta_P - Delta_T with two-stratum bootstrap (resample within strata)
dPa = np.array([d[s] for s in P]); dTa = np.array([d[s] for s in T])
iP = rng.integers(0, len(P), size=(B, len(P))); iT = rng.integers(0, len(T), size=(B, len(T)))
diff = dPa[iP].mean(1) - dTa[iT].mean(1)
dlo, dhi = np.percentile(diff, 2.5), np.percentile(diff, 97.5)
print(f"    (Delta_P - Delta_T) point={dP-dT:+.4f}  bootstrap95=[{dlo:+.4f},{dhi:+.4f}]")
check("Phase4 persistent-vs-transient interaction difference CI excludes 0", dlo > 0,
      f"CI=[{dlo:+.4f},{dhi:+.4f}]")

# joint-distribution sensitivity recompute (2x2 strata) -> sign stability
def cm(md, cp, c):
    v = [seeds[s][c]["established"] for s in ids
         if seeds[s]["C11"]["mem_duration"]==md and seeds[s]["C11"]["channel_persistent"]==cp]
    return np.mean(v) if v else float("nan")
cell = {(md,cp): {c: cm(md,cp,c) for c in C} for md in ("TRANSIENT","PERSISTENT") for cp in (0,1)}
grid = []
for wm in (0.25,0.5,0.75):
    for wc in (0.25,0.5,0.75):
        w = {("TRANSIENT",0):(1-wm)*(1-wc),("TRANSIENT",1):(1-wm)*wc,
             ("PERSISTENT",0):wm*(1-wc),("PERSISTENT",1):wm*wc}
        pp = {c: sum(w[k]*cell[k][c] for k in w) for c in C}
        grid.append(pp["C11"]-pp["C10"]-pp["C01"]+pp["C00"])
print(f"    joint grid Delta range=[{min(grid):+.4f},{max(grid):+.4f}] sign>0 all={min(grid)>0}")
check("Phase4 joint-grid sign stable >0", min(grid) > 0, f"min={min(grid):+.4f}")

print(f"\n== AUDIT {'PASSED' if FAIL==0 else 'FAILED'} ({FAIL} discrepancies) ==")
sys.exit(1 if FAIL else 0)

