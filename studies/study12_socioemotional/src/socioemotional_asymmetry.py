"""T3 - Positive vs negative socioemotional asymmetry, and the review-vs-IDS contrast for the
socioemotional subset. Reuses the exact event/window/L10-stage machinery established throughout this
program (peaks_taxonomy_sig.py-style lift; l10_taxonomy.py-style stage_bounds for review-vs-IDS)."""
import glob, os, json, re, unicodedata
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
COD2 = f"{LSH}/data/codebooks2"
ACT4 = f"{LSH}/data/act4teams"
OUT = os.path.dirname(__file__) + "/../data"
TCRIT = 2.33

BALES_CATS = ["bsolid", "btension", "bagree", "bdisagree", "btensh", "bantag"]
ACT4_CATS = ["pos", "neg"]
POSITIVE = ["bsolid", "btension", "bagree", "pos"]
NEGATIVE = ["bdisagree", "btensh", "bantag", "neg"]
FAMILY = BALES_CATS + ACT4_CATS


def load_cb(folder):
    d = {}
    for f in glob.glob(f"{folder}/*_passA.json"):
        mid = os.path.basename(f).replace("_passA.json", "")
        d[mid] = {int(w["t"]): w for w in json.load(open(f))["windows"]}
    return d


c2 = load_cb(COD2); c4 = load_cb(ACT4)
win = lambda s: int(s // 90 * 90)

# ---------------- per-meeting composite positive/negative lift ----------------
per_meeting = {}
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    if mid not in c2 or mid not in c4:
        continue
    g = pd.read_csv(f); secs = g["second"].to_numpy(); x = g["rmse_g"].to_numpy(float)
    m = np.nanmean(x); sd = np.nanstd(x)
    mask = x > m + TCRIT * sd; base = ~mask & np.isfinite(x)
    if mask.sum() < 20 or base.sum() < 20:
        continue
    cat_lift = {}
    for cat in FAMILY:
        cd = c2[mid] if cat in BALES_CATS else c4[mid]
        dens = np.array([cd.get(win(s), {}).get(cat, 0) for s in secs], float)
        if not np.isfinite(dens).any() or dens.sum() == 0:
            continue
        cat_lift[cat] = dens[mask].mean() - dens[base].mean()
    pos_vals = [cat_lift[c] for c in POSITIVE if c in cat_lift]
    neg_vals = [cat_lift[c] for c in NEGATIVE if c in cat_lift]
    if pos_vals and neg_vals:
        per_meeting[mid] = (np.mean(pos_vals), np.mean(neg_vals))

mids = sorted(per_meeting)
pos_arr = np.array([per_meeting[m][0] for m in mids])
neg_arr = np.array([per_meeting[m][1] for m in mids])
diff = pos_arr - neg_arr
stat = wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
print("=" * 90); print("T3 — Positive vs negative socioemotional lift asymmetry (paired, per meeting)")
print("=" * 90)
print(f"n meetings = {len(mids)}")
print(f"mean positive-composite lift = {pos_arr.mean():+.4f}   mean negative-composite lift = {neg_arr.mean():+.4f}")
print(f"paired Wilcoxon (positive - negative != 0): W stat, p = {stat.pvalue:.2e}")
print(f"{(diff > 0).sum()}/{len(diff)} meetings show positive > negative lift")
pd.DataFrame({"mid": mids, "positive_composite_lift": pos_arr, "negative_composite_lift": neg_arr,
              "diff": diff}).to_csv(f"{OUT}/socioemotional_pos_vs_neg.csv", index=False)

# ---------------- review-vs-IDS contrast for the socioemotional subset ----------------
def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower()); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def stage_bounds(mid):
    f = f"{LSH}/data/l10_stages/{mid}.json"; tp = f"{LSH}/data/text_startup/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)):
        return None
    d = json.load(open(f)); tx = pd.read_csv(tp)
    on = pd.to_numeric(tx["onset_seconds"], errors="coerce").to_numpy(); ntx = [norm(t) for t in tx["text"]]
    seg = []; prev = 0
    for st in d["stages"]:
        q = norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(ntx)):
            if q and q in ntx[i]:
                idx = i; break
        if idx is None:
            for i in range(len(ntx)):
                if q and q in ntx[i]:
                    idx = i; break
        if idx is not None:
            seg.append((st["name"], float(on[idx]))); prev = idx + 1
    if not seg:
        return None
    bounds = [s[1] for s in seg] + [float(np.nanmax(on)) + 5]
    return [(seg[k][0], seg[k][1], bounds[k + 1]) for k in range(len(seg))]


REVIEW = {"scorecard", "rock_review", "todo"}
rows = []
for mid in sorted(set(c2) & set(c4)):
    sb = stage_bounds(mid)
    if not sb:
        continue
    rev_wins = set(); ids_wins = set()
    for name, s0, s1 in sb:
        wins = range(int(s0 // 90) * 90, int(s1 // 90) * 90 + 90, 90)
        if name in REVIEW:
            rev_wins |= set(wins)
        elif name == "ids":
            ids_wins |= set(wins)
    if not rev_wins or not ids_wins:
        continue
    row = {"mid": mid}
    for cat in FAMILY:
        cd = c2[mid] if cat in BALES_CATS else c4[mid]
        rv = [cd.get(w, {}).get(cat, 0) for w in rev_wins if w in cd]
        iv = [cd.get(w, {}).get(cat, 0) for w in ids_wins if w in cd]
        if not rv or not iv:
            continue
        row[cat] = np.mean(rv) - np.mean(iv)
    rows.append(row)

rdf = pd.DataFrame(rows)
print("\n" + "=" * 90); print("T3 (cont.) — review-vs-IDS contrast, socioemotional subset (paired Wilcoxon, BH-FDR)")
print("=" * 90)
res_rows = []
for cat in FAMILY:
    if cat not in rdf.columns:
        continue
    vals = rdf[cat].dropna().to_numpy()
    if len(vals) < 15:
        continue
    p = wilcoxon(vals, zero_method="wilcox", alternative="two-sided").pvalue if np.any(vals != 0) else 1.0
    res_rows.append(dict(cat=cat, n=len(vals), mean_delta=vals.mean(), p=p))
rr = pd.DataFrame(res_rows)
if len(rr):
    p = np.array(rr["p"]); n = len(p); order = np.argsort(p); ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]; rr["q_fdr"] = np.clip(q, 0, 1)[np.argsort(order)]
    rr = rr.sort_values("mean_delta", ascending=False)
    for _, r in rr.iterrows():
        star = "***" if r.q_fdr < .001 else "**" if r.q_fdr < .01 else "*" if r.q_fdr < .05 else "n.s."
        print(f"  {r['cat']:10}  n={r.n}  review-minus-IDS={r.mean_delta:+.4f}  p={r.p:.4f}  q={r.q_fdr:.4f}  {star}")
rr.to_csv(f"{OUT}/socioemotional_review_vs_ids.csv", index=False)
print(f"\nwrote {OUT}/socioemotional_pos_vs_neg.csv, {OUT}/socioemotional_review_vs_ids.csv")
