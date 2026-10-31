"""Longitudinal, inter-meeting analysis: one row per meeting with every family of measures, then
(1) trajectories over weeks per team and pooled; (2) where each window-level channel varies (between teams, between
meetings, within meetings); (3) team signature (can a meeting's team be recognised from its dynamics?); (4) convergence
of the two teams over time; (5) inter-meeting links: lag-1 stability of each measure and cross-lagged prediction of the
next meeting (Y[w+1] ~ X[w] + Y[w] + team); (6) cross-family correlation network (team-demeaned Spearman, BH-FDR).
Families: turn-taking, floor and roles, agenda, events, content, language, inter-meeting continuity, outcomes (Study 8,
quote-anchored extraction), and LLM topics (qualitative side, reported separately).
Output: results/longit_panel.csv, results/longit_*.csv, results/longit_summary.txt"""
import sys, os, json, re, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import kendalltau, spearmanr
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
sys.path.insert(0, CM.L); import floor_measures as FM
rng = np.random.default_rng(161); CACHE = f"{CM.L}/data/semantic_cache"; R_ = CM.RES
G = pd.read_csv(f"{R_}/channels_grid.csv"); EV = CM.events(); P = json.load(open(f"{R_}/partitions_bounds.json")); Wk = CM.week_map()
OUT = pd.read_csv(f"{CM.L}/study8_outcomes/data/outcomes_per_meeting.csv")
SUR = json.load(open(f"{R_}/surrogate_events.json")) if os.path.exists(f"{R_}/surrogate_events.json") else {}
LLMT = pd.read_csv(f"{R_}/llm_topics_topics.csv") if os.path.exists(f"{R_}/llm_topics_topics.csv") else None
DIFF = pd.read_csv(f"{R_}/content2_diffusion.csv"); REC = pd.read_csv(f"{R_}/content2_recurrence_meeting.csv")
MIDS = CM.meetings(); rows = []

def meeting_windows(m):
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); on = z["onset"]; E = z["emb"].astype(float); nw = np.maximum(z["nw"], 1)
    g = np.arange(30, on.max() - 30, 30.0); cs = np.vstack([np.zeros((1, E.shape[1])), np.cumsum(E * nw[:, None], 0)])
    V = cs[np.searchsorted(on, g + 30)] - cs[np.searchsorted(on, g - 30)]; n = np.linalg.norm(V, axis=1); V = V[n > 0] / n[n > 0, None]; return V
