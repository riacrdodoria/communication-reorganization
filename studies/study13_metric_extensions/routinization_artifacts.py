"""Artifact checks for the routinization result (declining Markov entropy rate of role-to-role turn transitions).
Candidate artifacts: (a) member absences (a missing role mechanically lowers the entropy rate); (b) rising facilitator
participation (concentration of turns, not a more predictable who-follows-whom); (c) the change of transcription tool
in each team's last five meetings (diarization could differ).
Decomposition: H_ind = entropy rate expected if the next speaker were drawn from the other participants in proportion to
their turn shares, P(j|i) = p_j / (1 - p_i); S = H_ind - H_obs = transition structure beyond participation shares.
Routinization proper predicts S rising over weeks; concentration predicts H_ind falling.
Same decomposition for the member-to-member share. Trends by Kendall tau within team, all meetings and complete-attendance
meetings only, and pre-tool-change meetings only; OLS of each measure on week with absence, tool and facilitator-share
covariates. Output: results/routinization_artifacts.csv, results/routinization_artifacts_summary.txt"""
import sys, os, numpy as np, pandas as pd
from scipy.stats import kendalltau
import statsmodels.formula.api as smf
sys.path.insert(0, os.path.dirname(__file__)); import common as C
import routinization as R0  # functions only (main block guarded)

COV = pd.read_csv(f"{C.RES}/meeting_covariates.csv").set_index("mid")
W = C.week_map(); rows = []
for t in "AB":
    labs = ["FACILITATOR", f"{t}1", f"{t}2", f"{t}3"]
    for m in [x for x in C.meetings() if C.team(x) == t]:
        s = R0.turns(m); M = R0.matrix(s, labs); n = M.sum(1); p = n / n.sum(); H_obs = R0.entropy_rate(M)
        H_ind = 0.0; mm_ind_num = 0.0; mm_den = 0.0
        for i in range(4):
            if p[i] == 0: continue
            q = np.array([p[j] / (1 - p[i]) if j != i else 0 for j in range(4)]); q = q[q > 0]
            H_ind += p[i] * -(q * np.log2(q)).sum()
            if i > 0:
                mm_ind_num += p[i] * sum(p[j] / (1 - p[i]) for j in range(1, 4) if j != i); mm_den += p[i]
        mm_obs = M[1:, 1:].sum() / max(1, M[1:].sum())
        rows.append(dict(mid=m, team=t, week=W[m], H_obs=H_obs, H_ind=H_ind, S=H_ind - H_obs, mm_obs=mm_obs, mm_ind=mm_ind_num / mm_den,
                         mm_excess=mm_obs - mm_ind_num / mm_den, fac_turn_share=p[0], n_members=int(COV.loc[m, "n_members"]), tool=int(COV.loc[m, "tool_bot"])))
D = pd.DataFrame(rows); D.to_csv(f"{C.RES}/routinization_artifacts.csv", index=False)
L = ["H_obs = observed entropy rate; H_ind = expected from turn shares alone; S = H_ind - H_obs (structure beyond shares).",
     "mm = member-to-member transition share; mm_excess = observed minus expected from shares.", ""]
def tau(g, c):
    x = g[["week", c]].dropna(); r = kendalltau(x.week, x[c]); return f"{r[0]:+.2f} (p={r[1]:.3f}, n={len(x)})"
for t, g in D.groupby("team"):
    for label, sub in [("all meetings", g), ("3 members present", g[g.n_members == 3]), ("before tool change", g[g.tool == 0])]:
        L.append(f"Team {t}, {label}: " + "; ".join(f"{c} {tau(sub, c)}" for c in ["H_obs", "H_ind", "S", "fac_turn_share", "mm_obs", "mm_ind", "mm_excess"]))
    L.append("")
D["absent"] = (D.n_members < 3).astype(int)
for y in ["H_obs", "H_ind", "S", "mm_obs", "mm_excess"]:
    r = smf.ols(f"{y} ~ week + absent + tool + team", data=D).fit()
    L.append(f"OLS {y:9s}: week b={r.params['week']:+.4f} p={r.pvalues['week']:.3f} | absent b={r.params['absent']:+.3f} p={r.pvalues['absent']:.3f} | tool b={r.params['tool']:+.3f} p={r.pvalues['tool']:.3f}")
L.append("")
L.append("Mean by attendance: " + D.groupby("n_members")[["H_obs", "H_ind", "S"]].mean().round(3).to_string().replace("\n", " | "))
open(f"{C.RES}/routinization_artifacts_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
