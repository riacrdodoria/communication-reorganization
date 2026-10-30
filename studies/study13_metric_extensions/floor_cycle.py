"""The inject-and-integrate cycle: five tests of how individual floor flow (F1, singly-developed floor) and collective
transitions (F2, collaborative floor) relate. Boundary sets from partitions.py (partitions_bounds.json).
T1 Inject -> integrate. Long turns (one speaker >= 30 s). Outcomes after the turn ends (te): a reorganization event in
   [te-10, te+60]; lexical uptake = cosine(TF-IDF of the long turn, TF-IDF of OTHER speakers in (te, te+120]) minus the
   same with a random 120-s stretch of other speakers >= 300 s away (10 draws). Predictors: the turn's residual lexical
   novelty (z within meeting), log duration, facilitator vs member, IDS stage; logistic and OLS with meeting fixed
   effects. Comparison: ends of 10-30 s turns. Also residual topic entropy at events preceded by a long-turn end.
T2 Floor states every 5 s (60-s windows): F1 = top-speaker share >= .70; F2 = >= 3 active speakers and top share < .50;
   MIX otherwise. Content by state (residual novelty and topic entropy); state at each boundary type vs time share
   (pooled enrichment, 500 circular shifts); run transitions and dwell times.
T3 Two origins of topics. Topic boundaries opened by an extended floor turn only (long-turn onset within +/-30 s, no
   event), by a collective event only, by both, or by neither. Episode duration, events per minute, distinct speakers,
   mean entropy, novelty in the first 60 s, facilitator as opener. Within-meeting Wilcoxon, individual vs collective.
T4 Does centralization modulate the clocks? 5-min blocks: Freeman degree centralization of the role transition
   network (src floor_measures), top-speaker share; counts of collective (event + topic) and individual (long-turn onset
   + level shift) boundaries. Poisson GLM with meeting fixed effects, next block on current centralization (lagged)
   controlling for the current count.
T5 The two clocks by stage: enrichment of key pairs (+/-30 s) with reference boundaries in review vs IDS.
Output: results/floor_cycle_*.csv, results/floor_cycle_summary.txt"""
import sys, os, re, json, numpy as np, pandas as pd
import statsmodels.formula.api as smf, statsmodels.api as sm
from scipy.stats import wilcoxon
from sklearn.feature_extraction.text import TfidfVectorizer
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
sys.path.insert(0, CM.L); import floor_measures as FM
rng = np.random.default_rng(101)
BND = json.load(open(f"{CM.RES}/partitions_bounds.json")); CW = pd.read_csv(f"{CM.RES}/content_windows.csv"); BW = pd.read_csv(f"{CM.RES}/battery_windows.csv")
SW = set(w.strip().lower() for w in open(f"{CM.L}/data/stopwords-pt.txt", encoding="utf-8") if w.strip())
tok = lambda s: [w for w in re.findall(r"[a-záàâãéêíóôõúüç]+", str(s).lower()) if len(w) >= 3 and w not in SW]
def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b); return float(a @ b / (na * nb)) if na > 0 and nb > 0 else np.nan
def near(a, b): return np.min(np.abs(np.asarray(a)[:, None] - np.asarray(b)[None, :]), 1) if len(b) and len(a) else np.full(len(a), 1e9)
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return (wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan), len(x)
L = []; T1 = []; T3 = []; T4 = []; STATE = []