WV = {m: meeting_windows(m) for m in MIDS}
for m in MIDS:
    g = G[G.mid == m]; tx = CM.transcript(m); R = CM.roles(m); role = tx.speaker_id.astype(str).map(lambda s: R.get(s, "OTHER"))
    nw = tx.text.astype(str).str.split().str.len(); words = nw.groupby(role).sum(); mem = words.drop([x for x in ["FACILITATOR", "OTHER"] if x in words.index])
    sp = tx.speaker_id.astype(str).to_numpy(); k = np.concatenate(([True], sp[1:] != sp[:-1])); seq = role.to_numpy()[k]; people = sorted(set(seq) - {"OTHER"})
    Wm = np.zeros((len(people), len(people))); ix = {p: i for i, p in enumerate(people)}
    for a, b in zip(seq[:-1], seq[1:]):
        if a in ix and b in ix: Wm[ix[a], ix[b]] += 1
    T_h = P[m]["T"] / 3600; ev = EV[EV.mid == m]; on = ev.event_onset_s.to_numpy(); ag = np.array(P[m]["agenda"])
    antic = np.mean([np.any(((ag - t) >= 0) & ((ag - t) <= 90)) for t in on]) if ag.size and on.size else np.nan
    gini = lambda x: (np.abs(x[:, None] - x[None, :]).sum() / (2 * len(x) ** 2 * x.mean())) if len(x) > 1 and x.mean() > 0 else np.nan
    # inter-meeting content continuity: previous meeting of the same team vs other team's meeting nearest in date (before)
    same = sorted([x for x in MIDS if CM.team(x) == CM.team(m) and x[:10] < m[:10]]); other = sorted([x for x in MIDS if CM.team(x) != CM.team(m) and x[:10] < m[:10]])
    cont = (WV[m] @ WV[same[-1]].T).max(1).mean() - (WV[m] @ WV[other[-1]].T).max(1).mean() if same and other else np.nan
    st = g.state.value_counts(normalize=True)
    r = dict(mid=m, team=CM.team(m), week=Wk[m],
             # turn-taking
             entropy=g.entropy.mean(), entropy_sd=g.entropy.std(), det=g.det.mean(), switch=g.switch.mean(), active=g.active.mean(),
             F1=st.get("F1", 0), F2=st.get("F2", 0),
             # floor and roles
             fac_word_share=words.get("FACILITATOR", 0) / words.sum(), member_gini=gini(mem.to_numpy(float)), centralization=FM.degree_centralization(Wm),
             # agenda and events
             ids_share=np.mean(CM.stage_of_seconds(m, np.arange(0, P[m]["T"], 10)) == "ids"), event_rate=len(on) / T_h,
             event_excess=(len(on) / np.mean([len(x) for x in SUR[m]])) if m in SUR else np.nan, event_depth=ev.depth.mean(), events_anticipate_agenda=antic,
             # content
             novelty=g.novelty_res.mean(), topic_mixing=g.topic_entropy_res.mean(), sem_shift=g.sem_shift.mean(), return_earlier=g.ret_res.mean(),
             new_lemmas_per_h=(DIFF[(DIFF.mid == m) & (DIFF.lemma_id >= 0)].shape[0]) / T_h, ttr=g.ttr_res.mean(),
             # language
             sentiment=g.sentiment.mean(), sentiment_sd=g.sentiment.std(), collective=g.collective.mean(), question=g.question.mean(), lsm=g.lsm_res.mean(),
             # inter-meeting continuity
             carryover_prev=cont, recurrence_all_prior=REC.set_index("mid").rec_mean.get(m, np.nan))
    if LLMT is not None:
        t_ = LLMT[LLMT.mid == m]; r.update(llm_topics_per_h=len(t_) / T_h, llm_problem_share=(t_.kind == "problem").mean(), llm_decision_share=(t_.kind == "decision").mean())
    rows.append(r)
D = pd.DataFrame(rows).merge(OUT[["mid", "rating_mean", "n_todos_assigned", "n_issues_raised", "issue_resolution_rate_same_meeting", "todo_completion_rate"]], on="mid", how="left")
D = D.sort_values(["team", "week"]).reset_index(drop=True); D.to_csv(f"{R_}/longit_panel.csv", index=False)
FAM = {"turn-taking": ["entropy", "entropy_sd", "det", "switch", "active", "F1", "F2"], "floor & roles": ["fac_word_share", "member_gini", "centralization"],
       "agenda & events": ["ids_share", "event_rate", "event_excess", "event_depth", "events_anticipate_agenda"],
       "content": ["novelty", "topic_mixing", "sem_shift", "return_earlier", "new_lemmas_per_h", "ttr"], "language": ["sentiment", "sentiment_sd", "collective", "question", "lsm"],
       "continuity": ["carryover_prev", "recurrence_all_prior"], "outcomes": ["rating_mean", "n_todos_assigned", "n_issues_raised", "issue_resolution_rate_same_meeting", "todo_completion_rate"]}
VARS = [v for f in FAM.values() for v in f if v in D and D[v].notna().sum() > 10]; L = []

# (1) trajectories
rows = []
for v in VARS:
    r = dict(var=v, family=[f for f, vs in FAM.items() if v in vs][0])
    for t in "AB":
        x = D[(D.team == t)][["week", v]].dropna(); tau, p = kendalltau(x.week, x[v]) if len(x) > 5 else (np.nan, np.nan); r[f"tau_{t}"] = tau; r[f"p_{t}"] = p
    d = D.dropna(subset=[v]); fit = smf.ols(f"{v} ~ week * team", data=d.assign(**{v: (d[v] - d[v].mean()) / d[v].std()})).fit()
    r["b_week_pooled_sd"] = fit.params["week"] + fit.params.get("week:team[T.B]", 0) / 2; r["p_week"] = fit.pvalues["week"]; r["p_week_x_team"] = fit.pvalues.get("week:team[T.B]", np.nan)
    rows.append(r)
