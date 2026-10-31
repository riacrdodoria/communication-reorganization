"""Do reorganization events come in pairs because of temporal organization, or because of the detection procedure?
Same detection on observed and on run-shuffled series (3 surrogates per meeting): share of events followed by another
within 30-75 s, burstiness B of inter-event intervals. Output: results/cluster_tautology_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
from csd_tautology import metrics_from_state, detect, shuffled
def stats(ev):
    ev = np.sort(ev); d = np.diff(ev)
    if d.size < 3: return np.nan, np.nan
    return np.mean((d >= 30) & (d <= 75)), (d.std() - d.mean()) / (d.std() + d.mean())
rows = []
for m in CM.meetings():
    st, _ = CM.team_state(m); s, det, r = metrics_from_state(st); o = stats(detect(s, r))
    su = [stats(detect(*[x for i, x in enumerate(metrics_from_state(shuffled(st))) if i != 1])) for _ in range(3)]
    rows.append(dict(mid=m, pair=o[0], B=o[1], pair_sur=np.nanmean([x[0] for x in su]), B_sur=np.nanmean([x[1] for x in su]))); print(m, rows[-1], flush=True)
D = pd.DataFrame(rows); D.to_csv(f"{CM.RES}/cluster_tautology.csv", index=False)
L = [f"Share of inter-event intervals of 30-75 s: observed {D.pair.mean():.3f} vs surrogate {D.pair_sur.mean():.3f} (p={wilcoxon(D.pair-D.pair_sur).pvalue:.3f})",
     f"Burstiness B of inter-event intervals: observed {D.B.mean():+.3f} vs surrogate {D.B_sur.mean():+.3f} (p={wilcoxon(D.B-D.B_sur).pvalue:.3f})"]
open(f"{CM.RES}/cluster_tautology_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