for mid in CM.meetings():
    b = {k: np.array(v, float) for k, v in BND[mid].items() if k != "T"}; Tm = BND[mid]["T"]
    tx = CM.transcript(mid); tx = tx[tx.text.notna()].reset_index(drop=True); R = CM.roles(mid)
    sp = tx.speaker_id.astype(str).to_numpy(); on = tx.onset_seconds.to_numpy()
    k = np.concatenate(([True], sp[1:] != sp[:-1])); st_i = np.flatnonzero(k); en_i = np.concatenate((st_i[1:], [len(sp)]))
    ts = on[st_i]; te = np.concatenate((ts[1:], [on.max() + 5])); dur = te - ts; tsp = sp[st_i]
    vec = TfidfVectorizer(tokenizer=tok, lowercase=False, token_pattern=None, min_df=2, sublinear_tf=True)
    X = vec.fit_transform(tx.text.astype(str)).toarray()
    TV = np.array([X[a:c].sum(0) for a, c in zip(st_i, en_i)])
    cw = CW[CW.mid == mid]; nz = (cw.novelty_res - cw.novelty_res.mean()) / cw.novelty_res.std()
    stg = CM.stage_of_seconds(mid, ts)
    def other_text(a, c, who):
        m = (ts > a) & (ts <= c) & (tsp != who); return TV[m].sum(0) if m.any() else np.zeros(TV.shape[1])
    # ---- T1
    for i in np.flatnonzero(dur >= 10):
        a, e = ts[i], te[i]; who = tsp[i]
        sel = (cw.sec >= a) & (cw.sec <= e); nov = nz[sel].mean() if sel.any() else np.nan
        ev = b["event"]; y = int(np.any((ev >= e - 10) & (ev <= e + 60)))
        up = cos(TV[i], other_text(e, e + 120, who))
        far = [x for x in ts if abs(x - e) >= 300]
        upn = np.nanmean([cos(TV[i], other_text(s0, s0 + 120, who)) for s0 in rng.choice(far, size=min(10, len(far)), replace=False)]) if far else np.nan
        T1.append(dict(mid=mid, dur=dur[i], long=int(dur[i] >= 30), nov_z=nov, event60=y, uptake=up, uptake_null=upn,
                       fac=int(R.get(who, "OTHER") == "FACILITATOR"), ids=int(stg[i] == "ids"), te=e))
    # ---- T2 states
    bw = BW[BW.mid == mid].copy()
    bw["state"] = np.where(bw.top_share >= .70, "F1", np.where((bw.active >= 3) & (bw.top_share < .50), "F2", "MIX"))
    m2 = bw.merge(cw[["sec", "novelty_res", "topic_entropy_res"]], on="sec", how="left"); m2["mid"] = mid; STATE.append(m2[["mid", "sec", "state", "novelty_res", "topic_entropy_res", "entropy"]])
    # ---- T3 topic origins
    tb = np.sort(b["topic"]); ends = np.concatenate((tb[1:], [Tm]))
    g = CM.metrics(mid).set_index("second").entropy_g
    for x0, x1 in zip(tb, ends):
        ind = near([x0], b["floor"])[0] <= 30; col = near([x0], b["event"])[0] <= 30
        cls = "both" if ind and col else ("individual" if ind else ("collective" if col else "neither"))
        inside = (ts >= x0 - 5) & (ts < x1); opener = tsp[inside][0] if inside.any() else None
        evr = np.sum((b["event"] > x0 + 30) & (b["event"] < x1)) / max(1e-9, (x1 - x0 - 30) / 60) if x1 - x0 > 60 else np.nan
        sel = (cw.sec >= x0) & (cw.sec < x0 + 60)
        T3.append(dict(mid=mid, cls=cls, dur_min=(x1 - x0) / 60, events_per_min=evr, n_spk=len(set(tsp[inside])),
                       entropy=g.loc[(g.index >= x0) & (g.index < x1)].mean(), nov_first60=cw.novelty_res[sel].mean() if sel.any() else np.nan,
                       fac_opener=int(opener is not None and R.get(opener, "OTHER") == "FACILITATOR"), stage=CM.stage_of_seconds(mid, np.array([x0]))[0]))
    # ---- T4 5-min blocks
    people = sorted(set(tsp)); idx = {p: j for j, p in enumerate(people)}
    for s0 in np.arange(0, Tm - 300, 300):
        m = (ts >= s0) & (ts < s0 + 300); seq = tsp[m]; W = np.zeros((len(people), len(people)))
        for p, q in zip(seq[:-1], seq[1:]): W[idx[p], idx[q]] += 1
        bb = bw[(bw.sec >= s0) & (bw.sec < s0 + 300)]
        cnt = lambda key: int(np.sum((b[key] >= s0) & (b[key] < s0 + 300)))
        T4.append(dict(mid=mid, s0=s0, central=FM.degree_centralization(W), top_share=bb.top_share.mean(), collective=cnt("event") + cnt("topic"),
                       individual=cnt("floor") + cnt("level"), stage=pd.Series(CM.stage_of_seconds(mid, np.arange(s0, s0 + 300, 10))).mode()[0]))
    print(mid, flush=True)

