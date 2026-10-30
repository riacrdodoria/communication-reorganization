"""Triangulating topic change. Are topic boundaries semantic, and is 'topic boundaries fall in the collaborative floor'
a property of conversation or of the segmentation method?
Segmentations (all time-based: blocks of 60 s before and after every 5-s point; TextTiling depth scores, Hearst 1997;
boundaries = depth peaks above mean + 0.5 SD, >= 60 s apart; the number of boundaries is free):
  EMB   sentence-embedding cohesion (paraphrase-multilingual-MiniLM-L12-v2, word-weighted block means, cosine)
  NETC  semantic-network communities: lemma co-occurrence network of the meeting (same or adjacent utterance, weight
        >= 2), Louvain communities (Blondel et al., 2008); block = distribution over communities; similarity = 1 - JS
  NETG  semantic-network change: weighted Jaccard between the lemma co-occurrence networks (nodes + within-utterance
        edges) of the block before and the block after
  TILE  the original utterance-count TextTiling boundaries (gen_fine_episodes.py; TF-IDF, no lemmas or stopwords)
  AGENDA Pulso / L10 stage onsets (annotation, not lexical)
Control (text-shuffle null): utterance texts permuted within each meeting inside word-count quintiles, keeping every
onset, speaker and length; all lexical segmentations recomputed (20 shuffles). A segmentation property that survives
the text shuffle is produced by turn-taking, not by meaning.
Independent validation cues (Passonneau & Litman, 1997; Swerts, 1997): utterances opening with a Portuguese
topic-transition marker; pauses before an utterance in the meeting's top quartile.
Tests: (1) count and agreement among segmentations; (2) cue enrichment within +/-15 s (vs 200 circular shifts);
(3) floor state (F1/F2 from floor_cycle.py) at boundaries, observed vs circular and vs text shuffle; (4) relation to
reorganization events and extended floor turns (+/-30 s), observed vs text shuffle; (5) continuous semantic shift at
events and agenda boundaries and by floor state.
Output: results/topic_tri_*.csv, results/topic_tri_summary.txt"""
import sys, os, re, json, numpy as np, pandas as pd, networkx as nx
from collections import Counter
from scipy import sparse
from scipy.spatial.distance import jensenshannon
from scipy.stats import wilcoxon
from sklearn.feature_extraction.text import TfidfVectorizer
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
rng = np.random.default_rng(111); CACHE = f"{CM.L}/data/semantic_cache"; NSHUF = 20; NCIRC = 200; STEP = 5; BLK = 60
BND = json.load(open(f"{CM.RES}/partitions_bounds.json")); ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv")

def near(a, b): a = np.asarray(a); b = np.asarray(b); return np.min(np.abs(a[:, None] - b[None, :]), 1) if a.size and b.size else np.full(a.size, 1e9)
def wp(x): x = np.asarray(x, float); x = x[~np.isnan(x)]; return wilcoxon(x).pvalue if len(x) > 5 and np.any(x != 0) else np.nan

# ---------- original TILE segmenter (copied from gen_fine_episodes.py, applied to any text order)
WORD = re.compile(r"[a-zà-ÿ]+")
def tile(texts, TL=18, K=10, minspace=9):
    n = len(texts)
    if n < 2 * K + 2: return [0]
    X = TfidfVectorizer(token_pattern=r"[a-zà-ÿ]+", min_df=1).fit_transform(texts).toarray()
    nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1; Xn = X / nrm
    s = np.array([(Xn[max(0, i - K + 1):i + 1].mean(0) @ Xn[i + 1:i + 1 + K].mean(0)) / ((np.linalg.norm(Xn[max(0, i - K + 1):i + 1].mean(0)) + 1e-9) * (np.linalg.norm(Xn[i + 1:i + 1 + K].mean(0)) + 1e-9)) for i in range(n - 1)])
    s = pd.Series(s).rolling(3, center=True, min_periods=1).mean().to_numpy()
    depth = np.array([(max(s[max(0, i - K):i + 1]) - s[i]) + (max(s[i:min(n - 1, i + K + 1)]) - s[i]) for i in range(n - 1)])
    nb = max(2, round(n / TL)) - 1; cand = sorted([i for i in range(1, n - 2) if depth[i] >= depth[i - 1] and depth[i] >= depth[i + 1] and depth[i] > 0], key=lambda i: -depth[i]); ch = []
    for i in cand:
        st = i + 1
        if all(abs(st - c) >= minspace for c in ch) and st >= minspace and n - st >= minspace: ch.append(st)
        if len(ch) >= nb: break
    return sorted(ch)

