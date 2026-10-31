"""Label-free content dynamics II (utterance embeddings and lemmas from the local cache; outputs numeric only).
C. Content recurrence. 60-s windows every 10 s, word-weighted mean sentence embedding.
   C1 within meeting: 'return' = maximum similarity of a window to any window >= 10 min earlier in the same meeting
      (coming back to an earlier subject), residualized on log words and number of speakers in the window.
   C2 across weeks: 'recurrence' = maximum similarity to any window of the team's earlier meetings MINUS the same against
      the other team's meetings of the same dates (both teams use the same agenda format, so generic meeting language
      cancels out). Trend over weeks; event rate in high- vs low-recurrence windows (meeting fixed effects).
D. Vocabulary diffusion. Content lemmas new to a team (absent from its first two meetings, >= 5 uses overall):
   who introduces them (role of the first user; lift = share of introductions / share of words), whether another role
   adopts them in a later meeting, and whether introductions fall near reorganization events (+/-30 s, circular shift).
E. Lexical markers per 100 words in 60-s windows: collective 'a gente / nós / nosso / vamos', self 'eu / meu / minha',
   addressee 'você / vocês', hedges, certainty, contrast / negation, action / decision, and '?' (transcriber punctuation).
   Residualized on log words and speakers; at events (+/-15 s vs >= 90 s), before events ([-150, -30] vs >= 90 s), by
   floor state, and by agenda stage group.
Output: results/content2_*.csv, results/content2_summary.txt"""
import sys, os, re, json, numpy as np, pandas as pd
import statsmodels.formula.api as smf, statsmodels.api as sm
from scipy.stats import wilcoxon, kendalltau
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
rng = np.random.default_rng(141); CACHE = f"{CM.L}/data/semantic_cache"
P = json.load(open(f"{CM.RES}/partitions_bounds.json")); EV = CM.events(); ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv"); Wk = CM.week_map()
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan
def near(a, b): a = np.asarray(a); b = np.asarray(b); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
MARK = {"collective": r"\b(a gente|n[oó]s|nosso|nossa|nossos|nossas|vamos)\b", "self": r"\b(eu|meu|minha|meus|minhas)\b", "addressee": r"\b(voc[eê]s?)\b",
        "hedge": r"\b(acho|talvez|meio que|de repente|sei l[aá]|pode ser|provavelmente|tipo assim)\b", "certainty": r"\b(com certeza|certeza|claro|sempre|nunca|obviamente|definitivamente|exatamente)\b",
        "contrast": r"\b(n[aã]o|mas|por[eé]m|s[oó] que|entretanto|contudo)\b", "action": r"\b(vamos|fica combinado|combinado|decid\w*|pr[oó]ximo passo|tem que|precisa\w*|prazo|respons[aá]vel|at[eé] (segunda|ter[cç]a|quarta|quinta|sexta|amanh[aã]))\b",
        "question": r"\?"}
MIDS = CM.meetings(); WIN = {}; L = []
for m in MIDS:
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); on = z["onset"]; E = z["emb"].astype(float); nw = np.maximum(z["nw"], 1).astype(float); spk = z["speaker"]
    tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); txt = tx.text.astype(str).str.lower().tolist()
    cnt = np.array([[len(re.findall(p, t)) for p in MARK.values()] for t in txt], float)
    T_ = P[m]["T"]; grid = np.arange(30, T_ - 30, 10.0); a = np.searchsorted(on, grid - 30); b = np.searchsorted(on, grid + 30)
    cs = np.vstack([np.zeros((1, E.shape[1])), np.cumsum(E * nw[:, None], 0)]); V = cs[b] - cs[a]; nv = np.linalg.norm(V, axis=1); ok = nv > 0; V[ok] /= nv[ok, None]
    cw = np.concatenate(([0], np.cumsum(nw))); words = cw[b] - cw[a]; cc = np.vstack([np.zeros((1, cnt.shape[1])), np.cumsum(cnt, 0)]); C_ = cc[b] - cc[a]
    nsp = np.array([len(set(spk[x:y])) for x, y in zip(a, b)])
    WIN[m] = dict(grid=grid, V=V, ok=ok, words=words, nsp=nsp, marks=C_)
