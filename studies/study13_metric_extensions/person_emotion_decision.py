"""Three label-free extensions (lexicons and pretrained models; no human or LLM coding; outputs numeric only).
P. Person trajectories: per role and meeting (facilitator, A1-A3, B1-B3): word share, questions and 'a gente' per 100
   words, extended floor turns per hour, sentiment, commitments, emotion profile; Kendall tau over weeks (BH-FDR);
   member role differentiation (Gini of member word shares) and rank stability (first vs second half of the weeks).
E. Emotions (pysentimiento/bert-pt-emotion, 28 GoEmotions categories; categories with mean probability >= .02):
   120-s windows on the 5-s grid (word-weighted), z within meeting; collaborative minus single-speaker floor;
   IDS minus review; event signature against surrogate events; weekly trends per team.
D. Decision moments, Portuguese lexicons on utterance text: collective agreement ('fica combinado', 'fechado',
   'vamos fazer assim'...), individual commitment ('eu vou fazer', 'eu faço', 'deixa comigo'...), deadlines and
   assignment ('até sexta', 'prazo', 'responsável', 'próximo passo'). Convergent validity against Study 8 to-dos
   assigned per meeting; where they fall (agenda stage, floor state); relation to reorganization events against
   surrogate events; who commits relative to talk share; whether commitments in week w predict to-do completion in w+1.
Output: results/ped_*.csv, results/ped_summary.txt"""
import sys, os, re, json, numpy as np, pandas as pd
from scipy.stats import kendalltau, spearmanr, wilcoxon
from statsmodels.stats.multitest import multipletests
import statsmodels.formula.api as smf
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
CACHE = f"{CM.L}/data/semantic_cache"; R_ = CM.RES; Wk = CM.week_map(); P = json.load(open(f"{R_}/partitions_bounds.json"))
SUR = json.load(open(f"{R_}/surrogate_events.json")); EV = CM.events(); ST = pd.read_csv(f"{R_}/floor_cycle_T2_states.csv")
OUT = pd.read_csv(f"{CM.L}/study8_outcomes/data/outcomes_per_meeting.csv").set_index("mid")
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan
def near(a, b): a = np.asarray(a, float); b = np.asarray(b, float); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
DEC = {"agreement": r"\b(fica combinado|t[aá] combinado|combinado ent[aã]o|ent[aã]o fica|fechado ent[aã]o|t[aá] fechado|fechou|ficou decidido|decidimos|vamos fazer assim|vamos seguir|ent[aã]o vamos|bora)\b",
       "commitment": r"\b(eu vou (fazer|mandar|ver|falar|ligar|marcar|preparar|enviar|organizar|montar|levantar|atualizar|conversar)|eu fa[cç]o|eu fico (com|respons[aá]vel)|deixa comigo|pode deixar|fica comigo|eu me comprometo|eu mando|eu vejo isso|eu resolvo)\b",
       "deadline": r"\b(at[eé] (segunda|ter[cç]a|quarta|quinta|sexta|amanh[aã]|semana que vem|a pr[oó]xima)|prazo|respons[aá]vel|pr[oó]ximo passo|to-?do|tarefa)\b"}
COL = r"\b(a gente|n[oó]s|nosso|nossa|nossos|nossas)\b"
U = []
for m in CM.meetings():
    tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); R = CM.roles(m)
    f = np.load(f"{CACHE}/{m}_feat.npz", allow_pickle=True); e = np.load(f"{CACHE}/{m}_emo.npz", allow_pickle=True)
    lab = list(f["sent_labels"]); sent = f["sent"][:, lab.index("POS")] - f["sent"][:, lab.index("NEG")]; elab = list(e["labels"]); EM = e["emo"]
    low = tx.text.astype(str).str.lower(); nw = low.str.split().str.len().clip(lower=1)
    d = pd.DataFrame(dict(mid=m, team=CM.team(m), week=Wk[m], t=tx.onset_seconds.to_numpy(), role=tx.speaker_id.astype(str).map(lambda s: R.get(s, "OTHER")).to_numpy(),
                          nw=nw.to_numpy(), q=low.str.count(r"\?").to_numpy(), col=low.str.count(COL).to_numpy(), sent=sent,
                          **{k: low.str.contains(v, regex=True).astype(int).to_numpy() for k, v in DEC.items()}))
    for k_, l_ in enumerate(elab): d[f"emo_{l_}"] = EM[:, k_]
    U.append(d)