# ---------- time-based cohesion curves
def block_sums(M, on, grid):
    """M: (n_utt, d) dense or CSR, rows in onset order. Returns left and right block sums at each grid point."""
    a = np.searchsorted(on, grid - BLK, "left"); m = np.searchsorted(on, grid, "left"); b = np.searchsorted(on, grid + BLK, "left")
    if sparse.issparse(M):
        cs = sparse.vstack([sparse.csr_matrix((1, M.shape[1])), M]).tocsc()
        cum = None
        Ls = [np.asarray(M[x:y].sum(0)).ravel() for x, y in zip(a, m)]; Rs = [np.asarray(M[x:y].sum(0)).ravel() for x, y in zip(m, b)]
        return np.array(Ls), np.array(Rs)
    cs = np.vstack([np.zeros((1, M.shape[1])), np.cumsum(M, 0)])
    return cs[m] - cs[a], cs[b] - cs[m]
def sim_cos(Lb, Rb):
    nl = np.linalg.norm(Lb, axis=1); nr = np.linalg.norm(Rb, axis=1); ok = (nl > 0) & (nr > 0)
    out = np.full(len(Lb), np.nan); out[ok] = (Lb[ok] * Rb[ok]).sum(1) / (nl[ok] * nr[ok]); return out
def sim_js(Lb, Rb):
    out = np.full(len(Lb), np.nan)
    for i in range(len(Lb)):
        if Lb[i].sum() > 0 and Rb[i].sum() > 0: out[i] = 1 - jensenshannon(Lb[i] / Lb[i].sum(), Rb[i] / Rb[i].sum(), base=2)
    return out
def sim_wjac(Lb, Rb):
    mx = np.maximum(Lb, Rb).sum(1); out = np.full(len(Lb), np.nan); ok = mx > 0; out[ok] = np.minimum(Lb, Rb).sum(1)[ok] / mx[ok]; return out
def boundaries(grid, s, K=12, sep=60):
    s = pd.Series(s).interpolate(limit_direction="both").rolling(3, center=True, min_periods=1).mean().to_numpy(); n = s.size
    depth = np.array([(np.max(s[max(0, i - K):i + 1]) - s[i]) + (np.max(s[i:min(n, i + K + 1)]) - s[i]) for i in range(n)])
    thr = depth.mean() + .5 * depth.std(); cand = [i for i in range(1, n - 1) if depth[i] >= depth[i - 1] and depth[i] >= depth[i + 1] and depth[i] > thr]
    cand.sort(key=lambda i: -depth[i]); kept = []
    for i in cand:
        if all(abs(grid[i] - grid[j]) >= sep for j in kept): kept.append(i)
    return np.sort(grid[kept])

def curves(E, w, U, F, on, grid):
    Le, Re = block_sums(E * w[:, None], on, grid); Lu, Ru = block_sums(U, on, grid); Lf, Rf = block_sums(F, on, grid)
    return dict(EMB=sim_cos(Le, Re), NETC=sim_js(Lu, Ru), NETG=sim_wjac(Lf, Rf))