# ---------- C1 within-meeting return
rows = []
for m in MIDS:
    w = WIN[m]; g = w["grid"]; V = w["V"]; ok = w["ok"]; S = V @ V.T; ret = np.full(g.size, np.nan)
    for i in range(g.size):
        j = g <= g[i] - 600
        if ok[i] and (j & ok).any(): ret[i] = S[i, j & ok].max()
    d = pd.DataFrame(dict(mid=m, sec=g, ret=ret, lw=np.log1p(w["words"]), nsp=w["nsp"])).dropna()
    d["ret_res"] = smf.ols("ret ~ lw + nsp", data=d).fit().resid if len(d) > 20 else np.nan
    w["ret"] = pd.Series(d.ret_res.values, index=d.sec.values).reindex(g).to_numpy(); rows.append(d)
R1 = pd.concat(rows)
# ---------- C2 cross-week recurrence (same team minus other team)
team = {m: CM.team(m) for m in MIDS}; date = {m: m[:10] for m in MIDS}
for m in MIDS:
    w = WIN[m]; same = [x for x in MIDS if team[x] == team[m] and date[x] < date[m]]; other = [x for x in MIDS if team[x] != team[m] and date[x] < date[m]]
    if not same or not other: w["rec"] = np.full(w["grid"].size, np.nan); continue
    k = min(len(same), len(other)); same = sorted(same)[-k:]; other = sorted(other)[-k:]
    def mx(ms): M_ = np.vstack([WIN[x]["V"][WIN[x]["ok"]] for x in ms]); return (w["V"] @ M_.T).max(1)
    rec = mx(same) - mx(other); rec[~w["ok"]] = np.nan; w["rec"] = rec
# event-window analyses
L.append("C. CONTENT RECURRENCE")
rows = []
for m in MIDS:
    w = WIN[m]; g = w["grid"]; ev = EV[EV.mid == m].event_onset_s.to_numpy(); de = near(g, ev)
    s = ST[ST.mid == m].set_index("sec").state.reindex(g, method="nearest").to_numpy()
    r = dict(mid=m, team=team[m], week=Wk[m])
    for key in ["ret", "rec"]:
        x = w[key]
        if np.all(np.isnan(x)): continue
        zx = (x - np.nanmean(x)) / np.nanstd(x)
        r[f"{key}_event"] = np.nanmean(zx[de <= 15]) - np.nanmean(zx[de >= 90])
        pre = np.array([np.any((ev - t >= 30) & (ev - t <= 150)) for t in g]); r[f"{key}_pre"] = np.nanmean(zx[pre & (de > 15)]) - np.nanmean(zx[de >= 90])
        for st in ("F1", "F2"): r[f"{key}_{st}"] = np.nanmean(zx[s == st])
        r[f"{key}_mean"] = np.nanmean(x)
    rows.append(r)
C = pd.DataFrame(rows); C.to_csv(f"{CM.RES}/content2_recurrence_meeting.csv", index=False)
for key, lab in [("ret", "return to an earlier subject (>= 10 min before, same meeting)"), ("rec", "recurrence from earlier weeks (same team minus other team)")]:
    L.append(f"  {lab}")
    L.append(f"    at events d={C[key+'_event'].mean():+.3f} (p={wp(C[key+'_event']):.1e}); 2 min before events d={C[key+'_pre'].mean():+.3f} (p={wp(C[key+'_pre']):.1e}); F1 {C[key+'_F1'].mean():+.3f} vs F2 {C[key+'_F2'].mean():+.3f} (p={wp(C[key+'_F2']-C[key+'_F1']):.1e})")
for t, g in C.dropna(subset=["rec_mean"]).groupby("team"):
    tau, p = kendalltau(g.week, g.rec_mean); L.append(f"  team {t}: mean cross-week recurrence {g.rec_mean.mean():+.4f} (> 0 means own past dominates; p={wp(g.rec_mean):.1e}); trend over weeks tau={tau:+.2f} p={p:.3f}")