U = pd.concat(U, ignore_index=True); EMO = [c for c in U if c.startswith("emo_") and c != "emo_neutral" and U[c].mean() >= .02]
L = []; TU = pd.read_csv(f"{R_}/seqdyn_turns.csv")

# ===================== D. decisions
L.append("D. DECISION MOMENTS (lexicons)")
L.append("  utterances flagged: " + ", ".join(f"{k} {U[k].mean():.3%} (n={U[k].sum()})" for k in DEC))
Mt = U.groupby("mid")[list(DEC)].sum(); Mt["any"] = U.assign(any=(U[list(DEC)].sum(1) > 0).astype(int)).groupby("mid")["any"].sum(); Mt["hours"] = [P[m]["T"] / 3600 for m in Mt.index]
Mt = Mt.join(OUT[["n_todos_assigned", "todo_completion_rate", "n_issues_raised"]])
for k in list(DEC) + ["any"]:
    d = Mt[[k, "n_todos_assigned"]].dropna(); r, p = spearmanr(d[k] / Mt.loc[d.index, "hours"], d.n_todos_assigned); L.append(f"  convergent validity: {k:<10} per hour ~ to-dos assigned (Study 8) rho={r:+.2f} p={p:.3f} n={len(d)}")
U["stage"] = np.concatenate([CM.stage_of_seconds(m, g.t.to_numpy()) for m, g in U.groupby("mid", sort=False)])
U["grp"] = np.where(U.stage.isin(list(CM.REVIEW)), "review", np.where(U.stage == "ids", "IDS", np.where(U.stage == "conclude", "conclude", "other")))
L.append("  share of utterances flagged, by stage group: " + U.groupby("grp")[list(DEC)].mean().mul(100).round(2).to_string().replace("\n", " | "))
stt = []
for m, g in U.groupby("mid", sort=False):
    s = ST[ST.mid == m]; secs = s.sec.to_numpy(); sv = s.state.to_numpy(); stt.append(sv[np.abs(secs[None, :] - g.t.to_numpy()[:, None]).argmin(1)])
U["state"] = np.concatenate(stt)
base = U.state.value_counts(normalize=True)
for k in DEC:
    sh = U[U[k] == 1].state.value_counts(normalize=True); L.append(f"  {k:<10} by floor state (share / share of all utterances): " + ", ".join(f"{s_} {sh.get(s_, 0) / base[s_]:.2f}" for s_ in ("F1", "MIX", "F2")))
# relation to events vs surrogate events: share of decision utterances within 60 s AFTER an event onset
def share_after(evsets, k):
    hit = 0; n = 0
    for m, g in U[U[k] == 1].groupby("mid"):
        ev = np.asarray(evsets[m], float); t = g.t.to_numpy(); n += t.size
        hit += sum(np.any((t0 - ev >= 0) & (t0 - ev <= 60)) for t0 in t) if ev.size else 0
    return hit / max(n, 1)
for k in DEC:
    o = share_after({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in CM.meetings()}, k); s = np.array([share_after({m: SUR[m][j] for m in CM.meetings()}, k) for j in range(20)])
    L.append(f"  {k:<10} utterances within 60 s after an event: {o:.3f} vs surrogate events {s.mean():.3f} (ratio {o/s.mean():.2f}, z {(o-s.mean())/s.std():+.1f})")