SEGS = ["EMB", "NETC", "NETG", "TILE"]; RES = {}; SHUF = {s: {} for s in SEGS}; CUR = {}; INFO = []
for mid in CM.meetings():
    z = np.load(f"{CACHE}/{mid}.npz", allow_pickle=True); lem = json.load(open(f"{CACHE}/{mid}_lemmas.json"))
    on = z["onset"]; E = z["emb"].astype(float); nw = z["nw"]; w = np.maximum(nw, 1).astype(float); T = BND[mid]["T"]
    texts = pd.read_csv(f"{CM.TXT}/{mid}_transcript.csv"); texts = texts.assign(o=pd.to_numeric(texts.onset_seconds, errors="coerce")).dropna(subset=["o", "speaker_id"])
    texts = texts[texts.text.notna()].text.astype(str).tolist(); toks = [" ".join(WORD.findall(t.lower())) for t in texts]
    # semantic network of the meeting
    freq = Counter(l for u in lem for l in u); vocab = {l for l, c in freq.items() if c >= 2}
    G = nx.Graph()
    for i in range(len(lem)):
        bag = set(l for l in lem[i] if l in vocab) | (set(l for l in lem[i + 1] if l in vocab) if i + 1 < len(lem) else set())
        for a_ in bag:
            for b_ in bag:
                if a_ < b_: G.add_edge(a_, b_, weight=G[a_][b_]["weight"] + 1 if G.has_edge(a_, b_) else 1)
    G.remove_edges_from([(a_, b_) for a_, b_, d in G.edges(data=True) if d["weight"] < 2]); G.remove_nodes_from(list(nx.isolates(G)))
    comms = nx.community.louvain_communities(G, weight="weight", seed=1) if G.number_of_edges() else []
    cmap = {l: k for k, c in enumerate(comms) for l in c}; nC = max(1, len(comms))
    U = np.zeros((len(lem), nC))
    for i, u in enumerate(lem):
        for l in u:
            if l in cmap: U[i, cmap[l]] += 1
    feat = {}; rows, cols, vals = [], [], []
    for i, u in enumerate(lem):
        us = sorted(set(l for l in u if l in vocab)); items = us + [a_ + "|" + b_ for x, a_ in enumerate(us) for b_ in us[x + 1:]]
        for it in items:
            j = feat.setdefault(it, len(feat)); rows.append(i); cols.append(j); vals.append(1.0)
    F = sparse.csr_matrix((vals, (rows, cols)), shape=(len(lem), max(1, len(feat))))
    grid = np.arange(BLK, T - BLK, STEP, dtype=float)
    cv = curves(E, w, U, F, on, grid); CUR[mid] = (grid, cv)
    RES[mid] = {k: boundaries(grid, v) for k, v in cv.items()}; RES[mid]["TILE"] = np.array(BND[mid]["topic"]); RES[mid]["AGENDA"] = np.array(BND[mid]["agenda"])
    INFO.append(dict(mid=mid, n_comm=len(comms), modularity=nx.community.modularity(G, comms, weight="weight") if comms else np.nan, n_nodes=G.number_of_nodes()))
    # text-shuffle null
    q = pd.qcut(nw, 5, labels=False, duplicates="drop")
    for s_ in range(NSHUF):
        p = np.arange(len(nw))
        for b_ in np.unique(q):
            idx = np.flatnonzero(q == b_); p[idx] = rng.permutation(idx)
        cvs = curves(E[p], w[p], U[p], F[p], on, grid)
        for k in ["EMB", "NETC", "NETG"]: SHUF[k].setdefault(mid, []).append(boundaries(grid, cvs[k]))
        tb = tile([toks[i] for i in p]); SHUF["TILE"].setdefault(mid, []).append(on[np.array(tb, int)] if len(tb) else np.array([]))
    print(mid, {k: len(v) for k, v in RES[mid].items()}, "communities", len(comms), flush=True)

pd.DataFrame(INFO).to_csv(f"{CM.RES}/topic_tri_networks.csv", index=False)
MIDS = CM.meetings(); ALL = SEGS + ["AGENDA"]; L = []
Thr = {m: BND[m]["T"] / 3600 for m in MIDS}
L.append("1. SEGMENTATIONS: boundaries per hour (observed | text-shuffle mean)")
for k in ALL:
    o = np.mean([len(RES[m][k]) / Thr[m] for m in MIDS]); s_ = np.mean([np.mean([len(x) for x in SHUF[k][m]]) / Thr[m] for m in MIDS]) if k in SHUF else np.nan
    L.append(f"  {k:<7} {o:5.1f} | {s_:5.1f}")
INF = pd.DataFrame(INFO); L.append(f"  semantic networks: {INF.n_nodes.mean():.0f} lemmas, {INF.n_comm.mean():.1f} communities, modularity {INF.modularity.mean():.2f} (mean per meeting)")

def enrich(refs, targets, W=30, n=NCIRC):
    """pooled share of ref boundaries with a target within W, observed / circular expectation (targets shifted)"""
    obs = sum(int(np.sum(near(refs[m], targets[m]) <= W)) for m in MIDS); tot = sum(len(refs[m]) for m in MIDS)
    nul = np.array([sum(int(np.sum(near(refs[m], (np.asarray(targets[m]) + rng.uniform(0, BND[m]['T'])) % BND[m]['T']) <= W)) for m in MIDS if len(targets[m])) for _ in range(n)])
    return obs / nul.mean() if nul.mean() else np.nan, (np.sum(nul >= obs) + 1) / (n + 1), (np.sum(nul <= obs) + 1) / (n + 1), tot

