"""T2 - Event-locked socioemotional lift. Same machinery as the main content-fingerprint analysis
(peaks_taxonomy_sig.py): per-meeting density lift at reorganization events (RMSE > mean+2.33 SD) vs
baseline seconds, Wilcoxon signed-rank across meetings, Benjamini-Hochberg FDR WITHIN the 8-category
socioemotional family (never folded back into the original 41-category family). Also splits by Study
9's event classification (TRANSITION / INTERIOR_HANDOFF / INTERIOR_OTHER)."""
import glob, os, json
import numpy as np, pandas as pd
from collections import defaultdict
from scipy.stats import wilcoxon, kruskal

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
COD2 = f"{LSH}/data/codebooks2"
ACT4 = f"{LSH}/data/act4teams"
EVENTS_CSV = f"{LSH}/study9_initiators/data/events_initiators.csv"
OUT = os.path.dirname(__file__) + "/../data"
TCRIT = 2.33

BALES_CATS = ["bsolid", "btension", "bagree", "bdisagree", "btensh", "bantag"]
ACT4_CATS = ["pos", "neg"]
FAMILY = BALES_CATS + ACT4_CATS
VALENCE = {"bsolid": "+", "btension": "+", "bagree": "+", "pos": "+",
           "bdisagree": "-", "btensh": "-", "bantag": "-", "neg": "-"}


def load_cb(folder):
    d = {}
    for f in glob.glob(f"{folder}/*_passA.json"):
        mid = os.path.basename(f).replace("_passA.json", "")
        d[mid] = {int(w["t"]): w for w in json.load(open(f))["windows"]}
    return d


c2 = load_cb(COD2)
c4 = load_cb(ACT4)


def bh(pvals):
    p = np.array(pvals); n = len(p); order = np.argsort(p); ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]; out = np.empty(n); out[order] = np.clip(q, 0, 1)
    return out


# ---------------- main event-locked lift (mask/baseline, exactly as peaks_taxonomy_sig.py) ----------------
lifts = defaultdict(list)
win = lambda s: int(s // 90 * 90)
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    if mid not in c2 or mid not in c4:
        continue
    g = pd.read_csv(f); secs = g["second"].to_numpy(); x = g["rmse_g"].to_numpy(float)
    m = np.nanmean(x); sd = np.nanstd(x)
    mask = x > m + TCRIT * sd; base = ~mask & np.isfinite(x)
    if mask.sum() < 20 or base.sum() < 20:
        continue
    for cat in FAMILY:
        cd = c2[mid] if cat in BALES_CATS else c4[mid]
        dens = np.array([cd.get(win(s), {}).get(cat, 0) for s in secs], float)
        if not np.isfinite(dens).any() or dens.sum() == 0:
            continue
        lifts[cat].append(dens[mask].mean() - dens[base].mean())

rng = np.random.default_rng(1200)
rows = []
for cat in FAMILY:
    L = np.array(lifts.get(cat, [])); L = L[np.isfinite(L)]
    if len(L) < 15:
        continue
    p = wilcoxon(L, zero_method="wilcox", alternative="two-sided").pvalue if np.any(L != 0) else 1.0
    boots = np.array([rng.choice(L, size=len(L), replace=True).mean() for _ in range(2000)])
    ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])
    rows.append(dict(cat=cat, valence=VALENCE[cat], n=len(L), mean_lift=L.mean(),
                      ci_lo=ci_lo, ci_hi=ci_hi, pos_meetings=int((L > 0).sum()), p=p))
df = pd.DataFrame(rows).sort_values("mean_lift", ascending=False)
df["q_fdr"] = bh(df["p"].tolist())
df.to_csv(f"{OUT}/socioemotional_lifts.csv", index=False)
print("=" * 90); print("T2 — Event-locked socioemotional lift (8-category confirmatory family, BH-FDR within family)")
print("=" * 90)
for _, r in df.iterrows():
    star = "***" if r.q_fdr < .001 else "**" if r.q_fdr < .01 else "*" if r.q_fdr < .05 else "n.s."
    print(f"  {r['cat']:10} ({r.valence})  lift={r.mean_lift:+.4f}  {r.pos_meetings}/{r.n} mtgs same-dir  "
          f"p={r.p:.4f}  q={r.q_fdr:.4f}  {star}")

# ---------------- event-class split (Kruskal-Wallis per category, window-grain) ----------------
ev = pd.read_csv(EVENTS_CSV)
class_rows = []
for cat in FAMILY:
    groups = {"TRANSITION": [], "INTERIOR_HANDOFF": [], "INTERIOR_OTHER": []}
    for _, r in ev.iterrows():
        mid = r["mid"]
        if mid not in c2 or mid not in c4:
            continue
        cd = c2[mid] if cat in BALES_CATS else c4[mid]
        w = win(r["event_onset_s"])
        val = cd.get(w, {}).get(cat, None)
        if val is None:
            continue
        groups[r["event_class"]].append(val)
    ns = {k: len(v) for k, v in groups.items()}
    if all(n >= 15 for n in ns.values()):
        stat, p = kruskal(*groups.values())
    else:
        stat, p = np.nan, np.nan
    class_rows.append(dict(cat=cat, valence=VALENCE[cat],
                            mean_transition=np.mean(groups["TRANSITION"]) if groups["TRANSITION"] else np.nan,
                            mean_handoff=np.mean(groups["INTERIOR_HANDOFF"]) if groups["INTERIOR_HANDOFF"] else np.nan,
                            mean_other=np.mean(groups["INTERIOR_OTHER"]) if groups["INTERIOR_OTHER"] else np.nan,
                            n_transition=ns["TRANSITION"], n_handoff=ns["INTERIOR_HANDOFF"], n_other=ns["INTERIOR_OTHER"],
                            kruskal_H=stat, p=p))
cdf = pd.DataFrame(class_rows)
cdf["q_fdr"] = bh(cdf["p"].fillna(1.0).tolist())
cdf.to_csv(f"{OUT}/socioemotional_by_class.csv", index=False)
print("\n" + "=" * 90); print("T2 (cont.) — socioemotional density by event class (window-grain, Kruskal-Wallis)")
print("=" * 90)
for _, r in cdf.iterrows():
    star = "***" if r.q_fdr < .001 else "**" if r.q_fdr < .01 else "*" if r.q_fdr < .05 else "n.s."
    print(f"  {r['cat']:10} ({r.valence})  TRANSITION={r.mean_transition:.3f} (n={r.n_transition})  "
          f"HANDOFF={r.mean_handoff:.3f} (n={r.n_handoff})  OTHER={r.mean_other:.3f} (n={r.n_other})  "
          f"H={r.kruskal_H:.2f}  q={r.q_fdr:.4f}  {star}")
print(f"\nwrote {OUT}/socioemotional_lifts.csv, {OUT}/socioemotional_by_class.csv")