# who commits
w_role = U.groupby(["team", "role"]).nw.sum(); c_role = U[U.commitment == 1].groupby(["team", "role"]).size()
L.append("  commitment share / word share by role: " + ", ".join(f"{t}-{r}: {c_role.get((t, r), 0) / c_role.loc[t].sum():.2f}/{w_role[(t, r)] / w_role.loc[t].drop('OTHER', errors='ignore').sum():.2f}" for (t, r) in w_role.index if r != "OTHER"))
# commitments in week w -> to-do completion in week w+1
Mt["team"] = [CM.team(m) for m in Mt.index]; Mt["week"] = [Wk[m] for m in Mt.index]; Mt = Mt.sort_values(["team", "week"])
Mt["commit_h"] = Mt.commitment / Mt.hours; Mt["agree_h"] = Mt.agreement / Mt.hours; Mt["completion_next"] = Mt.groupby("team").todo_completion_rate.shift(-1)
for k in ["commit_h", "agree_h"]:
    d = Mt[[k, "completion_next", "todo_completion_rate", "team"]].dropna()
    if len(d) > 12:
        f_ = smf.ols(f"completion_next ~ {k} + todo_completion_rate + team", data=d.assign(**{k: (d[k] - d[k].mean()) / d[k].std()})).fit()
        L.append(f"  {k} in week w -> to-do completion in w+1: beta={f_.params[k]:+.2f} p={f_.pvalues[k]:.3f} n={len(d)}")
for t, g in Mt.groupby("team"):
    L.append(f"  team {t} trends over weeks: commitments/h tau={kendalltau(g.week, g.commit_h)[0]:+.2f} (p={kendalltau(g.week, g.commit_h)[1]:.3f}); agreements/h tau={kendalltau(g.week, g.agree_h)[0]:+.2f} (p={kendalltau(g.week, g.agree_h)[1]:.3f})")
Mt.to_csv(f"{R_}/ped_decisions_meeting.csv")

# ===================== E. emotions
L.append(f"\nE. EMOTIONS (categories with mean probability >= .02: {', '.join(c[4:] for c in EMO)})")
rows = []
G5 = {}
for m, g in U.groupby("mid", sort=False):
    T = P[m]["T"]; grid = np.arange(60, T - 60, 5.0); t = g.t.to_numpy(); w = g.nw.to_numpy(float); a = np.searchsorted(t, grid - 60); b = np.searchsorted(t, grid + 60)
    cs = np.vstack([np.zeros((1, len(EMO))), np.cumsum(g[EMO].to_numpy() * w[:, None], 0)]); cw = np.concatenate(([0], np.cumsum(w)))
    V = (cs[b] - cs[a]) / np.maximum(cw[b] - cw[a], 1)[:, None]; Z = (V - V.mean(0)) / V.std(0)
    s = ST[ST.mid == m].set_index("sec").state.reindex(grid, method="nearest").to_numpy(); stg = CM.stage_of_seconds(m, grid)
    grp = np.where(np.isin(stg, list(CM.REVIEW)), "review", np.where(stg == "ids", "IDS", "other")); G5[m] = (grid, Z)
    r = dict(mid=m, team=CM.team(m), week=Wk[m])
    for j, c in enumerate(EMO):
        r[f"{c}_F2mF1"] = np.nanmean(Z[s == "F2", j]) - np.nanmean(Z[s == "F1", j]); r[f"{c}_IDSmREV"] = np.nanmean(Z[grp == "IDS", j]) - np.nanmean(Z[grp == "review", j]); r[f"{c}_mean"] = V[:, j].mean()
    rows.append(r)
EM_ = pd.DataFrame(rows); EM_.to_csv(f"{R_}/ped_emotions_meeting.csv", index=False)
def sig(evsets, j, lags=(-30, 0, 30, 60)):
    out = []
    for lg in lags:
        v = []
        for m, (grid, Z) in G5.items():
            for t0 in np.asarray(evsets[m], float):
                k = np.searchsorted(grid, t0 + lg)
                if 0 <= k < grid.size and abs(grid[k] - (t0 + lg)) <= 5: v.append(Z[k, j])
        out.append(np.nanmean(v))
    return np.array(out)