# 2. agreement
L.append("\n2. AGREEMENT between segmentations (+/-30 s, observed / circular expectation; * p < .01)")
M = pd.DataFrame(index=ALL, columns=ALL, dtype=object)
for a in ALL:
    for b in ALL:
        if a != b:
            r, pe, _, _ = enrich({m: RES[m][a] for m in MIDS}, {m: RES[m][b] for m in MIDS}); M.loc[a, b] = f"{r:.2f}{'*' if pe < .01 else ''}"
L.append(M.fillna("—").to_string())

# 3. cues
cues = {}; pauses = {}
for m in MIDS:
    z = np.load(f"{CACHE}/{m}.npz", allow_pickle=True); on = z["onset"]; nw = z["nw"]
    end_prev = np.concatenate(([-np.inf], np.minimum(on[:-1] + .5 * nw[:-1], on[1:]))); gap = np.clip(on - end_prev, 0, None); gap[0] = 0
    cues[m] = on[z["cue"]]; pauses[m] = on[gap >= np.percentile(gap[1:], 75)]
L.append("\n3. INDEPENDENT CUES within +/-15 s of boundaries (observed / circular; p enrichment)")
rows = []
for k in ALL:
    r1, p1, _, n = enrich({m: RES[m][k] for m in MIDS}, cues, W=15); r2, p2, _, _ = enrich({m: RES[m][k] for m in MIDS}, pauses, W=15)
    rs = [enrich({m: SHUF[k][m][i] for m in MIDS}, cues, W=15, n=30)[0] for i in range(5)] if k in SHUF else [np.nan]
    rows.append(dict(seg=k, n=n, cue_ratio=r1, cue_p=p1, pause_ratio=r2, pause_p=p2, cue_ratio_textshuffle=np.nanmean(rs)))
    L.append(f"  {k:<7} n={n:<5} topic-transition marker {r1:.2f} (p={p1:.3f}) [text-shuffle {np.nanmean(rs):.2f}] | long pause {r2:.2f} (p={p2:.3f})")
pd.DataFrame(rows).to_csv(f"{CM.RES}/topic_tri_cues.csv", index=False)

# 4. floor state at boundaries: observed vs circular and vs text-shuffle
def state_ratio(bset, n=100):
    obs = Counter(); exp = Counter()
    for m in MIDS:
        s = ST[ST.mid == m]; secs = s.sec.to_numpy(); stt = s.state.to_numpy(); bb = np.asarray(bset[m])
        if bb.size == 0: continue
        obs.update(stt[np.abs(secs[None, :] - bb[:, None]).argmin(1)])
        for _ in range(n):
            sh = (bb + rng.uniform(0, BND[m]["T"])) % BND[m]["T"]; exp.update(stt[np.abs(secs[None, :] - sh[:, None]).argmin(1)])
    return {k: obs[k] / (exp[k] / n) if exp[k] else np.nan for k in ("F1", "MIX", "F2")}
L.append("\n4. FLOOR STATE AT BOUNDARIES (observed / circular expectation); text-shuffle segmentations give the method's own share")
rows = []
for k in ALL:
    o = state_ratio({m: RES[m][k] for m in MIDS}, n=60)
    if k in SHUF:
        sh = [state_ratio({m: SHUF[k][m][i] for m in MIDS}, n=20) for i in range(NSHUF)]
        f2 = np.array([x["F2"] for x in sh]); f1 = np.array([x["F1"] for x in sh])
        rows.append(dict(seg=k, F1=o["F1"], F2=o["F2"], F1_shuf=f1.mean(), F2_shuf=f2.mean(), F2_shuf_lo=np.percentile(f2, 2.5), F2_shuf_hi=np.percentile(f2, 97.5),
                         p_F2_beyond_shuffle=(np.sum(f2 >= o["F2"]) + 1) / (NSHUF + 1)))
        L.append(f"  {k:<7} F2 {o['F2']:.2f} vs text-shuffle {f2.mean():.2f} [{np.percentile(f2,2.5):.2f}, {np.percentile(f2,97.5):.2f}] (p={(np.sum(f2>=o['F2'])+1)/(NSHUF+1):.3f}) | F1 {o['F1']:.2f} vs {f1.mean():.2f}")
    else:
        rows.append(dict(seg=k, F1=o["F1"], F2=o["F2"])); L.append(f"  {k:<7} F2 {o['F2']:.2f} | F1 {o['F1']:.2f} (not lexical: no text-shuffle)")
