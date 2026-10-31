"""Every event-anchored finding against SURROGATE EVENTS (same detection rule applied to run-shuffled team-state series;
20 sets per meeting, surrogate_events.json). A surrogate set has the number and the clustering that the detection
procedure produces, but no relation to what is actually happening in the meeting. For each statistic the observed pooled
value is compared with the 20 pooled surrogate values (z and rank p = (b + 1) / 21; with 20 sets p >= .048).
Statistics: agenda coincidence (+/-30 s); agenda anticipation (agenda onset 15-60 s after the event); LLM topic
coincidence (qualitative side); member questions in the 45 s after onset; the opening turn (duration, question);
initiator (facilitator share, quietest member share; Study 9 primary rule); extended-floor-turn coincidence; and the
event signature of content and language channels (event-triggered mean of within-meeting z at lags -120..+120 s).
Turn-taking channels around real vs surrogate times are definitional and reported only as a reference.
Output: results/evnull_stats.csv, results/evnull_signature.csv, results/evnull_summary.txt"""
import sys, os, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
SUR = json.load(open(f"{CM.RES}/surrogate_events.json")); P = json.load(open(f"{CM.RES}/partitions_bounds.json")); EV = CM.events()
G = pd.read_csv(f"{CM.RES}/channels_grid.csv"); TU = pd.read_csv(f"{CM.RES}/seqdyn_turns.csv")
LLM = json.load(open(f"{CM.RES}/llm_topics_bounds.json")) if os.path.exists(f"{CM.RES}/llm_topics_bounds.json") else {}
MIDS = [m for m in CM.meetings() if m in SUR]; K = min(len(SUR[m]) for m in MIDS)
def near(a, b): a = np.asarray(a, float); b = np.asarray(b, float); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
# quietest member per team (fewest words over the team's meetings)
words = {}
for m in CM.meetings():
    tx = CM.transcript(m); R = CM.roles(m); r = tx.speaker_id.astype(str).map(lambda s: R.get(s, "OTHER")); w = tx.text.astype(str).str.split().str.len()
    for k_, v in w.groupby(r).sum().items(): words[(CM.team(m), k_)] = words.get((CM.team(m), k_), 0) + v
QUIET = {t: min([(v, k_) for (tt, k_), v in words.items() if tt == t and k_ not in ("FACILITATOR", "OTHER")])[1] for t in "AB"}
TUm = {m: TU[TU.mid == m] for m in MIDS}
def initiator(m, t):
    g = TUm[m]; pre = g[(g.t >= t - 15) & (g.t < t)]; dom = pre.groupby("role").dur.sum().idxmax() if len(pre) else None
    win = g[(g.t >= t - 5) & (g.t <= t + 10)]; win = win[win.role != dom] if dom is not None else win
    return win.role.iloc[0] if len(win) else None
def stats_for(evs):
    """evs: {mid: onsets}. Returns dict of pooled statistics."""
    n = sum(len(v) for v in evs.values()); s = dict.fromkeys(["agenda_coinc", "agenda_anticip", "llm_coinc", "member_q45", "open_dur", "open_question", "init_fac", "init_quiet", "floor_coinc"], 0.0)
    cnt_llm = 0; cnt_open = 0; cnt_init = 0
    for m, ev in evs.items():
        ev = np.asarray(ev, float)
        if ev.size == 0: continue
        ag = np.array(P[m]["agenda"]); g = TUm[m]; fl = np.array(P[m]["floor"])
        s["agenda_coinc"] += np.sum(near(ev, ag) <= 30) if ag.size else 0
        s["agenda_anticip"] += sum(np.any(((ag - t) >= 15) & ((ag - t) <= 60)) for t in ev) if ag.size else 0
        if m in LLM: s["llm_coinc"] += np.sum(near(ev, LLM[m]["topic"]) <= 30); cnt_llm += ev.size
        mq = g[g.question & (g.role != "FACILITATOR") & (g.role != "OTHER")].t.to_numpy()
        s["member_q45"] += sum(np.sum((mq > t) & (mq <= t + 45)) for t in ev)
        s["floor_coinc"] += np.sum(near(ev, fl) <= 30) if fl.size else 0
        for t in ev:
            o = g[(g.t >= t - 5) & (g.t <= t + 10)]
            if len(o): s["open_dur"] += o.dur.iloc[0]; s["open_question"] += float(o.question.iloc[0]); cnt_open += 1
            ini = initiator(m, t)
            if ini is not None: s["init_fac"] += ini == "FACILITATOR"; s["init_quiet"] += ini == QUIET[CM.team(m)]; cnt_init += 1
    for k_ in ["agenda_coinc", "agenda_anticip", "member_q45", "floor_coinc"]: s[k_] /= max(n, 1)
    s["llm_coinc"] /= max(cnt_llm, 1); s["open_dur"] /= max(cnt_open, 1); s["open_question"] /= max(cnt_open, 1); s["init_fac"] /= max(cnt_init, 1); s["init_quiet"] /= max(cnt_init, 1)
    return s