# event rate by recurrence tercile (within meeting)
rr = []
for m in MIDS:
    w = WIN[m]; x = w["rec"]
    if np.all(np.isnan(x)): continue
    ev = EV[EV.mid == m].event_onset_s.to_numpy(); q = pd.qcut(pd.Series(x).rank(method="first"), 3, labels=["low", "mid", "high"])
    for lab in ["low", "mid", "high"]:
        sel = (q == lab).to_numpy() & ~np.isnan(x); rr.append(dict(mid=m, tercile=lab, events_per_10min=600 * sum(np.any(np.abs(ev - t) <= 5) for t in w["grid"][sel]) / max(1, sel.sum() * 10)))
RR = pd.DataFrame(rr).pivot(index="mid", columns="tercile", values="events_per_10min")
L.append(f"  event rate (per 10 min) by cross-week recurrence tercile: low {RR['low'].mean():.2f}, mid {RR['mid'].mean():.2f}, high {RR['high'].mean():.2f} (high - low p={wp(RR['high']-RR['low']):.3f})")

# ---------- D vocabulary diffusion
D_ = []
for t in "AB":
    ms = sorted([m for m in MIDS if team[m] == t], key=lambda m: Wk[m]); uses = []; words_by_role = {}
    for m in ms:
        z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); lem = json.load(open(f"{CACHE}/{m}_lemmas.json")); R = CM.roles(m)
        for i, (u, s) in enumerate(zip(lem, z["speaker"])):
            role = R.get(str(s), "OTHER"); words_by_role[role] = words_by_role.get(role, 0) + z["nw"][i]
            for l in set(u): uses.append((Wk[m], m, z["onset"][i], role, l))
    U = pd.DataFrame(uses, columns=["week", "mid", "t", "role", "lemma"]); base = set(U[U.week <= 2].lemma); tot = U.lemma.value_counts()
    cand = [l for l in tot.index if tot[l] >= 5 and l not in base]
    for l in cand:
        u = U[U.lemma == l].sort_values(["week", "t"]); first = u.iloc[0]
        if first.role == "OTHER": continue
        later = u[(u.week > first.week) & (u.role != first.role) & (u.role != "OTHER")]
        D_.append(dict(team=t, lemma_id=hash(l) % 10**8, week=first.week, mid=first.mid, t=first.t, introducer=first.role, adopted=int(len(later) > 0),
                       n_adopters=later.role.nunique(), uses=int(tot[l])))
    wr = pd.Series(words_by_role); wr = wr[wr.index != "OTHER"]; D_share = wr / wr.sum()
    for r_ in D_share.index: D_.append(dict(team=t, lemma_id=-1, introducer=r_, word_share=D_share[r_]))
DF = pd.DataFrame(D_); DF.to_csv(f"{CM.RES}/content2_diffusion.csv", index=False)
L.append("\nD. VOCABULARY DIFFUSION (lemmas new to the team after week 2, >= 5 uses)")
for t, g in DF.groupby("team"):
    lem = g[g.lemma_id >= 0]; ws = g[g.lemma_id == -1].set_index("introducer").word_share
    intro = lem.introducer.value_counts(normalize=True); ad = lem.groupby("introducer").adopted.mean()
    L.append(f"  team {t}: {len(lem)} new lemmas; adopted by another role later {lem.adopted.mean():.2f}")
    for r_ in sorted(intro.index):
        L.append(f"    {r_:<12} introduces {intro[r_]:.2f} of new lemmas (word share {ws.get(r_, np.nan):.2f}, lift {intro[r_]/ws.get(r_, np.nan):.2f}); adoption {ad.get(r_, np.nan):.2f}")
lem = DF[DF.lemma_id >= 0]; obs = 0; nul = np.zeros(300)
for m, g in lem.groupby("mid"):
    ev = EV[EV.mid == m].event_onset_s.to_numpy(); T_ = P[m]["T"]; obs += int(np.sum(near(g.t, ev) <= 30))
    for s in range(300): nul[s] += np.sum(near(g.t, (ev + rng.uniform(0, T_)) % T_) <= 30)
