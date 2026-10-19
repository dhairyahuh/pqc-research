#!/usr/bin/env python3
"""Generate publication-quality figures + tables for the Phase 2-4 consolidated report,
computed DIRECTLY from the verified raw JSONL datasets (same files the audit verified).
Figures -> figures/, tables (md+csv) -> tables/. Deterministic bootstrap (fixed seed).
Frame-relative; no physical/causal claim implied by any figure."""
import os, json
os.environ.setdefault("MPLCONFIGDIR", os.environ.get("TMPDIR", "/tmp") + "/mpl")
os.makedirs(os.environ["MPLCONFIGDIR"], exist_ok=True)
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

R = "research/results"; FIG = "research/phase2_4_report/figures"; TAB = "research/phase2_4_report/tables"
os.makedirs(FIG, exist_ok=True); os.makedirs(TAB, exist_ok=True)
def jsonl(p): return [json.loads(l) for l in open(p)]
# colorblind-safe (Okabe-Ito subset), light background
CB = {"blue":"#0072B2","orange":"#E69F00","green":"#009E73","red":"#D55E00",
      "grey":"#999999","purple":"#CC79A7","sky":"#56B4E9"}
plt.rcParams.update({"figure.dpi":140,"font.size":11,"axes.spines.top":False,
                     "axes.spines.right":False,"axes.grid":True,"grid.alpha":0.25})

def wtable(name, header, rows):
    with open(f"{TAB}/{name}.csv","w") as f:
        f.write(",".join(header)+"\n"); [f.write(",".join(map(str,r))+"\n") for r in rows]
    with open(f"{TAB}/{name}.md","w") as f:
        f.write("| "+" | ".join(header)+" |\n|"+"|".join(["---"]*len(header))+"|\n")
        [f.write("| "+" | ".join(map(str,r))+" |\n") for r in rows]

# ---- load ----
p2 = jsonl(f"{R}/phase2_mem_logical_v1/raw.jsonl")
p3 = jsonl(f"{R}/phase3_channel_v1/raw.jsonl")
p4 = jsonl(f"{R}/phase4_combined_v1/raw.jsonl")
seeds = {}
for r in p4: seeds.setdefault(r["seed"], {})[r["condition"]] = r
ids = sorted(seeds); C = ("C00","C10","C01","C11")
Y = {c: np.array([seeds[s][c]["established"] for s in ids], float) for c in C}
rng = np.random.default_rng(20261010); n=len(ids); B=10000
idx = rng.integers(0,n,size=(B,n))
def bci(a): b=a[idx].mean(1); return a.mean(), np.percentile(b,2.5), np.percentile(b,97.5)
pstat = {c: bci(Y[c]) for c in C}

# ---- FIG 1: per-condition completion with 95% CI ----
fig,ax=plt.subplots(figsize=(6,4))
labels=["C00\nneither","C10\nmem only","C01\nchan only","C11\nboth"]
vals=[pstat[c][0]*100 for c in C]
err=[[(pstat[c][0]-pstat[c][1])*100 for c in C],[(pstat[c][2]-pstat[c][0])*100 for c in C]]
ax.bar(labels,vals,color=[CB["grey"],CB["blue"],CB["orange"],CB["red"]],
       yerr=err,capsize=5,edgecolor="white")
for i,v in enumerate(vals): ax.text(i,v+2,f"{v:.1f}%",ha="center",fontsize=10)
ax.set_ylabel("P(key established) %"); ax.set_ylim(0,108)
ax.set_title("Phase 4: session completion by condition (N=500, 95% bootstrap CI)")
fig.tight_layout(); fig.savefig(f"{FIG}/fig1_completion.png"); plt.close(fig)

# ---- FIG 2: interaction overall + conditional, with difference ----
d={s: seeds[s]["C11"]["established"]-seeds[s]["C10"]["established"]
      -seeds[s]["C01"]["established"]+seeds[s]["C00"]["established"] for s in ids}
