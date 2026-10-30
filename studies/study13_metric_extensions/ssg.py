"""Item 6. State space grid (Hollenstein, 2013; Lewis et al., 1999) of floor structure.
Grid axes from the battery windows (60 s, step 5 s): active speakers (1..n) x top-speaker share (5 bins: <.4, .4-.55,
.55-.7, .7-.85, >=.85). Per meeting and agenda-stage group (review = scorecard/rock/to-do; IDS), and per near-event vs
baseline windows: cells visited per 10 min, dispersion (1 - sum (d_i/D)^2, normalized by cell count), mean visit duration
(s), attractor cell (most occupied) and its occupancy share.
Tests: review vs IDS within meeting; near-event vs baseline within meeting; IDS stickiness over weeks within team.
Output: results/ssg_meeting.csv, results/ssg_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as C

B = pd.read_csv(f"{C.RES}/battery_windows.csv"); Wk = C.week_map()
B["ts"] = np.digitize(B.top_share, [.4, .55, .7, .85]); B["cell"] = B.active.astype(int) * 10 + B.ts
STEP = 5.0
def ssg(cells):
    if len(cells) < 12: return {}
    d = pd.Series(cells).value_counts(); n = d.size; D = d.sum(); p = d / D
    disp = (1 - (p ** 2).sum()) / (1 - 1 / n) if n > 1 else 0.0
    visits = (cells[1:] != cells[:-1]).sum() + 1
    return dict(cells_per10=n / (len(cells) * STEP / 600), dispersion=disp, visit_s=len(cells) * STEP / visits, attractor=int(d.index[0]), attractor_share=p.iloc[0])
rows = []
for mid, g in B.groupby("mid"):
    stg = C.stage_of_seconds(mid, g.sec.to_numpy()); grp = np.where(np.isin(stg, list(C.REVIEW)), "review", np.where(stg == "ids", "ids", "other"))
    for name, mask in [("review", grp == "review"), ("ids", grp == "ids"), ("near_event", g.near_event.to_numpy()), ("baseline", g.base_event.to_numpy()), ("all", np.ones(len(g), bool))]:
        r = ssg(g.cell.to_numpy()[mask])
        if r: rows.append(dict(mid=mid, team=C.team(mid), week=Wk[mid], part=name, **r))
S = pd.DataFrame(rows); S.to_csv(f"{C.RES}/ssg_meeting.csv", index=False)
L = []
def contrast(a, b, m):
    x = S[S.part == a].set_index("mid")[m]; y = S[S.part == b].set_index("mid")[m]; d = (x - y).dropna(); p, n = C.wilcoxon_p(d)
    return f"  {m:<16} {a} {x.mean():.3f} vs {b} {y.mean():.3f}  (paired n={n}, Wilcoxon p={p:.1e})"
for a, b in [("review", "ids"), ("near_event", "baseline")]:
    L.append(f"{a} vs {b}:"); L += [contrast(a, b, m) for m in ["cells_per10", "dispersion", "visit_s", "attractor_share"]]
    xa = S[S.part == a].set_index("mid").attractor; xb = S[S.part == b].set_index("mid").attractor; j = xa.index.intersection(xb.index)
    L.append(f"  same attractor cell in {int((xa[j] == xb[j]).sum())}/{len(j)} meetings; attractor (active*10+share bin) modal {a}: {xa.mode().tolist()} {b}: {xb.mode().tolist()}")
for t in "AB":
    g = S[(S.part == "ids") & (S.team == t)]
    for m in ["visit_s", "dispersion", "attractor_share"]:
        tau, p = kendalltau(g.week, g[m]); L.append(f"Team {t} IDS {m} vs week: tau={tau:+.2f} p={p:.3f}")
open(f"{C.RES}/ssg_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