A = pd.DataFrame(T1); A.to_csv(f"{CM.RES}/floor_cycle_T1_turns.csv", index=False)
S = pd.concat(STATE); S.to_csv(f"{CM.RES}/floor_cycle_T2_states.csv", index=False)
B3 = pd.DataFrame(T3); B3.to_csv(f"{CM.RES}/floor_cycle_T3_topics.csv", index=False)
B4 = pd.DataFrame(T4); B4.to_csv(f"{CM.RES}/floor_cycle_T4_blocks.csv", index=False)

# ===================== T1
L.append("T1. INJECT -> INTEGRATE (long turns >= 30 s vs 10-30 s turns)")
for lab, g in [("long (>=30 s)", A[A.long == 1]), ("short (10-30 s)", A[A.long == 0])]:
    L.append(f"  {lab}: n={len(g)}; event within [-10, +60] s of turn end {g.event60.mean():.3f}; uptake {g.uptake.mean():.4f} vs far null {g.uptake_null.mean():.4f}")
# circular-shift expectation for long-turn ends
obs = A[A.long == 1].event60.sum(); null = []
for _ in range(500):
    h = 0
    for mid, g in A[A.long == 1].groupby("mid"):
        ev = (np.array(BND[mid]["event"]) + rng.uniform(0, BND[mid]["T"])) % BND[mid]["T"]; e = g.te.to_numpy()
        h += int(np.sum([np.any((ev >= x - 10) & (ev <= x + 60)) for x in e]))
    null.append(h)
L.append(f"  long-turn ends followed by an event: observed {obs} vs circular-shift {np.mean(null):.1f} (ratio {obs/np.mean(null):.2f}, p={(np.sum(np.array(null)>=obs)+1)/501:.3f})")
d = A[A.long == 1].dropna(subset=["nov_z"]).copy(); d["ldur"] = np.log(d.dur)
r = smf.logit("event60 ~ nov_z + ldur + fac + ids + mid", data=d).fit(disp=False)
L.append(f"  logit event60 (long turns, meeting FE, n={len(d)}): novelty OR={np.exp(r.params['nov_z']):.3f} p={r.pvalues['nov_z']:.3f}; log duration OR={np.exp(r.params['ldur']):.3f} p={r.pvalues['ldur']:.3f}; facilitator OR={np.exp(r.params['fac']):.3f} p={r.pvalues['fac']:.3f}")
d["integ"] = d.uptake - d.uptake_null
r2 = smf.ols("integ ~ nov_z + ldur + fac + ids + event60 + mid", data=d.dropna(subset=["integ"])).fit()
L.append(f"  integration (uptake minus null) mean {d.integ.mean():+.4f} (meeting-level Wilcoxon p={wp(d.groupby('mid').integ.mean())[0]:.1e})")
L.append(f"  OLS integration: novelty b={r2.params['nov_z']:+.4f} p={r2.pvalues['nov_z']:.3f}; event follows b={r2.params['event60']:+.4f} p={r2.pvalues['event60']:.3f}; facilitator b={r2.params['fac']:+.4f} p={r2.pvalues['fac']:.3f}; log dur b={r2.params['ldur']:+.4f} p={r2.pvalues['ldur']:.3f}")
# topic entropy at events preceded by a long-turn end
rows = []
for mid in CM.meetings():
    ev = np.array(BND[mid]["event"]); lt_end = A[(A.mid == mid) & (A.long == 1)].te.to_numpy(); cw = CW[CW.mid == mid]
    if ev.size == 0 or cw.empty: continue
    pre = np.array([np.any((lt_end >= x - 60) & (lt_end <= x + 10)) for x in ev])
    te_at = np.array([cw.topic_entropy_res[np.abs(cw.sec - x) <= 5].mean() for x in ev]); nv_at = np.array([cw.novelty_res[np.abs(cw.sec - x) <= 5].mean() for x in ev])
    rows.append(dict(mid=mid, share_pre=pre.mean(), te_pre=np.nanmean(te_at[pre]) if pre.any() else np.nan, te_other=np.nanmean(te_at[~pre]) if (~pre).any() else np.nan,
                     nv_pre=np.nanmean(nv_at[pre]) if pre.any() else np.nan, nv_other=np.nanmean(nv_at[~pre]) if (~pre).any() else np.nan))