TR = pd.DataFrame(rows); TR["q_A"] = multipletests(TR.p_A.fillna(1), method="fdr_bh")[1]; TR["q_B"] = multipletests(TR.p_B.fillna(1), method="fdr_bh")[1]
TR.to_csv(f"{R_}/longit_trajectories.csv", index=False)
L.append("(1) TRAJECTORIES OVER WEEKS (Kendall tau per team; q = BH-FDR across all measures; * q < .05, + p < .05)")
for _, r in TR.iterrows():
    fa = lambda t: f"{r['tau_'+t]:+.2f}{'*' if r['q_'+t] < .05 else ('+' if r['p_'+t] < .05 else ' ')}"
    L.append(f"  {r['family']:<15} {r['var']:<34} A {fa('A')}  B {fa('B')}  week x team p={r['p_week_x_team']:.3f}")

# (2) where each channel varies (window level)
L.append("\n(2) VARIANCE OF WINDOW-LEVEL CHANNELS: between teams / between meetings within team / within meetings")
G2 = G.copy(); G2["team"] = G2.mid.map(CM.team); rows = []
for c in ["entropy", "det", "top_share", "switch", "novelty_res", "topic_entropy_res", "sem_shift", "ret_res", "sentiment", "collective", "question", "lsm_res", "ttr_res"]:
    d = G2.dropna(subset=[c]); tot = ((d[c] - d[c].mean()) ** 2).sum()
    bt = (d.groupby("team")[c].transform("mean") - d[c].mean()).pow(2).sum(); bm = (d.groupby("mid")[c].transform("mean") - d.groupby("team")[c].transform("mean")).pow(2).sum()
    rows.append(dict(channel=c, between_team=bt / tot, between_meeting=bm / tot, within_meeting=1 - (bt + bm) / tot))
VD = pd.DataFrame(rows); VD.to_csv(f"{R_}/longit_variance.csv", index=False); L.append(VD.round(3).to_string(index=False))

# (3) team signature
L.append("\n(3) TEAM SIGNATURE: leave-one-meeting-out classification of team (accuracy; permutation p, 500)")
def loo_acc(cols, y):
    X = D[cols].fillna(D[cols].mean()).to_numpy(); acc = 0
    for i in range(len(D)):
        tr = np.arange(len(D)) != i; clf = make_pipeline(StandardScaler(), LogisticRegression(C=.5, max_iter=1000)).fit(X[tr], y[tr]); acc += clf.predict(X[i:i + 1])[0] == y[i]
    return acc / len(D)
y = (D.team == "B").to_numpy().astype(int)
for name, cols in [("turn-taking only", FAM["turn-taking"]), ("floor & roles", FAM["floor & roles"]), ("content", FAM["content"]), ("language", FAM["language"])]:
    cols = [c for c in cols if c in D]; a = loo_acc(cols, y); null = [loo_acc(cols, rng.permutation(y)) for _ in range(200)]
    L.append(f"  {name:<18} accuracy {a:.2f} (permutation p={(np.sum(np.array(null) >= a) + 1) / 201:.3f})")

# (4) convergence of the two teams
L.append("\n(4) CONVERGENCE: distance between the teams' standardized profiles at the same week index")
Z = D.copy(); prof = [c for c in VARS if c not in FAM["outcomes"]]; Z[prof] = (Z[prof] - Z[prof].mean()) / Z[prof].std()
A_ = Z[Z.team == "A"].set_index("week")[prof]; B_ = Z[Z.team == "B"].set_index("week")[prof]; wk = A_.index.intersection(B_.index)
dist = [np.sqrt(np.nanmean((A_.loc[w] - B_.loc[w]) ** 2)) for w in wk]; tau, p = kendalltau(wk, dist)
L.append(f"  weeks {len(wk)}; distance first third {np.mean(dist[:len(dist)//3]):.2f}, last third {np.mean(dist[-len(dist)//3:]):.2f}; trend tau={tau:+.2f} p={p:.3f}")

# (5) inter-meeting links
L.append("\n(5) INTER-MEETING LINKS")
rows = []
for v in VARS:
    s = []
    for t in "AB":
        x = D[D.team == t][v].to_numpy(); ok = ~np.isnan(x[:-1]) & ~np.isnan(x[1:])
        if ok.sum() > 5: s.append(spearmanr(x[:-1][ok], x[1:][ok])[0])
    rows.append(dict(var=v, lag1_rho=np.mean(s) if s else np.nan))