obs = stats_for({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in MIDS}); sur = [stats_for({m: SUR[m][k] for m in MIDS}) for k in range(K)]
rows = []
for k_ in obs:
    v = np.array([s[k_] for s in sur]); rows.append(dict(stat=k_, observed=obs[k_], surrogate_mean=v.mean(), surrogate_sd=v.std(), ratio=obs[k_] / v.mean() if v.mean() else np.nan,
                                                     z=(obs[k_] - v.mean()) / v.std() if v.std() > 0 else np.nan, p_high=(np.sum(v >= obs[k_]) + 1) / (K + 1), p_low=(np.sum(v <= obs[k_]) + 1) / (K + 1)))
S = pd.DataFrame(rows); S.to_csv(f"{CM.RES}/evnull_stats.csv", index=False)
# signatures
LAGS = np.arange(-120, 121, 10); CH = ["novelty_res", "topic_entropy_res", "sem_shift", "ret_res", "sentiment", "collective", "question", "lsm_res", "ttr_res", "entropy", "det", "top_share", "switch"]
Z = {}
for m in MIDS:
    g = G[G.mid == m].set_index("sec"); Z[m] = (g[CH] - g[CH].mean()) / g[CH].std()
def signature(evs):
    acc = {c: np.zeros(LAGS.size) for c in CH}; n = {c: np.zeros(LAGS.size) for c in CH}
    for m, ev in evs.items():
        z = Z[m]; idx = z.index.to_numpy()
        for t in np.asarray(ev, float):
            for j, lg in enumerate(LAGS):
                k_ = np.searchsorted(idx, t + lg)
                if 0 <= k_ < idx.size and abs(idx[k_] - (t + lg)) <= 5:
                    row = z.iloc[k_]
                    for c in CH:
                        if not np.isnan(row[c]): acc[c][j] += row[c]; n[c][j] += 1
    return {c: acc[c] / np.maximum(n[c], 1) for c in CH}
so = signature({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in MIDS}); ss = [signature({m: SUR[m][k] for m in MIDS}) for k in range(K)]
rows = []
for c in CH:
    arr = np.array([s[c] for s in ss]); lo, hi = np.percentile(arr, [2.5, 97.5], 0)
    for j, lg in enumerate(LAGS): rows.append(dict(channel=c, lag=lg, observed=so[c][j], surrogate_mean=arr[:, j].mean(), lo=lo[j], hi=hi[j]))
SG = pd.DataFrame(rows); SG["excess"] = SG.observed - SG.surrogate_mean; SG.to_csv(f"{CM.RES}/evnull_signature.csv", index=False)
L = [f"Meetings {len(MIDS)}; surrogate sets per meeting {K}; quietest members {QUIET}", "", "EVENT-ANCHORED STATISTICS: observed vs surrogate events (z; p for observed above / below surrogates)"]
for r in S.itertuples(): L.append(f"  {r.stat:<15} observed {r.observed:.3f} vs surrogate {r.surrogate_mean:.3f} (ratio {r.ratio:.2f}, z {r.z:+.1f}, p_high {r.p_high:.3f}, p_low {r.p_low:.3f})")
L.append("\nEVENT SIGNATURE (within-meeting z; observed minus surrogate; lags with observed outside the surrogate 95 % band marked)")
for c in CH:
    d = SG[SG.channel == c]; mark = " ".join(f"{int(r.lag):+d}:{r.excess:+.2f}{'*' if (r.observed > r.hi or r.observed < r.lo) else ''}" for r in d.itertuples() if r.lag % 30 == 0)
    L.append(f"  {c:<18}{'(definitional) ' if c in ('entropy','det','top_share','switch') else ''}{mark}")
open(f"{CM.RES}/evnull_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