E1 = pd.DataFrame(rows)
L.append(f"  events preceded by a long-turn end (within 60 s): {E1.share_pre.mean():.3f} of events; topic entropy at them {E1.te_pre.mean():+.4f} vs other events {E1.te_other.mean():+.4f} (p={wp(E1.te_pre-E1.te_other)[0]:.3f}); novelty {E1.nv_pre.mean():+.4f} vs {E1.nv_other.mean():+.4f} (p={wp(E1.nv_pre-E1.nv_other)[0]:.3f})")

# ===================== T2
L.append("\nT2. FLOOR STATES (5-s grid, 60-s windows)")
L.append("  time share: " + S.state.value_counts(normalize=True).round(3).to_dict().__str__())
cs = S.groupby(["mid", "state"])[["novelty_res", "topic_entropy_res"]].mean().unstack()
for v in ["novelty_res", "topic_entropy_res"]:
    L.append(f"  {v} by state (mean of meeting means): F1 {cs[v]['F1'].mean():+.4f}  MIX {cs[v]['MIX'].mean():+.4f}  F2 {cs[v]['F2'].mean():+.4f}; F1 vs F2 Wilcoxon p={wp(cs[v]['F1']-cs[v]['F2'])[0]:.1e}")
# boundaries by state
rows = []
for key in ["agenda", "topic", "event", "level", "floor", "novelty"]:
    obs = {"F1": 0, "MIX": 0, "F2": 0}; nul = {s: [] for s in obs}
    for _ in range(301): pass
    for mid in CM.meetings():
        s = S[S.mid == mid]; secs = s.sec.to_numpy(); stt = s.state.to_numpy(); bb = np.array(BND[mid][key])
        if bb.size == 0: continue
        j = np.abs(secs[None, :] - bb[:, None]).argmin(1)
        for x in stt[j]: obs[x] += 1
    tot = sum(obs.values()); base = S.state.value_counts(normalize=True)
    nulls = {s: [] for s in obs}
    for _ in range(300):
        c = {s: 0 for s in obs}
        for mid in CM.meetings():
            s = S[S.mid == mid]; secs = s.sec.to_numpy(); stt = s.state.to_numpy(); bb = np.array(BND[mid][key]); Tm = BND[mid]["T"]
            if bb.size == 0: continue
            sh = (bb + rng.uniform(0, Tm)) % Tm; j = np.abs(secs[None, :] - sh[:, None]).argmin(1)
            for x in stt[j]: c[x] += 1
        for s_ in c: nulls[s_].append(c[s_])
    rows.append(dict(boundary=key, n=tot, **{f"{s_}_ratio": obs[s_] / np.mean(nulls[s_]) for s_ in obs},
                     **{f"{s_}_p_enrich": (np.sum(np.array(nulls[s_]) >= obs[s_]) + 1) / 301 for s_ in obs}, **{f"{s_}_p_deplete": (np.sum(np.array(nulls[s_]) <= obs[s_]) + 1) / 301 for s_ in obs}))
SB = pd.DataFrame(rows); SB.to_csv(f"{CM.RES}/floor_cycle_T2_boundaries.csv", index=False)
L.append("  state at boundary, observed / circular-shift expected:")
for r_ in SB.itertuples():
    L.append(f"    {r_.boundary:<8} n={r_.n:<5} F1 {r_.F1_ratio:.2f} (p+={r_.F1_p_enrich:.3f}, p-={r_.F1_p_deplete:.3f})  MIX {r_.MIX_ratio:.2f}  F2 {r_.F2_ratio:.2f} (p+={r_.F2_p_enrich:.3f}, p-={r_.F2_p_deplete:.3f})")
# transitions between state runs
runs = []
for mid, s in S.groupby("mid"):
    st = s.state.to_numpy(); cut = np.flatnonzero(st[1:] != st[:-1]) + 1; starts = np.concatenate(([0], cut)); lens = np.diff(np.concatenate((starts, [st.size])))
    seq = st[starts]; runs += [dict(mid=mid, state=a, nxt=c, dwell_s=5 * l) for a, c, l in zip(seq[:-1], seq[1:], lens[:-1])]
RU = pd.DataFrame(runs)
L.append("  run transitions P(next | current): " + pd.crosstab(RU.state, RU.nxt, normalize="index").round(3).to_string().replace("\n", " | "))
L.append("  median dwell (s): " + RU.groupby("state").dwell_s.median().to_dict().__str__())

