"""Does every Paper 1 headline replicate in both teams? Each statistic recomputed per team with the same null as the
pooled result. Archival validation: per domain (submarine, surgical). Output: results/replication_by_team.csv and
results/replication_by_team_summary.txt (the 'findings at a glance' table)."""
import sys, os, json, numpy as np, pandas as pd
from scipy.stats import wilcoxon, spearmanr, kendalltau
import statsmodels.formula.api as smf, statsmodels.api as sm
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
from typology import entropy_series, shuffled
rng = np.random.default_rng(171); R_ = CM.RES; P = json.load(open(f"{R_}/partitions_bounds.json")); SUR = json.load(open(f"{R_}/surrogate_events.json")); EV = CM.events()
TU = pd.read_csv(f"{R_}/seqdyn_turns.csv"); G = pd.read_csv(f"{R_}/channels_grid.csv"); ST = pd.read_csv(f"{R_}/floor_cycle_T2_states.csv")
TEAM = {m: CM.team(m) for m in CM.meetings()}; rows = []
def near(a, b): a = np.asarray(a, float); b = np.asarray(b, float); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
def add(h, a, b, unit, null, note=""):
    rows.append(dict(headline=h, A=a[0], A_p=a[1], B=b[0], B_p=b[1], unit=unit, null=null, note=note))
# H1 archival by domain
V = pd.read_csv(f"{CM.L}/study1_lsh_validation/results/lsh_variants_team.csv")
for col, lab in [("r_entropy", "entropy r"), ("r_det", "%DET r"), ("r_rmse", "RMSE r"), ("events_std_matched", "events matched")]:
    w = V[V.variant == "LSH-WD"].groupby("domain")[col].mean(); l = V[V.variant == "LSH"].groupby("domain")[col].mean()
    rows.append(dict(headline=f"Reconstruction beats pure LSH: {lab}", A=w["submarine"], A_p=np.nan, B=w["surgical"], B_p=np.nan, unit=f"LSH-WD (pure LSH {l['submarine']:.2f} / {l['surgical']:.2f})", null="true standard", note="A = submarine, B = surgical"))
# H2 excursion frequency vs run-shuffle (100 surrogate corpora per team)
def peaks(e, K=2.0, SEP=60):
    thr = e.mean() + K * e.std(ddof=1); c = sorted([(i, e[i]) for i in range(1, e.size - 1) if e[i] > thr and e[i] >= e[i - 1] and e[i] >= e[i + 1]], key=lambda x: -x[1]); kept = []
    for i, _ in c:
        if all(abs(i - x) >= SEP for x in kept): kept.append(i)
    return len([i for i in kept if i - 90 >= 0 and i + 90 < e.size])
S = {m: CM.team_state(m) for m in CM.meetings()}; res = {}
for t in "AB":
    ms = [m for m in S if TEAM[m] == t]; o = sum(peaks(entropy_series(*S[m])) for m in ms)
    nul = np.array([sum(peaks(entropy_series(shuffled(S[m][0]), S[m][1])) for m in ms) for _ in range(100)]); res[t] = (o / nul.mean(), (np.sum(nul >= o) + 1) / 101)
add("Excursions more frequent than turn-preserving chance", res["A"], res["B"], "observed / run-shuffle peaks", "run-shuffle (100)")
# H3 setpoint relocation by agenda stage
E_ = pd.read_csv(f"{R_}/system_cuts_eta.csv"); r = {}
for t, g in E_.groupby("team"): d = g.eta_stage - g.eta_stage_null; r[t] = (d.mean(), wilcoxon(d.dropna()).pvalue)
add("Setpoint relocates across agenda stages (eta2 excess)", r["A"], r["B"], "eta2 observed - null", "run-shuffle (200)")
# H4 no periodicity
Pp = pd.read_csv(f"{R_}/system_cuts_periodicity.csv").dropna(subset=["p"]); Pp["team"] = Pp.mid.map(TEAM); r = {t: ((g.p < .05).mean(), np.nan) for t, g in Pp[Pp.cut == "fixed_10min"].groupby("team")}
add("No periodic segments beyond chance (10-min cuts)", r["A"], r["B"], "share periodic (chance .05)", "run-shuffle (100)")
# H5-H7 event statistics vs surrogate events, per team
TUm = {m: TU[TU.mid == m] for m in CM.meetings()}
def evstats(evs, ms):
    n = 0; ag = 0; an = 0; q = 0; fl = 0; oq = 0; no = 0
    for m in ms:
        ev = np.asarray(evs[m], float); a = np.array(P[m]["agenda"]); g = TUm[m]; n += ev.size
        if ev.size == 0: continue
        if a.size: ag += np.sum(near(ev, a) <= 30); an += sum(np.any(((a - t0) >= 15) & ((a - t0) <= 60)) for t0 in ev)
        mq = g[g.question & (g.role != "FACILITATOR") & (g.role != "OTHER")].t.to_numpy(); q += sum(np.sum((mq > t0) & (mq <= t0 + 45)) for t0 in ev)
        fl += np.sum(near(ev, P[m]["floor"]) <= 30)
        for t0 in ev:
            o = g[(g.t >= t0 - 5) & (g.t <= t0 + 10)]
            if len(o): oq += float(o.question.iloc[0]); no += 1
    return np.array([ag / n, an / n, q / n, fl / n, oq / max(no, 1)])