AC = pd.DataFrame(rows); AC.to_csv(f"{R_}/longit_lag1.csv", index=False)
L.append("  lag-1 stability (mean of the two teams' Spearman rho between consecutive meetings): " + ", ".join(f"{r[0]} {r[1]:+.2f}" for r in AC.sort_values("lag1_rho", ascending=False)[["var","lag1_rho"]].itertuples(index=False)))
Lg = D.copy()
for v in VARS: Lg[v + "_next"] = Lg.groupby("team")[v].shift(-1)
X_ = ["event_rate", "event_excess", "F2", "centralization", "fac_word_share", "member_gini", "sentiment", "collective", "question", "lsm", "novelty", "topic_mixing", "carryover_prev", "n_todos_assigned", "n_issues_raised"]
Y_ = ["todo_completion_rate", "rating_mean", "n_issues_raised", "event_rate", "fac_word_share", "sentiment", "carryover_prev", "centralization"]
rows = []
for xv in [x for x in X_ if x in D]:
    for yv in [x for x in Y_ if x in D]:
        if xv == yv: continue
        d = Lg[["team", xv, yv, yv + "_next"]].dropna()
        if len(d) < 15: continue
        dz = d.copy(); dz[[xv, yv, yv + "_next"]] = (dz[[xv, yv, yv + "_next"]] - dz[[xv, yv, yv + "_next"]].mean()) / dz[[xv, yv, yv + "_next"]].std()
        f = smf.ols(f"Q('{yv}_next') ~ Q('{xv}') + Q('{yv}') + team", data=dz).fit(); rows.append(dict(x=xv, y_next=yv, beta=f.params[f"Q('{xv}')"], p=f.pvalues[f"Q('{xv}')"], n=len(d)))
CL = pd.DataFrame(rows); CL["q"] = multipletests(CL.p, method="fdr_bh")[1]; CL = CL.sort_values("p"); CL.to_csv(f"{R_}/longit_crosslag.csv", index=False)
L.append("  cross-lagged (standardized beta of X in meeting w predicting Y in meeting w+1, controlling Y in w and team); top 12:")
for r in CL.head(12).itertuples(): L.append(f"    {r.x:<20} -> next {r.y_next:<22} beta={r.beta:+.2f} p={r.p:.3f} q={r.q:.2f} n={r.n}")

# (6) cross-family correlation network (meeting level, team-demeaned)
L.append("\n(6) CROSS-FAMILY LINKS AT THE MEETING LEVEL (team-demeaned Spearman, BH-FDR across all pairs); q < .10:")
Dm = D.copy(); Dm[VARS] = Dm[VARS] - Dm.groupby("team")[VARS].transform("mean"); rows = []
for i, a in enumerate(VARS):
    for b in VARS[i + 1:]:
        d = Dm[[a, b]].dropna()
        if len(d) > 15: rho, p = spearmanr(d[a], d[b]); rows.append(dict(a=a, b=b, rho=rho, p=p))
CN = pd.DataFrame(rows); CN["q"] = multipletests(CN.p, method="fdr_bh")[1]
fam_of = {v: f for f, vs in FAM.items() for v in vs}; CN["cross_family"] = CN.a.map(fam_of) != CN.b.map(fam_of); CN.to_csv(f"{R_}/longit_network.csv", index=False)
for r in CN[(CN.q < .10) & CN.cross_family].sort_values("p").itertuples(): L.append(f"  {r.a:<26} ~ {r.b:<30} rho={r.rho:+.2f} q={r.q:.3f}")
if LLMT is not None:
    L.append("\n(LLM topics, qualitative side) trajectories: " + ", ".join(f"{v} A {kendalltau(D[D.team=='A'].week, D[D.team=='A'][v])[0]:+.2f} B {kendalltau(D[D.team=='B'].week, D[D.team=='B'][v])[0]:+.2f}" for v in ["llm_topics_per_h", "llm_problem_share", "llm_decision_share"]))
open(f"{R_}/longit_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
