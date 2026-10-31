"""Data for the emotions-and-decisions figure (numeric only).
(1) Emotion signature around events at lags -120..+120 s (10-s steps): 120-s word-weighted windows of each emotion
    probability, z within meeting; observed event-triggered mean vs 20 surrogate-event sets (mean and 95 % band).
(2) Peri-event histogram of decision utterances (agreement, commitment, deadline) in 15-s bins from -120 to +120 s
    around event onsets, as a rate ratio to the meeting-level expectation, observed vs surrogate events.
Output: results/ped_emo_signature.csv, results/ped_decision_peth.csv"""
import sys, os, re, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
CACHE = f"{CM.L}/data/semantic_cache"; P = json.load(open(f"{CM.RES}/partitions_bounds.json")); SUR = json.load(open(f"{CM.RES}/surrogate_events.json")); EV = CM.events()
DEC = {"agreement": r"\b(fica combinado|t[aá] combinado|combinado ent[aã]o|ent[aã]o fica|fechado ent[aã]o|t[aá] fechado|fechou|ficou decidido|decidimos|vamos fazer assim|vamos seguir|ent[aã]o vamos|bora)\b",
       "commitment": r"\b(eu vou (fazer|mandar|ver|falar|ligar|marcar|preparar|enviar|organizar|montar|levantar|atualizar|conversar)|eu fa[cç]o|eu fico (com|respons[aá]vel)|deixa comigo|pode deixar|fica comigo|eu me comprometo|eu mando|eu vejo isso|eu resolvo)\b",
       "deadline": r"\b(at[eé] (segunda|ter[cç]a|quarta|quinta|sexta|amanh[aã]|semana que vem|a pr[oó]xima)|prazo|respons[aá]vel|pr[oó]ximo passo|to-?do|tarefa)\b"}
EMO = ["approval", "disapproval", "admiration", "optimism", "curiosity", "confusion", "realization"]
LAGS = np.arange(-120, 121, 10); Z = {}; DT = {}
for m in CM.meetings():
    tx = CM.transcript(m); tx = tx[tx.text.notna()].reset_index(drop=True); t = tx.onset_seconds.to_numpy(); low = tx.text.astype(str).str.lower(); w = low.str.split().str.len().clip(lower=1).to_numpy(float)
    e = np.load(f"{CACHE}/{m}_emo.npz", allow_pickle=True); lab = list(e["labels"]); E = e["emo"][:, [lab.index(x) for x in EMO]]
    grid = np.arange(60, P[m]["T"] - 60, 5.0); a = np.searchsorted(t, grid - 60); b = np.searchsorted(t, grid + 60)
    cs = np.vstack([np.zeros((1, len(EMO))), np.cumsum(E * w[:, None], 0)]); cw = np.concatenate(([0], np.cumsum(w)))
    V = (cs[b] - cs[a]) / np.maximum(cw[b] - cw[a], 1)[:, None]; Z[m] = (grid, (V - V.mean(0)) / V.std(0))
    DT[m] = {k: t[low.str.contains(v, regex=True).to_numpy()] for k, v in DEC.items()}
def sig(evsets):
    out = np.zeros((len(EMO), LAGS.size)); n = np.zeros(LAGS.size)
    for m, (grid, z) in Z.items():
        for t0 in np.asarray(evsets[m], float):
            k = np.searchsorted(grid, t0 + LAGS); ok = (k >= 0) & (k < grid.size)
            ok[ok] &= np.abs(grid[k[ok]] - (t0 + LAGS[ok])) <= 5
            out[:, ok] += z[k[ok]].T; n[ok] += 1
    return out / np.maximum(n, 1)
obs = sig({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in Z}); sur = np.array([sig({m: SUR[m][j] for m in Z}) for j in range(20)])
rows = []
for i, c in enumerate(EMO):
    lo, hi = np.percentile(sur[:, i], [2.5, 97.5], 0)
    for j, lg in enumerate(LAGS): rows.append(dict(emotion=c, lag=lg, observed=obs[i, j], sur_mean=sur[:, i, j].mean(), lo=lo[j], hi=hi[j]))
pd.DataFrame(rows).to_csv(f"{CM.RES}/ped_emo_signature.csv", index=False)
BINS = np.arange(-120, 121, 15)
def peth(evsets, k):
    num = np.zeros(BINS.size - 1); den = np.zeros(BINS.size - 1)
    for m in Z:
        d = DT[m][k]; T = P[m]["T"]; rate = d.size / T
        for t0 in np.asarray(evsets[m], float):
            num += np.histogram(d - t0, BINS)[0]; den += rate * 15 * np.array([(t0 + a) >= 0 and (t0 + b) <= T for a, b in zip(BINS[:-1], BINS[1:])])
    return num / np.maximum(den, 1e-9)
rows = []
for k in DEC:
    o = peth({m: EV[EV.mid == m].event_onset_s.to_numpy() for m in Z}, k); s = np.array([peth({m: SUR[m][j] for m in Z}, k) for j in range(20)]); lo, hi = np.percentile(s, [2.5, 97.5], 0)
    for j, a in enumerate(BINS[:-1]): rows.append(dict(kind=k, bin_start=a, observed=o[j], sur_mean=s[:, j].mean(), lo=lo[j], hi=hi[j]))
pd.DataFrame(rows).to_csv(f"{CM.RES}/ped_decision_peth.csv", index=False); print("ok")
# (3) decisions by floor state: share of decision utterances in each state / share of all utterances
ST = pd.read_csv(f"{CM.RES}/floor_cycle_T2_states.csv"); cnt = {k: {"F1": 0, "MIX": 0, "F2": 0} for k in DEC}; allc = {"F1": 0, "MIX": 0, "F2": 0}
for m in Z:
    s = ST[ST.mid == m]; secs = s.sec.to_numpy(); sv = s.state.to_numpy()
    tx = CM.transcript(m); tx = tx[tx.text.notna()]; t_all = tx.onset_seconds.to_numpy()
    for x in sv[np.abs(secs[None, :] - t_all[:, None]).argmin(1)]: allc[x] += 1
    for k in DEC:
        if DT[m][k].size:
            for x in sv[np.abs(secs[None, :] - DT[m][k][:, None]).argmin(1)]: cnt[k][x] += 1
tot = sum(allc.values()); rows = []
for k in DEC:
    n = sum(cnt[k].values())
    for s_ in ("F1", "MIX", "F2"): rows.append(dict(kind=k, state=s_, n=cnt[k][s_], ratio=(cnt[k][s_] / n) / (allc[s_] / tot)))
pd.DataFrame(rows).to_csv(f"{CM.RES}/ped_decision_floor.csv", index=False); print(pd.DataFrame(rows).round(2).to_string(index=False))
