"""Item 7. Label-free content dynamics (no human or LLM coding). Transcripts are read locally; outputs are numeric only.
Per meeting, a TF-IDF space is fit on utterances (lowercase, accents kept, Portuguese stopwords removed, tokens >= 3 chars).
(a) Lexical novelty: every 5 s, 1 - cosine(words in [t-30, t+30), words in [t-330, t-30)). Residualized within meeting on
    log word counts of both windows and on the number of distinct speakers in the current window (turn-length control).
(b) Topic entropy: KMeans (k = 12) on utterance vectors; Shannon entropy of topic labels in the 60-s window (normalized).
(c) Cross-speaker uptake: cosine between consecutive turns of different speakers, relative to a null that pairs each
    turn with a random turn of the same meeting at least 5 min away (ratio > 1 = local uptake).
    Self-continuation: cosine between a speaker's turn and that speaker's previous turn, same null.
Anchors: RMSE event onsets (+/-15 s vs >= 90 s) and topic-episode boundaries (+/-15 s vs >= 60 s); standardized
within-meeting differences, Wilcoxon across meetings. Lead-lag: mean residual novelty at offsets -60..+60 s from events.
Weeks: Kendall tau of uptake ratio and mean novelty within team.
Output: results/content_windows.csv, content_meeting.csv, content_leadlag.csv, content_summary.txt"""
import sys, os, re, numpy as np, pandas as pd
from scipy.stats import kendalltau
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
sys.path.insert(0, os.path.dirname(__file__)); import common as C
rng = np.random.default_rng(61)
SW = set(w.strip().lower() for w in open(f"{C.L}/data/stopwords-pt.txt", encoding="utf-8") if w.strip())
tok = lambda s: [w for w in re.findall(r"[a-záàâãéêíóôõúüç]+", str(s).lower()) if len(w) >= 3 and w not in SW]

def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b); return float(a @ b / (na * nb)) if na > 0 and nb > 0 else np.nan

