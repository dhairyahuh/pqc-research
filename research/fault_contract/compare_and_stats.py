#!/usr/bin/env python3
"""Phase 2 matched-baseline comparison + statistics (gates G1-G5 support).

Joins the new v1 JSONL dataset against the historical Step 2C-A CSV by trial_id,
verifies the real cryptographic facts are identical (matched baseline), checks the
documented outcome-class migration mapping, and reports outcome counts with
Wilson 95% CIs and a Clopper-Pearson upper bound for 0-SDC. Exits nonzero if any
matched-baseline mismatch is found (gate G4).
"""
import csv, json, math, sys

MIGRATE = {
    "CLEAN_SUCCESS": "CLEAN_COMPLETED",
    "GENUINE_RECOVERY": "RECOVERED",
    "SAFE_FAIL_STOP": "SAFE_FAIL_DETECTED",
    "LOCAL_BLIND_FO_CONTAINED": "SAFE_FAIL_FO_CONTAINED",
    "INEFFECTIVE_FAULT_VALID": "INEFFECTIVE",
}

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = (z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / d
    return (p, max(0.0, c-h), min(1.0, c+h))

def cp_upper(k, n, alpha=0.025):
    # one-sided Clopper-Pearson upper bound; for k=0 -> 1-alpha**(1/n)
    try:
        from scipy.stats import beta
        return 1.0 if n == 0 else float(beta.ppf(1-alpha, k+1, n-k))
    except Exception:
        return 1.0 if n == 0 else 1 - alpha**(1.0/n)

def main():
    new_path, hist_path, out_md = sys.argv[1], sys.argv[2], sys.argv[3]
    new = {}
    with open(new_path) as f:
        for line in f:
            r = json.loads(line); new[r["trial_id"]] = r
    hist = {}
    with open(hist_path) as f:
        for r in csv.DictReader(f):
            hist[int(r["trial_id"])] = r

    mism = []
    map_bad = []
    both = sorted(set(new) & set(hist))
    for i in both:
        n, h = new[i], hist[i]
        # alignment keys
        if (n["config"] != h["config"] or n["suite"] != h["fault_suite"] or
            n["stage"] != int(h["stage"]) or n["butterfly"] != int(h["butterfly"]) or
            n["bit"] != int(h["bit"]) or n["persistent"] != int(h["persistent"])):
            mism.append((i, "alignment")); continue
        # crypto facts
        if (n["ss_match"] != int(h["output_correct"]) or
            n["rej_match"] != int(h["implicit_rejection"]) or
            n["status"].lower() != ("0x%08x" % int(h["final_status"], 16)).lower()):
            mism.append((i, "crypto_fact")); continue
        # migration mapping
        exp = MIGRATE.get(h["outcome_class"])
        if exp is not None and n["terminal_outcome"] != exp:
            map_bad.append((i, h["outcome_class"], n["terminal_outcome"]))

    # outcome distribution + activated denominators
    from collections import Counter
    dist = Counter(r["terminal_outcome"] for r in new.values())
    activated = [r for r in new.values() if r["injection_status"] == "ACTIVATED"]
    nact = len(activated)
    nsdc = sum(1 for r in activated if r["terminal_outcome"] == "SDC")
    det = sum(1 for r in activated if r["monitor_detected"] == 1)
    inconclusive = dist.get("INCONCLUSIVE", 0)

    lines = []
    lines.append("# Phase 2 — matched-baseline comparison & statistics\n")
    lines.append(f"- new records: {len(new)}; historical rows: {len(hist)}; joined: {len(both)}")
    lines.append(f"- **G4 crypto/alignment mismatches: {len(mism)}** (expect 0)")
    lines.append(f"- migration-mapping mismatches: {len(map_bad)} (expect 0)")
    lines.append(f"- **G3 INCONCLUSIVE outcomes: {inconclusive}** (expect 0)")
    lines.append(f"- activated trials: {nact}; locally detected: {det}; SDC: {nsdc}\n")
    p, lo, hi = wilson(det, nact)
    lines.append(f"- detection rate among activated: {det}/{nact} = {p:.4f} "
                 f"(Wilson 95% CI [{lo:.4f}, {hi:.4f}])")
    lines.append(f"- SDC among activated: {nsdc}/{nact}; one-sided 97.5% upper bound = "
                 f"{cp_upper(nsdc, nact):.5f} (0 observed SDC is NOT 0 risk)\n")
    lines.append("## terminal_outcome distribution (all trials)")
    for k in sorted(dist):
        lines.append(f"- {k}: {dist[k]}")
    if mism:
        lines.append("\n## MISMATCHES (first 20)"); lines += [f"- {m}" for m in mism[:20]]
    if map_bad:
        lines.append("\n## MIGRATION MISMATCHES (first 20)"); lines += [f"- {m}" for m in map_bad[:20]]

    report = "\n".join(lines) + "\n"
    with open(out_md, "w") as f: f.write(report)
    print(report)
    gates_ok = (len(mism) == 0 and len(map_bad) == 0 and inconclusive == 0)
    print("GATES G3+G4:", "PASS" if gates_ok else "FAIL")
    sys.exit(0 if gates_ok else 4)

if __name__ == "__main__":
    main()