P=[s for s in ids if seeds[s]["C11"]["channel_persistent"]==1]
T=[s for s in ids if seeds[s]["C11"]["channel_persistent"]==0]
dov=Y["C11"].mean()-Y["C10"].mean()-Y["C01"].mean()+Y["C00"].mean()
bdov=Y["C11"][idx].mean(1)-Y["C10"][idx].mean(1)-Y["C01"][idx].mean(1)+Y["C00"][idx].mean(1)
dPa=np.array([d[s] for s in P]); dTa=np.array([d[s] for s in T])
iP=rng.integers(0,len(P),(B,len(P))); iT=rng.integers(0,len(T),(B,len(T)))
bP=dPa[iP].mean(1); bT=dTa[iT].mean(1); bdiff=bP-bT
def ci(a): return np.percentile(a,2.5),np.percentile(a,97.5)
fig,ax=plt.subplots(figsize=(6.2,4))
names=["Overall","Channel\nPERSISTENT","Channel\nTRANSIENT","Diff (P - T)"]
pts=[dov,dPa.mean(),dTa.mean(),dPa.mean()-dTa.mean()]
cis=[ci(bdov),ci(bP),ci(bT),ci(bdiff)]
yerr=[[pts[i]-cis[i][0] for i in range(4)],[cis[i][1]-pts[i] for i in range(4)]]
ax.errorbar(names,pts,yerr=yerr,fmt="o",color=CB["blue"],capsize=5,markersize=7)
ax.axhline(0,color=CB["grey"],lw=1,ls="--")
for i,v in enumerate(pts): ax.text(i,v+0.03,f"{v:+.3f}",ha="center",fontsize=9)
ax.set_ylabel("interaction  Δ = p11−p10−p01+p00"); ax.set_ylim(-0.1,0.6)
ax.set_title("Phase 4: interaction (F-conditional) — masking is persistent-channel only")
fig.tight_layout(); fig.savefig(f"{FIG}/fig2_interaction.png"); plt.close(fig)

# ---- FIG 3: joint sensitivity heatmap ----
def cm(md,cp,c):
    v=[seeds[s][c]["established"] for s in ids if seeds[s]["C11"]["mem_duration"]==md and seeds[s]["C11"]["channel_persistent"]==cp]
    return np.mean(v) if v else np.nan
cell={(md,cp):{c:cm(md,cp,c) for c in C} for md in ("TRANSIENT","PERSISTENT") for cp in (0,1)}
ws=[0.25,0.5,0.75]; G=np.zeros((3,3))
for i,wm in enumerate(ws):
    for j,wc in enumerate(ws):
        w={("TRANSIENT",0):(1-wm)*(1-wc),("TRANSIENT",1):(1-wm)*wc,("PERSISTENT",0):wm*(1-wc),("PERSISTENT",1):wm*wc}
        pp={c:sum(w[k]*cell[k][c] for k in w) for c in C}
        G[i,j]=pp["C11"]-pp["C10"]-pp["C01"]+pp["C00"]
fig,ax=plt.subplots(figsize=(5.2,4.3))
im=ax.imshow(G,cmap="viridis",origin="lower",aspect="auto")
ax.set_xticks(range(3),[f"{w}" for w in ws]); ax.set_yticks(range(3),[f"{w}" for w in ws])
ax.set_xlabel("P(channel persistent)"); ax.set_ylabel("P(memory persistent)")
for i in range(3):
    for j in range(3): ax.text(j,i,f"{G[i,j]:+.3f}",ha="center",va="center",color="white",fontsize=9)
ax.set_title("Phase 4: joint-weight sensitivity of Δ (sign stable > 0)")
fig.colorbar(im,label="Δ"); fig.tight_layout(); fig.savefig(f"{FIG}/fig3_sensitivity.png"); plt.close(fig)

