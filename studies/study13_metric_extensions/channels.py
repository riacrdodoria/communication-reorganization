"""One table with every channel on a 5-s grid per meeting (windows centred on each grid point).
Turn-taking (60 s): entropy, %DET, top-speaker share, active speakers, speaker switches per min, floor state.
Content (from content_windows / embeddings): residual lexical novelty, residual topic mixing, return to an earlier
subject (>= 10 min before), embedding semantic shift (minute before vs after).
Language (120 s, more text per window): sentiment (mean P(POS) - P(NEG) over utterances, pysentimiento pt),
language style matching across the speakers present (Ireland & Pennebaker 2010: 1 - |p_i - p_j| / (p_i + p_j) per
function-word class, averaged over classes and speaker pairs with >= 20 tokens each), lexical richness (lemma
type-token ratio residualized on token count), collective 'a gente / nós' and '?' per 100 words.
Output: results/channels_grid.csv (numeric only)"""
import sys, os, re, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
CACHE = f"{CM.L}/data/semantic_cache"; CW = pd.read_csv(f"{CM.RES}/content_windows.csv"); BW = pd.read_csv(f"{CM.RES}/battery_windows.csv")
ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv"); P = json.load(open(f"{CM.RES}/partitions_bounds.json"))
COL = re.compile(r"\b(a gente|n[oó]s|nosso|nossa|nossos|nossas)\b"); rows = []
for m in CM.meetings():
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); f = np.load(f"{CACHE}/{m}_feat.npz", allow_pickle=True); lem = json.load(open(f"{CACHE}/{m}_lemmas.json"))
    on = z["onset"]; spk = z["speaker"]; nw = np.maximum(z["nw"], 1); E = z["emb"].astype(float)
    lab = list(f["sent_labels"]); sent = f["sent"][:, lab.index("POS")] - f["sent"][:, lab.index("NEG")]; FW = f["fw"][:, :-1].astype(float); ntok = f["fw"][:, -1].astype(float)
    tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); low = tx.text.astype(str).str.lower()
    col = low.str.count(COL.pattern).to_numpy(float); q = low.str.count(r"\?").to_numpy(float)
    T = P[m]["T"]; grid = np.arange(60, T - 60, 5.0)
    # embedding shift and return
    cs = np.vstack([np.zeros((1, E.shape[1])), np.cumsum(E * nw[:, None], 0)])
    def blk(a_, b_): ia, ib = np.searchsorted(on, a_), np.searchsorted(on, b_); V = cs[ib] - cs[ia]; n = np.linalg.norm(V, axis=1, keepdims=True); return np.where(n > 0, V / np.maximum(n, 1e-12), np.nan)
    Lb, Rb, Cb = blk(grid - 60, grid), blk(grid, grid + 60), blk(grid - 30, grid + 30)
    shift = 1 - np.nansum(Lb * Rb, 1); shift[np.isnan(Lb).any(1) | np.isnan(Rb).any(1)] = np.nan
    ret = np.full(grid.size, np.nan); okc = ~np.isnan(Cb).any(1); S_ = np.where(okc[:, None] & okc[None, :], np.nan_to_num(Cb) @ np.nan_to_num(Cb).T, np.nan)
    for i in range(grid.size):
        j = (grid <= grid[i] - 600) & okc
        if okc[i] and j.any(): ret[i] = np.nanmax(S_[i, j])
    for i, t in enumerate(grid):
        a, b = np.searchsorted(on, t - 60), np.searchsorted(on, t + 60); sl = slice(a, b); w = nw[sl].sum()
        r = dict(mid=m, sec=t, sem_shift=shift[i], ret=ret[i], words120=w, n_utt120=b - a)
        r["sentiment"] = np.average(sent[sl], weights=nw[sl]) if b > a else np.nan
        r["collective"] = 100 * col[sl].sum() / max(w, 1); r["question"] = 100 * q[sl].sum() / max(w, 1)
        toks = [l for u in lem[a:b] for l in u]; r["ttr"] = len(set(toks)) / len(toks) if len(toks) >= 20 else np.nan; r["ntok_lem"] = len(toks)
        # LSM across speakers present
        prof = {}
        for s_ in set(spk[sl]):
            k = np.flatnonzero(spk[sl] == s_) + a; n = ntok[k].sum()
            if n >= 20: prof[s_] = FW[k].sum(0) / n
        if len(prof) >= 2:
            ks = list(prof); vals = []
            for x in range(len(ks)):
                for y in range(x + 1, len(ks)):
                    p1, p2 = prof[ks[x]], prof[ks[y]]; vals.append(np.mean(1 - np.abs(p1 - p2) / (p1 + p2 + 1e-4)))
            r["lsm"] = np.mean(vals)
        else: r["lsm"] = np.nan
        rows.append(r)
    print(m, flush=True)
G_ = pd.DataFrame(rows)
G_ = G_.merge(BW[["mid", "sec", "entropy", "det", "top_share", "active", "switch"]], on=["mid", "sec"], how="left")
G_ = G_.merge(CW[["mid", "sec", "novelty_res", "topic_entropy_res"]], on=["mid", "sec"], how="left").merge(ST[["mid", "sec", "state"]], on=["mid", "sec"], how="left")
import statsmodels.formula.api as smf
for c, ctrl in [("ttr", "np.log1p(ntok_lem)"), ("ret", "np.log1p(words120)"), ("lsm", "np.log1p(words120)")]:
    d = G_.dropna(subset=[c]); G_.loc[d.index, c + "_res"] = smf.ols(f"{c} ~ {ctrl} + C(mid)".replace("C(", "Q('mid')*0+C(") if False else f"{c} ~ {ctrl}", data=d).fit().resid
G_.to_csv(f"{CM.RES}/channels_grid.csv", index=False); print(G_.describe().T[["count", "mean", "std"]].round(3))