L.append(f"  introductions within +/-30 s of an event: ratio {obs/nul.mean():.2f} (p enrich={(np.sum(nul>=obs)+1)/301:.3f}); adoption of lemmas introduced near events vs elsewhere:")
lem = lem.assign(near_ev=[near([t], EV[EV.mid == m].event_onset_s.to_numpy())[0] <= 30 for t, m in zip(lem.t, lem.mid)])
L.append(f"    near {lem[lem.near_ev].adopted.mean():.2f} (n={lem.near_ev.sum()}) vs elsewhere {lem[~lem.near_ev].adopted.mean():.2f} (n={(~lem.near_ev).sum()})")
r = smf.logit("adopted ~ near_ev + C(introducer) + np.log(uses)".replace("C(", "Q('x')*0+C(") if False else "adopted ~ near_ev + np.log(uses) + fac", data=lem.assign(near_ev=lem.near_ev.astype(int), fac=(lem.introducer == "FACILITATOR").astype(int))).fit(disp=False)
L.append(f"    logit adoption: near event OR={np.exp(r.params['near_ev']):.2f} p={r.pvalues['near_ev']:.3f}; facilitator introducer OR={np.exp(r.params['fac']):.2f} p={r.pvalues['fac']:.3f}")

# ---------- E markers
L.append("\nE. LEXICAL MARKERS (per 100 words, residualized on log words and speakers; standardized differences)")
rows = []
for m in MIDS:
    w = WIN[m]; g = w["grid"]; ev = EV[EV.mid == m].event_onset_s.to_numpy(); de = near(g, ev)
    s = ST[ST.mid == m].set_index("sec").state.reindex(g, method="nearest").to_numpy(); stg = CM.stage_of_seconds(m, g)
    grp = np.where(np.isin(stg, list(CM.REVIEW)), "review", np.where(stg == "ids", "IDS", "other"))
    pre = np.array([np.any((ev - t >= 30) & (ev - t <= 150)) for t in g]) & (de > 15)
    r = dict(mid=m)
    for k_, name in enumerate(MARK):
        rate = 100 * w["marks"][:, k_] / np.maximum(w["words"], 1); ok = w["words"] >= 20
        d = pd.DataFrame(dict(y=rate, lw=np.log1p(w["words"]), nsp=w["nsp"]))[ok]
        res = np.full(g.size, np.nan); res[ok] = smf.ols("y ~ lw + nsp", data=d).fit().resid if len(d) > 30 else np.nan; zx = (res - np.nanmean(res)) / np.nanstd(res)
        r[f"{name}_event"] = np.nanmean(zx[de <= 15]) - np.nanmean(zx[de >= 90]); r[f"{name}_pre"] = np.nanmean(zx[pre]) - np.nanmean(zx[de >= 90])
        r[f"{name}_F2mF1"] = np.nanmean(zx[s == "F2"]) - np.nanmean(zx[s == "F1"]); r[f"{name}_IDSmREV"] = np.nanmean(zx[grp == "IDS"]) - np.nanmean(zx[grp == "review"])
    rows.append(r)
E_ = pd.DataFrame(rows); E_.to_csv(f"{CM.RES}/content2_markers.csv", index=False)
L.append(f"  {'marker':<11} {'at event':>16} {'2 min before':>16} {'F2 minus F1':>16} {'IDS minus review':>18}")
for name in MARK:
    cells = []
    for c in ["event", "pre", "F2mF1", "IDSmREV"]:
        x = E_[f"{name}_{c}"]; p = wp(x); cells.append(f"{x.mean():+.3f}{'**' if p < .01 else ('*' if p < .05 else '  ')}")
    L.append(f"  {name:<11} {cells[0]:>16} {cells[1]:>16} {cells[2]:>16} {cells[3]:>18}")
L.append("  (* p < .05, ** p < .01, Wilcoxon over 34 meetings)")
open(f"{CM.RES}/content2_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
