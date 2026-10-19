#!/usr/bin/env python3
"""Phase 4 JOINT-distribution sensitivity + masking accounting (design-review, EXPLORATORY).
Reads a combined jsonl, pairs the four conditions by seed, and reports:
  - overall Delta with paired bootstrap CI over seeds (frame-relative);
  - Delta over a JOINT grid reweighting memory-duration x channel-persistence (2x2 strata);
  - conditional Delta by channel-persistence, config, and blocking-vs-nonblocking channel class;
  - masking accounting (MASKED_BY_CHANNEL kept separate from activated/detected/recovered/safe).
Does NOT constitute confirmatory analysis. Usage: combined_sensitivity.py <jsonl> [--B N]
"""
import json, sys, numpy as np
from collections import Counter

rows = [json.loads(l) for l in open(sys.argv[1])]
B = int(sys.argv[sys.argv.index("--B")+1]) if "--B" in sys.argv else 5000
bs = {}
for r in rows: bs.setdefault(r["seed"], {})[r["condition"]] = r
C = ("C00","C10","C01","C11")
seeds = [s for s,d in bs.items() if all(c in d for c in C)
         and not any(d[c]["protocol_outcome"]=="INCONCLUSIVE" or d[c]["excluded"] for c in C)]
def arr(c): return np.array([bs[s][c]["established"] for s in seeds], float)
A = {c: arr(c) for c in C}
def delta_of(p): return p["C11"]-p["C10"]-p["C01"]+p["C00"]
pbar = {c: A[c].mean() for c in C}
d0 = delta_of(pbar)
rng = np.random.default_rng(20261010); n=len(seeds)
idx = rng.integers(0,n,size=(B,n))
bd = A["C11"][idx].mean(1)-A["C10"][idx].mean(1)-A["C01"][idx].mean(1)+A["C00"][idx].mean(1)
print(f"paired seeds n={n}; Delta_hat={d0:+.4f}  bootstrap95 [{np.percentile(bd,2.5):+.4f},{np.percentile(bd,97.5):+.4f}]")
for c in C: print(f"  {c} P(est)={pbar[c]*100:.1f}%")

# ---- JOINT grid: reweight P(mem_duration=PERSISTENT)=wm and P(channel_persistent)=wc ----
def cellmean(mdur, chp, c):
    v=[bs[s][c]["established"] for s in seeds
       if bs[s]["C11"]["mem_duration"]==mdur and bs[s]["C11"]["channel_persistent"]==chp]
    return (np.mean(v) if v else float("nan")), len(v)
cells={(md,cp):{c:cellmean(md,cp,c)[0] for c in C} for md in ("TRANSIENT","PERSISTENT") for cp in (0,1)}
cov ={(md,cp):cellmean(md,cp,"C11")[1] for md in ("TRANSIENT","PERSISTENT") for cp in (0,1)}
print("joint-cell coverage (seeds):", {k:cov[k] for k in cov})
grid=[]
print("JOINT grid Delta  [rows wm=P(mem PERSIST), cols wc=P(chan PERSIST)]:")
for wm in (0.25,0.5,0.75):
    line=[]
    for wc in (0.25,0.5,0.75):
        w={("TRANSIENT",0):(1-wm)*(1-wc),("TRANSIENT",1):(1-wm)*wc,
           ("PERSISTENT",0):wm*(1-wc),("PERSISTENT",1):wm*wc}
        p={c:sum(w[k]*cells[k][c] for k in w) for c in C}
        dd=delta_of(p); grid.append(dd); line.append(f"{dd:+.3f}")
    print(f"  wm={wm}: "+"  ".join(line))
print(f"JOINT grid Delta range: [{min(grid):+.4f}, {max(grid):+.4f}]  sign stable>0: {min(grid)>0}")

# ---- conditional Delta by strata ----
def cond_delta(pred,label):
    ss=[s for s in seeds if pred(s)]
    if len(ss)<8: print(f"  [{label}] n={len(ss)} (insufficient)"); return
    p={c:np.mean([bs[s][c]["established"] for s in ss]) for c in C}
    print(f"  [{label}] n={len(ss)} Delta={delta_of(p):+.4f}")
print("conditional Delta by strata:")
cond_delta(lambda s: bs[s]['C11']['channel_persistent']==1,"channel PERSISTENT")
cond_delta(lambda s: bs[s]['C11']['channel_persistent']==0,"channel TRANSIENT")
for cfg in ("BASELINE","TFIB_REF","TFIB_META"):
    cond_delta(lambda s,cfg=cfg: bs[s]['C11']['config']==cfg, f"config={cfg}")
block={'PACKET_LOSS','DELAY','INTERRUPTION','TRUNCATION'}
cond_delta(lambda s: bs[s]['C11']['channel_class'] in block,"channel=blocking")
cond_delta(lambda s: bs[s]['C11']['channel_class'] not in block,"channel=non-blocking")

# ---- masking accounting (C11 only; denominator = memory-armed AND channel-armed = C11) ----
c11=[bs[s]['C11'] for s in seeds]
st=Counter(r['mem_injection_status'] for r in c11)
masked=[r for r in c11 if r['mem_injection_status']=='MASKED_BY_CHANNEL']
activ =[r for r in c11 if r['mem_injection_status']=='ACTIVATED']
print(f"MASKING (denominator = |C11| = {len(c11)}): status={dict(st)}")
print(f"  masking rate = {len(masked)}/{len(c11)} = {len(masked)/len(c11)*100:.1f}%")
print(f"  established among MASKED  = {sum(r['established'] for r in masked)}/{len(masked)}")
print(f"  established among ACTIVATED= {sum(r['established'] for r in activ)}/{len(activ)}")
