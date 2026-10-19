#!/usr/bin/env python3
"""Phase 4 FROZEN analysis (pre-registered before confirmatory). Pairs the four
conditions by seed (complete-case), estimates p00/p10/p01/p11 and the interaction
contrast Delta = p11 - p10 - p01 + p00, with nonparametric bootstrap CIs over SEEDS
(the i.i.d. Monte-Carlo unit). Frame-relative: CIs are sampling uncertainty over the
pre-registered fault distribution F, NOT physical fault rates. Usage:
  combined_stats.py <raw.jsonl> <out.md> [--label PILOT|CONFIRMATORY] [--B 10000]
"""
import json, sys, numpy as np

def main():
    path, out_md = sys.argv[1], sys.argv[2]
    label = "RUN"; B = 10000
    if "--label" in sys.argv: label = sys.argv[sys.argv.index("--label")+1]
    if "--B" in sys.argv: B = int(sys.argv[sys.argv.index("--B")+1])
    rows = [json.loads(l) for l in open(path)]
    byseed = {}
    for r in rows:
        byseed.setdefault(r["seed"], {})[r["condition"]] = r
    conds = ("C00", "C10", "C01", "C11")
    seeds, dropped = [], 0
    Y = {c: [] for c in conds}
    for s, d in sorted(byseed.items()):
        if any(c not in d for c in conds): dropped += 1; continue
        if any(d[c]["protocol_outcome"] == "INCONCLUSIVE" or d[c]["excluded"] for c in conds):
            dropped += 1; continue
        seeds.append(s)
        for c in conds: Y[c].append(d[c]["established"])
    n = len(seeds)
    arr = {c: np.array(Y[c], dtype=float) for c in conds}
    p = {c: (arr[c].mean() if n else float("nan")) for c in conds}
    delta_point = p["C11"] - p["C10"] - p["C01"] + p["C00"]
    # paired bootstrap over seeds
    rng = np.random.default_rng(20261010)
    if n:
        idx = rng.integers(0, n, size=(B, n))
        def boot(a): return a[idx].mean(axis=1)
        bp = {c: boot(arr[c]) for c in conds}
        bd = bp["C11"] - bp["C10"] - bp["C01"] + bp["C00"]
        ci = lambda x: (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)))
        pci = {c: ci(bp[c]) for c in conds}; dci = ci(bd)
    else:
        pci = {c: (float("nan"),)*2 for c in conds}; dci = (float("nan"),)*2
    from collections import Counter
    # masking accounting on the PAIRED seed set (denominator = |C11| paired = n).
    c11 = [byseed[s]["C11"] for s in seeds] if n else []
    status = Counter(r["mem_injection_status"] for r in c11)
    masked = [r for r in c11 if r["mem_injection_status"] == "MASKED_BY_CHANNEL"]
    activ  = [r for r in c11 if r["mem_injection_status"] == "ACTIVATED"]
    # conditional Delta by channel persistence (the stratum that drives interaction)
    def cond_delta(flag):
        ss = [s for s in seeds if byseed[s]["C11"]["channel_persistent"] == flag]
        if len(ss) < 8: return None, len(ss)
        pp = {c: np.mean([byseed[s][c]["established"] for s in ss]) for c in conds}
        return pp["C11"]-pp["C10"]-pp["C01"]+pp["C00"], len(ss)
    dP, nP = cond_delta(1); dT, nT = cond_delta(0)
    L = [f"# Phase 4 combined-fault — {label} statistics (frame-relative)\n",
         f"- seeds analysed (paired, complete-case): {n}; dropped seeds: {dropped}",
         f"- total condition-trials: {len(rows)}\n",
         "## per-condition P(key established) [bootstrap 95% CI over seeds]"]
    for c in conds:
        L.append(f"- {c}: {p[c]*100:.1f}%  [{pci[c][0]*100:.1f}%, {pci[c][1]*100:.1f}%]  (n={n})")
    L.append(f"\n## interaction  Delta = p11 - p10 - p01 + p00")
    L.append(f"- Delta_hat = {delta_point:+.4f}  [bootstrap 95% CI {dci[0]:+.4f}, {dci[1]:+.4f}]")
    L.append(f"- conditional on channel PERSISTENT: Delta={('%+.4f'%dP) if dP is not None else 'n/a'} (n={nP})")
    L.append(f"- conditional on channel TRANSIENT: Delta={('%+.4f'%dT) if dT is not None else 'n/a'} (n={nT})")
    L.append("\n## masking accounting — MASKED_BY_CHANNEL is NOT a recovered memory fault")
    L.append(f"- memory-injection status in C11 (denominator |C11|={len(c11)}): {dict(status)}")
    if c11:
        mrate = len(masked)/len(c11)*100
        L.append(f"- masking rate = {len(masked)}/{len(c11)} = {mrate:.1f}% "
                 f"(memory armed + channel armed, memory never reached activation)")
        if masked: L.append(f"- established among MASKED = {sum(r['established'] for r in masked)}/{len(masked)} "
                            f"(completion here is governed by the CHANNEL retry, not memory recovery)")
        if activ:  L.append(f"- established among ACTIVATED = {sum(r['established'] for r in activ)}/{len(activ)}")
    L.append("\n_Frame-relative Monte-Carlo estimand over the pre-registered distribution F. "
             "NOT a physical probability, significance, or causal claim. Logical-value memory + "
             "simulated channel only; no persistent-storage/radiation/RF/qualification claim._")
    rep = "\n".join(L) + "\n"
    open(out_md, "w").write(rep); print(rep)
    return 0

if __name__ == "__main__":
    sys.exit(main())
