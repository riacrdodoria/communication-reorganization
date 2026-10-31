"""Moment-level links between channels: mean within-meeting Spearman correlation between every pair of channels on
the 5-s grid (channels_grid.csv), with the number of meetings in which the sign agrees and a Wilcoxon test across
meetings. Output: results/channels_crosscorr.csv, results/channels_crosscorr_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
G = pd.read_csv(f"{CM.RES}/channels_grid.csv"); G["F2"] = (G.state == "F2").astype(float); G["F1"] = (G.state == "F1").astype(float)
TT = ["entropy", "det", "top_share", "switch", "F1", "F2"]; CO = ["novelty_res", "topic_entropy_res", "sem_shift", "ret_res", "sentiment", "collective", "question", "lsm_res", "ttr_res"]
rows = []
for a in TT + CO:
    for b in CO:
        if a == b or (a in CO and CO.index(a) > CO.index(b)): continue
        r = [g[[a, b]].dropna().corr(method="spearman").iloc[0, 1] for _, g in G.groupby("mid") if g[[a, b]].dropna().shape[0] > 50]
        r = np.array(r); rows.append(dict(a=a, b=b, rho=r.mean(), same_sign=int(max((r > 0).sum(), (r < 0).sum())), n=len(r), p=wilcoxon(r).pvalue))
C = pd.DataFrame(rows).sort_values("p"); C.to_csv(f"{CM.RES}/channels_crosscorr.csv", index=False)
L = ["Moment-level links (mean within-meeting Spearman; sign agreement over meetings; Wilcoxon p). |rho| >= .10 and p < .001:"]
for r in C[(C.rho.abs() >= .10) & (C.p < .001)].itertuples(): L.append(f"  {r.a:<18} ~ {r.b:<18} rho={r.rho:+.2f}  {r.same_sign}/{r.n}  p={r.p:.1e}")
open(f"{CM.RES}/channels_crosscorr_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