pd.DataFrame(rows).to_csv(f"{CM.RES}/topic_tri_floorstate.csv", index=False)

# 5. relation to events and extended floor turns, observed vs text shuffle
L.append("\n5. RELATION TO REORGANIZATION EVENTS AND EXTENDED FLOOR TURNS (+/-30 s; observed vs text-shuffle)")
ev = {m: np.array(BND[m]["event"]) for m in MIDS}; fl = {m: np.array(BND[m]["floor"]) for m in MIDS}; rows = []
for k in ALL:
    re_, pe_, _, _ = enrich({m: RES[m][k] for m in MIDS}, ev); rf, _, pdf, _ = enrich({m: RES[m][k] for m in MIDS}, fl)
    if k in SHUF:
        se = [enrich({m: SHUF[k][m][i] for m in MIDS}, ev, n=30)[0] for i in range(8)]; sf = [enrich({m: SHUF[k][m][i] for m in MIDS}, fl, n=30)[0] for i in range(8)]
    else: se = sf = [np.nan]
    rows.append(dict(seg=k, event=re_, event_p=pe_, event_shuf=np.nanmean(se), floor=rf, floor_p_deplete=pdf, floor_shuf=np.nanmean(sf)))
    L.append(f"  {k:<7} -> event {re_:.2f} (p={pe_:.3f}) [text-shuffle {np.nanmean(se):.2f}] | -> extended floor turn {rf:.2f} (p depletion {pdf:.3f}) [text-shuffle {np.nanmean(sf):.2f}]")
pd.DataFrame(rows).to_csv(f"{CM.RES}/topic_tri_relations.csv", index=False)

# 6. continuous semantic shift
L.append("\n6. CONTINUOUS SEMANTIC SHIFT (1 - similarity of the minute before vs after), standardized within meeting")
rows = []
for m in MIDS:
    grid, cv = CUR[m]; st = ST[ST.mid == m].set_index("sec").state
    stg = st.reindex(grid, method="nearest").to_numpy()
    de = near(grid, BND[m]["event"]); da = near(grid, BND[m]["agenda"]) if len(BND[m]["agenda"]) else np.full(grid.size, 1e9)
    r = dict(mid=m)
    for k, v in cv.items():
        x = 1 - v; zx = (x - np.nanmean(x)) / np.nanstd(x)
        r[f"{k}_event"] = np.nanmean(zx[de <= 15]) - np.nanmean(zx[de >= 90]); r[f"{k}_agenda"] = np.nanmean(zx[da <= 30]) - np.nanmean(zx[da >= 120])
        for s_ in ("F1", "MIX", "F2"): r[f"{k}_{s_}"] = np.nanmean(zx[stg == s_])
    rows.append(r)
S6 = pd.DataFrame(rows); S6.to_csv(f"{CM.RES}/topic_tri_shift.csv", index=False)
for k in ["EMB", "NETC", "NETG"]:
    L.append(f"  {k:<5} at events d={S6[k+'_event'].mean():+.3f} (p={wp(S6[k+'_event']):.1e}) | at agenda boundaries d={S6[k+'_agenda'].mean():+.3f} (p={wp(S6[k+'_agenda']):.1e}) | by state F1 {S6[k+'_F1'].mean():+.3f} MIX {S6[k+'_MIX'].mean():+.3f} F2 {S6[k+'_F2'].mean():+.3f} (F2-F1 p={wp(S6[k+'_F2']-S6[k+'_F1']):.1e})")
json.dump({m: {k: np.asarray(v).tolist() for k, v in RES[m].items()} for m in MIDS}, open(f"{CM.RES}/topic_tri_bounds.json", "w"))
open(f"{CM.RES}/topic_tri_summary.txt", "w").write("\n".join(L)); print("\n".join(L))