# ===================== T3
L.append("\nT3. TWO ORIGINS OF TOPICS")
L.append("  share: " + B3.cls.value_counts(normalize=True).round(3).to_dict().__str__())
g = B3.groupby(["mid", "cls"])[["dur_min", "events_per_min", "n_spk", "entropy", "nov_first60", "fac_opener"]].mean().unstack()
for v in ["dur_min", "events_per_min", "n_spk", "entropy", "nov_first60", "fac_opener"]:
    m = B3.groupby("cls")[v].mean()
    L.append(f"  {v:<15} individual {m.get('individual', np.nan):.3f}  collective {m.get('collective', np.nan):.3f}  both {m.get('both', np.nan):.3f}  neither {m.get('neither', np.nan):.3f} | ind vs coll within meeting p={wp(g[v]['individual']-g[v]['collective'])[0]:.3f} (n={wp(g[v]['individual']-g[v]['collective'])[1]})")
L.append("  class by stage: " + pd.crosstab(np.where(B3.stage == 'ids', 'IDS', np.where(B3.stage.isin(list(CM.REVIEW)), 'review', 'other')), B3.cls, normalize="index").round(3).to_string().replace("\n", " | "))

# ===================== T4
L.append("\nT4. CENTRALIZATION AND THE TWO CLOCKS (5-min blocks)")
B4 = B4.sort_values(["mid", "s0"]); B4["cz"] = B4.groupby("mid").central.transform(lambda x: (x - x.mean()) / x.std())
B4["tz"] = B4.groupby("mid").top_share.transform(lambda x: (x - x.mean()) / x.std())
for c in ["collective", "individual"]: B4[c + "_next"] = B4.groupby("mid")[c].shift(-1)
B4["ids"] = (B4.stage == "ids").astype(int); D4 = B4.dropna(subset=["cz", "tz", "collective_next"])
for c in ["collective", "individual"]:
    r0 = smf.glm(f"{c} ~ cz + ids + mid", data=D4, family=sm.families.Poisson()).fit()
    r1 = smf.glm(f"{c}_next ~ cz + {c} + ids + mid", data=D4, family=sm.families.Poisson()).fit()
    r2 = smf.glm(f"{c}_next ~ tz + {c} + ids + mid", data=D4, family=sm.families.Poisson()).fit()
    L.append(f"  {c:<10} same block: centralization RR={np.exp(r0.params['cz']):.3f} p={r0.pvalues['cz']:.3f} | next block: centralization RR={np.exp(r1.params['cz']):.3f} p={r1.pvalues['cz']:.3f}; top share RR={np.exp(r2.params['tz']):.3f} p={r2.pvalues['tz']:.3f}")
L.append(f"  blocks: {len(D4)}; mean collective {D4.collective.mean():.2f}, individual {D4.individual.mean():.2f} per 5 min")

# ===================== T5
L.append("\nT5. THE TWO CLOCKS BY STAGE (+/-30 s, 500 circular shifts)")
pairs = [("topic", "event"), ("event", "topic"), ("event", "floor"), ("topic", "floor"), ("level", "floor"), ("novelty", "floor"), ("novelty", "level")]
rows = []
for grp, test in [("review", lambda s: np.isin(s, list(CM.REVIEW))), ("IDS", lambda s: s == "ids")]:
    for a, c in pairs:
        obs = 0; n = 0; nul = np.zeros(500)
        for mid in CM.meetings():
            ra = np.array(BND[mid][a]); tb = np.array(BND[mid][c]); Tm = BND[mid]["T"]
            if ra.size == 0 or tb.size == 0: continue
            ra = ra[test(CM.stage_of_seconds(mid, ra))]
            if ra.size == 0: continue
            n += ra.size; obs += int(np.sum(near(ra, tb) <= 30))
            for s_ in range(500): nul[s_] += np.sum(near(ra, (tb + rng.uniform(0, Tm)) % Tm) <= 30)
        rows.append(dict(stage=grp, ref=a, target=c, n=n, ratio=obs / nul.mean(), p_enrich=(np.sum(nul >= obs) + 1) / 501, p_deplete=(np.sum(nul <= obs) + 1) / 501))
P5 = pd.DataFrame(rows); P5.to_csv(f"{CM.RES}/floor_cycle_T5_bystage.csv", index=False)
L.append(P5.pivot_table(index=["ref", "target"], columns="stage", values="ratio").round(2).to_string())
L.append("  p enrichment / depletion:"); L.append(P5.round(3).to_string(index=False))
open(f"{CM.RES}/floor_cycle_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