names = ["Events coincide with agenda transitions", "Events anticipate the next agenda stage (15-60 s)", "Member questions follow event onset (45 s)", "Events avoid extended floor turns", "Opening turn is rarely a question"]
per = {}
for t in "AB":
    ms = [m for m in CM.meetings() if TEAM[m] == t]; o = evstats({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in ms}, ms); s = np.array([evstats({m: SUR[m][k] for m in ms}, ms) for k in range(20)])
    ratio = o / s.mean(0); p = [((np.sum(s[:, j] >= o[j]) + 1) / 21) if ratio[j] >= 1 else ((np.sum(s[:, j] <= o[j]) + 1) / 21) for j in range(5)]; per[t] = (ratio, p)
for j, h in enumerate(names): add(h, (per["A"][0][j], per["A"][1][j]), (per["B"][0][j], per["B"][1][j]), "observed / surrogate events", "surrogate events (20)")
# H8 content signature at event (topic mixing, return), observed minus surrogate
Z = {m: g.set_index("sec")[["topic_entropy_res", "ret_res"]].pipe(lambda x: (x - x.mean()) / x.std()) for m, g in G.groupby("mid")}
def at(evs, ms, c):
    v = []
    for m in ms:
        z = Z[m][c]; idx = z.index.to_numpy()
        for t0 in np.asarray(evs[m], float):
            k = np.searchsorted(idx, t0)
            if 0 <= k < idx.size and abs(idx[k] - t0) <= 5 and not np.isnan(z.iloc[k]): v.append(z.iloc[k])
    return np.mean(v)
for c, h in [("topic_entropy_res", "Topic mixing rises at events"), ("ret_res", "Return to earlier subjects at events")]:
    r = {}
    for t in "AB":
        ms = [m for m in CM.meetings() if TEAM[m] == t]; o = at({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in ms}, ms, c); s = np.array([at({m: SUR[m][k] for m in ms}, ms, c) for k in range(20)])
        r[t] = (o - s.mean(), (np.sum(s >= o) + 1) / 21)
    add(h, r["A"], r["B"], "z observed - surrogate", "surrogate events (20)")
# H9 agenda boundaries in the collaborative floor
r = {}
for t in "AB":
    ms = [m for m in CM.meetings() if TEAM[m] == t]; obs = 0; exp = 0; n = 0
    for m in ms:
        s = ST[ST.mid == m]; secs = s.sec.to_numpy(); sv = s.state.to_numpy(); a = np.array(P[m]["agenda"])
        if a.size == 0: continue
        obs += np.sum(sv[np.abs(secs[None, :] - a[:, None]).argmin(1)] == "F2"); n += a.size
        exp += np.mean([np.sum(sv[np.abs(secs[None, :] - ((a + rng.uniform(0, P[m]["T"])) % P[m]["T"])[:, None]).argmin(1)] == "F2") for _ in range(100)])
    r[t] = (obs / exp, np.nan)
add("Agenda transitions fall in the collaborative floor", r["A"], r["B"], "observed / circular-shift expected", "circular shift (100)")
# H10 centralization and events in 5-min blocks (events only)
B4 = pd.read_csv(f"{R_}/floor_cycle_T4_blocks.csv"); B4["team"] = B4.mid.map(TEAM)
B4["ev"] = [int(np.sum((EV[EV.mid == m].event_onset_s >= s0) & (EV[EV.mid == m].event_onset_s < s0 + 300))) for m, s0 in zip(B4.mid, B4.s0)]
B4["cz"] = B4.groupby("mid").central.transform(lambda x: (x - x.mean()) / x.std()); B4["ids"] = (B4.stage == "ids").astype(int); r = {}
for t, g in B4.dropna(subset=["cz"]).groupby("team"):
    f = smf.glm("ev ~ cz + ids + mid", data=g, family=sm.families.Poisson()).fit(); r[t] = (np.exp(f.params["cz"]), f.pvalues["cz"])
add("Centralized stretches have fewer events", r["A"], r["B"], "rate ratio per SD", "Poisson, meeting FE")
# H11 turn-content coupling
r = {}
for t in "AB":
    v = [g[["switch", "ret_res"]].dropna().corr(method="spearman").iloc[0, 1] for m, g in G.groupby("mid") if TEAM[m] == t]; r[t] = (np.mean(v), wilcoxon(v).pvalue)
add("Speaker switching goes with return to earlier subjects", r["A"], r["B"], "mean within-meeting rho", "Wilcoxon over meetings")
# H12-H13 longitudinal
D = pd.read_csv(f"{R_}/longit_panel.csv"); r = {}; r2 = {}
for t, g in D.groupby("team"):
    g = g.sort_values("week"); r[t] = kendalltau(g.week, g.active); x = g.det.to_numpy(); r2[t] = spearmanr(x[:-1], x[1:])
add("Floor narrows over weeks (active speakers)", (r["A"][0], r["A"][1]), (r["B"][0], r["B"][1]), "Kendall tau", "—")
add("Consecutive meetings alternate in organization (%DET lag-1)", (r2["A"][0], r2["A"][1]), (r2["B"][0], r2["B"][1]), "Spearman rho", "—")
T_ = pd.DataFrame(rows); T_.to_csv(f"{R_}/replication_by_team.csv", index=False)
L = ["FINDINGS BY TEAM (A | B); p from the null named; same direction marked"]
for r_ in T_.itertuples():
    pa = f"p={r_.A_p:.3f}" if pd.notna(r_.A_p) else ""; pb = f"p={r_.B_p:.3f}" if pd.notna(r_.B_p) else ""
    L.append(f"  {r_.headline:<58} A {r_.A:+.3f} {pa:<9} | B {r_.B:+.3f} {pb:<9} [{r_.unit}; {r_.null}] {r_.note}")
open(f"{R_}/replication_by_team_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