E = C.events(); Wk = C.week_map(); win_rows = []; meet_rows = []; ll_rows = []
for mid in C.meetings():
    tx = C.transcript(mid); tx = tx[tx.text.notna()].reset_index(drop=True)
    vec = TfidfVectorizer(tokenizer=tok, lowercase=False, token_pattern=None, min_df=2, sublinear_tf=True)
    X = vec.fit_transform(tx.text.astype(str)).toarray(); on = tx.onset_seconds.to_numpy(); sp = tx.speaker_id.astype(str).to_numpy()
    nw = np.array([len(tok(t)) for t in tx.text]); cs = np.vstack([np.zeros(X.shape[1]), np.cumsum(X, 0)]); cw = np.concatenate(([0], np.cumsum(nw)))
    k = min(12, max(2, (X.sum(1) > 0).sum() // 20)); lab = np.full(len(tx), -1); ok = X.sum(1) > 0
    lab[ok] = KMeans(n_clusters=k, n_init=5, random_state=0).fit_predict(X[ok] / np.linalg.norm(X[ok], axis=1, keepdims=True))
    ev = E[E.mid == mid].event_onset_s.to_numpy(); bd = C.episode_bounds(mid); T = on.max()
    idx = lambda a, b: (np.searchsorted(on, a, "left"), np.searchsorted(on, b, "left"))
    rows = []
    for t in np.arange(330, T - 30, 5.0):
        i0, i1 = idx(t - 30, t + 30); j0, j1 = idx(t - 330, t - 30)
        cur = cs[i1] - cs[i0]; prev = cs[j1] - cs[j0]; nov = 1 - cos(cur, prev) if cur.any() and prev.any() else np.nan
        l = lab[i0:i1]; l = l[l >= 0]; te = (lambda p: -(p * np.log(p)).sum() / np.log(k))(np.bincount(l, minlength=k)[np.bincount(l, minlength=k) > 0] / l.size) if l.size else np.nan
        rows.append(dict(mid=mid, sec=t, novelty=nov, topic_entropy=te, w_cur=cw[i1] - cw[i0], w_prev=cw[j1] - cw[j0], n_spk=len(set(sp[i0:i1])),
                         d_ev=np.min(np.abs(ev - t)) if ev.size else 1e9, d_ev_signed=(t - ev[np.argmin(np.abs(ev - t))]) if ev.size else np.nan, d_bd=np.min(np.abs(bd - t)) if bd.size else 1e9))
    W = pd.DataFrame(rows).dropna(subset=["novelty"])
    Z = np.column_stack([np.ones(len(W)), np.log1p(W.w_cur), np.log1p(W.w_prev), W.n_spk])
    for m in ["novelty", "topic_entropy"]:
        y = W[m].to_numpy(); okm = ~np.isnan(y); beta = np.linalg.lstsq(Z[okm], y[okm], rcond=None)[0]; W[m + "_res"] = y - Z @ beta
    win_rows.append(W)
    # (c) uptake on turns
    keep = np.concatenate(([True], sp[1:] != sp[:-1])); starts = np.flatnonzero(keep); ends = np.concatenate((starts[1:], [len(sp)]))
    TV = np.array([X[a:b].sum(0) for a, b in zip(starts, ends)]); ts = on[starts]; tsp = sp[starts]
    def null_cos(i):
        far = np.flatnonzero(np.abs(ts - ts[i]) >= 300); return cos(TV[i], TV[rng.choice(far)]) if far.size else np.nan
    up, upn, sc, scn, up_near, up_base = [], [], [], [], [], []
    for i in range(1, len(TV)):
        c = cos(TV[i], TV[i - 1]); n = null_cos(i); up.append(c); upn.append(n)
        dn = np.min(np.abs(ev - ts[i])) if ev.size else 1e9
        if dn <= 30: up_near.append(c)
        elif dn >= 90: up_base.append(c)
        prev_same = np.flatnonzero(tsp[:i] == tsp[i])
        if prev_same.size: sc.append(cos(TV[i], TV[prev_same[-1]])); scn.append(null_cos(i))
    meet_rows.append(dict(mid=mid, team=C.team(mid), week=Wk[mid], uptake=np.nanmean(up), uptake_null=np.nanmean(upn), uptake_ratio=np.nanmean(up) / np.nanmean(upn),
                          selfcont=np.nanmean(sc), selfcont_null=np.nanmean(scn), uptake_near=np.nanmean(up_near), uptake_base=np.nanmean(up_base), mean_novelty=W.novelty.mean(), k=k))
    for off in range(-60, 65, 10):
        sel = W[np.abs(W.d_ev_signed - off) <= 5]; ll_rows.append(dict(mid=mid, offset=off, nov_res=sel.novelty_res.mean() / W.novelty_res.std(), te_res=sel.topic_entropy_res.mean() / W.topic_entropy_res.std()))
    r = meet_rows[-1]; print(mid, f"uptake {r['uptake']:.3f}/{r['uptake_null']:.3f} self {r['selfcont']:.3f}/{r['selfcont_null']:.3f} near {r['uptake_near']:.3f} base {r['uptake_base']:.3f}", flush=True)

W = pd.concat(win_rows, ignore_index=True); M = pd.DataFrame(meet_rows); LL = pd.DataFrame(ll_rows)
W.to_csv(f"{C.RES}/content_windows.csv", index=False); M.to_csv(f"{C.RES}/content_meeting.csv", index=False); LL.to_csv(f"{C.RES}/content_leadlag.csv", index=False)
L = []
for m in ["novelty", "novelty_res", "topic_entropy", "topic_entropy_res"]:
    for name, col, far in [("event", "d_ev", 90), ("boundary", "d_bd", 60)]:
        d = []
        for mid, g in W.groupby("mid"):
            ga, gb = g[g[col] <= 15][m], g[g[col] >= far][m]
            if len(ga) > 2 and len(gb) > 2 and g[m].std() > 0: d.append((ga.mean() - gb.mean()) / g[m].std())
        p, n = C.wilcoxon_p(d); L.append(f"{m:<18} {name:<8} d={np.mean(d):+.3f}  positive {int(np.sum(np.array(d)>0))}/{n}  Wilcoxon p={p:.1e}")
L.append("")
L.append(f"Cross-speaker uptake: {M.uptake.mean():.3f} vs far-turn null {M.uptake_null.mean():.3f} (ratio {M.uptake_ratio.mean():.2f}; Wilcoxon p={C.wilcoxon_p(M.uptake-M.uptake_null)[0]:.1e})")
L.append(f"Self-continuation: {M.selfcont.mean():.3f} vs null {M.selfcont_null.mean():.3f} (Wilcoxon p={C.wilcoxon_p(M.selfcont-M.selfcont_null)[0]:.1e}); self minus cross {np.mean(M.selfcont-M.uptake):+.3f} (p={C.wilcoxon_p(M.selfcont-M.uptake)[0]:.1e})")
L.append(f"Uptake near events (+/-30 s) {M.uptake_near.mean():.3f} vs baseline (>=90 s) {M.uptake_base.mean():.3f} (Wilcoxon p={C.wilcoxon_p(M.uptake_near-M.uptake_base)[0]:.1e})")
for t in "AB":
    g = M[M.team == t]
    for m in ["uptake_ratio", "selfcont", "mean_novelty"]:
        tau, p = kendalltau(g.week, g[m]); L.append(f"Team {t} {m} vs week: tau={tau:+.2f} p={p:.3f}")
L.append("\nLead-lag (event onset at 0; standardized residual novelty / topic entropy):")
L.append(LL.groupby("offset")[["nov_res", "te_res"]].mean().round(3).T.to_string())
open(f"{C.RES}/content_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