# ---- FIG 4: masking breakdown ----
c11=[seeds[s]["C11"] for s in ids]
mk=[r for r in c11 if r["mem_injection_status"]=="MASKED_BY_CHANNEL"]
av=[r for r in c11 if r["mem_injection_status"]=="ACTIVATED"]
fig,ax=plt.subplots(figsize=(5.6,4))
cats=["ACTIVATED","MASKED_BY_CHANNEL"]; tot=[len(av),len(mk)]; estd=[sum(r["established"] for r in av),sum(r["established"] for r in mk)]
x=np.arange(2)
ax.bar(x,tot,color=CB["sky"],label="C11 trials",edgecolor="white")
ax.bar(x,estd,color=CB["green"],label="of which established",edgecolor="white")
for i in range(2): ax.text(i,tot[i]+6,f"{tot[i]}",ha="center"); ax.text(i,estd[i]+6,f"{estd[i]}",ha="center",fontsize=9,color=CB["green"])
ax.set_xticks(x,cats); ax.set_ylabel("count (of |C11|=500)"); ax.legend()
ax.set_title("Phase 4: masking — masked ≠ recovered (completion is channel-driven)")
fig.tight_layout(); fig.savefig(f"{FIG}/fig4_masking.png"); plt.close(fig)

# ---- FIG 5: isolated-arm distributions ----
oc2=Counter(r["terminal_outcome"] for r in p2); oc3=Counter(r["protocol_outcome"] for r in p3)
fig,(a1,a2)=plt.subplots(1,2,figsize=(11,4.2))
k2=sorted(oc2,key=lambda k:-oc2[k]); a1.bar(range(len(k2)),[oc2[k] for k in k2],color=CB["blue"],edgecolor="white")
a1.set_xticks(range(len(k2)),k2,rotation=35,ha="right",fontsize=8); a1.set_title("Phase 2 memory (N=900) terminal outcomes")
k3=sorted(oc3,key=lambda k:-oc3[k]); a2.bar(range(len(k3)),[oc3[k] for k in k3],color=CB["orange"],edgecolor="white")
a2.set_xticks(range(len(k3)),k3,rotation=35,ha="right",fontsize=8); a2.set_title("Phase 3 channel (N=600) protocol outcomes")
fig.tight_layout(); fig.savefig(f"{FIG}/fig5_isolated.png"); plt.close(fig)

# ---- tables ----
wtable("table_phase4_conditions",["condition","P_established_pct","ci_lo_pct","ci_hi_pct","n"],
       [[c,f"{pstat[c][0]*100:.1f}",f"{pstat[c][1]*100:.1f}",f"{pstat[c][2]*100:.1f}",n] for c in C])
wtable("table_interaction",["estimand","point","ci_lo","ci_hi","n"],
       [["Delta_overall",f"{dov:+.4f}",f"{ci(bdov)[0]:+.4f}",f"{ci(bdov)[1]:+.4f}",n],
        ["Delta_persistent",f"{dPa.mean():+.4f}",f"{ci(bP)[0]:+.4f}",f"{ci(bP)[1]:+.4f}",len(P)],
        ["Delta_transient",f"{dTa.mean():+.4f}",f"{ci(bT)[0]:+.4f}",f"{ci(bT)[1]:+.4f}",len(T)],
        ["Delta_P_minus_T",f"{dPa.mean()-dTa.mean():+.4f}",f"{ci(bdiff)[0]:+.4f}",f"{ci(bdiff)[1]:+.4f}",n]])
wtable("table_sensitivity",["P_mem_persist","P_chan_persist=0.25","0.50","0.75"],
       [[ws[i]]+[f"{G[i,j]:+.3f}" for j in range(3)] for i in range(3)])
wtable("table_phase2_outcomes",["terminal_outcome","count"],[[k,oc2[k]] for k in k2])
wtable("table_phase3_outcomes",["protocol_outcome","count"],[[k,oc3[k]] for k in k3])
print("figures:",sorted(os.listdir(FIG)))
print("tables:",sorted(os.listdir(TAB)))
print(f"masking {len(mk)}/500; established masked {sum(r['established'] for r in mk)} activated {sum(r['established'] for r in av)}")