L.append(f"  {'emotion':<16}{'F2-F1':>9}{'IDS-review':>12}  event signature at -30/0/+30/+60 s (observed minus surrogate; * outside surrogate 95 %)   weekly tau A / B")
for j, c in enumerate(EMO):
    o = sig({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in CM.meetings()}, j); S_ = np.array([sig({m: SUR[m][k] for m in CM.meetings()}, j) for k in range(20)])
    lo, hi = np.percentile(S_, [2.5, 97.5], 0); ex = " ".join(f"{x:+.2f}{'*' if (oo > h or oo < l) else ' '}" for x, oo, l, h in zip(o - S_.mean(0), o, lo, hi))
    f2 = EM_[f"{c}_F2mF1"]; ids = EM_[f"{c}_IDSmREV"]
    ta = kendalltau(EM_[EM_.team == "A"].week, EM_[EM_.team == "A"][f"{c}_mean"]); tb = kendalltau(EM_[EM_.team == "B"].week, EM_[EM_.team == "B"][f"{c}_mean"])
    L.append(f"  {c[4:]:<16}{f2.mean():+.2f}{'**' if wp(f2) < .01 else ('* ' if wp(f2) < .05 else '  ')}{ids.mean():+.2f}{'**' if wp(ids) < .01 else ('* ' if wp(ids) < .05 else '  ')}       {ex}      {ta[0]:+.2f}{'+' if ta[1] < .05 else ' '} / {tb[0]:+.2f}{'+' if tb[1] < .05 else ' '}")

# ===================== P. persons
L.append("\nP. PERSON TRAJECTORIES (per role and meeting; Kendall tau over weeks; * q < .05 within the person table, + p < .05)")
U["long"] = 0
lt = TU[TU.dur >= 30].groupby(["mid", "role"]).size()
pp = U[U.role != "OTHER"].groupby(["mid", "team", "week", "role"]).agg(words=("nw", "sum"), q=("q", "sum"), col=("col", "sum"), sent=("sent", "mean"), commit=("commitment", "sum"),
                                                                            **{c: (c, "mean") for c in ["emo_curiosity", "emo_confusion", "emo_approval", "emo_annoyance", "emo_optimism"] if c in U}).reset_index()
tot = pp.groupby("mid").words.transform("sum"); pp["word_share"] = pp.words / tot; pp["q100"] = 100 * pp.q / pp.words; pp["col100"] = 100 * pp.col / pp.words
pp["long_per_h"] = [lt.get((m, r), 0) / (P[m]["T"] / 3600) for m, r in zip(pp.mid, pp.role)]; pp.to_csv(f"{R_}/ped_persons_meeting.csv", index=False)
VARS = ["word_share", "q100", "col100", "long_per_h", "sent", "commit"] + [c for c in ["emo_curiosity", "emo_confusion", "emo_approval", "emo_annoyance", "emo_optimism"] if c in pp]
rows = []
for (t, r), g in pp.groupby(["team", "role"]):
    for v in VARS:
        if g[v].notna().sum() > 6: tau, p = kendalltau(g.week, g[v]); rows.append(dict(team=t, role=r, var=v, tau=tau, p=p, n=g[v].notna().sum()))
PT = pd.DataFrame(rows); PT["q"] = multipletests(PT.p.fillna(1), method="fdr_bh")[1]; PT.to_csv(f"{R_}/ped_persons_trends.csv", index=False)
piv = PT.assign(cell=[f"{a:+.2f}{'*' if q < .05 else ('+' if p < .05 else ' ')}" for a, p, q in zip(PT.tau, PT.p, PT.q)]).pivot_table(index=["team", "role"], columns="var", values="cell", aggfunc="first")
L.append(piv[[v for v in VARS if v in piv]].to_string())
L.append(f"  meetings attended: " + ", ".join(f"{t}-{r} {g.mid.nunique()}" for (t, r), g in pp.groupby(["team", "role"])))
for t, g in pp[pp.role != "FACILITATOR"].groupby("team"):
    gi = g.groupby("week").word_share.apply(lambda x: (np.abs(x.values[:, None] - x.values[None, :]).sum() / (2 * len(x) ** 2 * x.mean())) if len(x) > 1 else np.nan)
    h1 = g[g.week <= 8].groupby("role").word_share.mean(); h2 = g[g.week > 8].groupby("role").word_share.mean(); j = h1.index.intersection(h2.index)
    L.append(f"  team {t}: member inequality (Gini of word shares) over weeks tau={kendalltau(gi.index, gi.values)[0]:+.2f} p={kendalltau(gi.index, gi.values)[1]:.3f}; member ranking first vs second half: " + ", ".join(f"{r_} {h1[r_]:.2f}->{h2[r_]:.2f}" for r_ in j))
open(f"{R_}/ped_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
