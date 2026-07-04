"""T1 - Replication ledger. One row per headline statistic from Studies 1-9, with Team A / Team B /
pooled estimates, same_direction, both_significant (where applicable), and a magnitude ratio
(min/max of |A|,|B|). Where a per-team split requires rerunning an established method on a team
subset (rather than just re-aggregating an existing per-meeting CSV), that is done faithfully with
the SAME method/parameters as the original study - never a new metric. Where a split is genuinely
not computable, the row is marked NA with a reason (never silently dropped)."""
import glob, os, re, json, unicodedata, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr, wilcoxon, kendalltau, skew, kurtosis, pearsonr
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from team_utils import team_of, TEAMS, NICE

LSH = os.path.expanduser("~/lsh-work")
sys.path.insert(0, LSH)
GM = f"{LSH}/data/metrics_gorman_l8"
OUT = os.path.dirname(__file__) + "/../data"
os.makedirs(OUT, exist_ok=True)
rows = []


def add(stat_id, description, study, a, b, pooled=None, a_sig=None, b_sig=None, note=""):
    same_dir = None
    mag_ratio = None
    if a is not None and b is not None and not (isinstance(a, float) and np.isnan(a)) and not (isinstance(b, float) and np.isnan(b)):
        same_dir = bool(np.sign(a) == np.sign(b)) if (a != 0 and b != 0) else None
        if a != 0 and b != 0:
            mag_ratio = min(abs(a), abs(b)) / max(abs(a), abs(b))
    both_sig = (a_sig is True and b_sig is True) if (a_sig is not None and b_sig is not None) else None
    rows.append(dict(stat_id=stat_id, description=description, study=study,
                      team_a=a, team_b=b, pooled=pooled, team_a_sig=a_sig, team_b_sig=b_sig,
                      same_direction=same_dir, both_significant=both_sig, magnitude_ratio=mag_ratio, note=note))
    print(f"[{stat_id}] A={a}  B={b}  pooled={pooled}  same_dir={same_dir}  note={note}")


# ============================================================ 1. LSH validity r (Study 1)
print("\n=== 1. LSH validity ===")
import gorman_reimpl as gr  # noqa
HZ = gr.HZ; WIN = gr.WIN_S * HZ; STEP = HZ
def winent(state, nsp):
    denom = np.log2(2 ** nsp) if nsp > 0 else 1
    out = []
    for a in range(0, len(state) - WIN, STEP):
        seg = state[a:a + WIN]; _, c = np.unique(seg, return_counts=True); p = c / c.sum()
        out.append(-(p * np.log2(p)).sum() / denom * 100 if denom > 0 else 0)
    return np.array(out)
r_by_team = {t: [] for t in TEAMS}
for f in sorted(glob.glob(f"{LSH}/data/text_startup/*_transcript.csv")):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    try:
        df = pd.read_csv(f); std, nsp = gr.build_states(df)
    except Exception:
        continue
    if nsp < 2 or len(std) < WIN + 10:
        continue
    lshs = std.copy(); last = 0
    for i in range(len(lshs)):
        if lshs[i] == 0: lshs[i] = last
        else: last = lshs[i]
    es = winent(std, nsp); el = winent(lshs, nsp); n = min(len(es), len(el))
    if n < 30: continue
    r_by_team[team_of(mid)].append(pearsonr(es[:n], el[:n])[0])
add("lsh_validity_r", "LSH vs standard entropy trajectory (median per-meeting r)", "Study 1",
    float(np.median(r_by_team["startup_a"])), float(np.median(r_by_team["startup_b"])),
    pooled=float(np.median(sum(r_by_team.values(), []))))

# ============================================================ 2. BC unimodality (Study 2)
print("\n=== 2. Bimodality coefficient ===")
def sarle_bc(x):
    x = x[np.isfinite(x)]
    g1 = skew(x); k = kurtosis(x, fisher=False); n = len(x)
    return (g1 ** 2 + 1) / (k + (3 * (n - 1) ** 2) / ((n - 2) * (n - 3)))
ent_by_team = {t: [] for t in TEAMS}
for f in glob.glob(f"{GM}/*_gorman.csv"):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    g = pd.read_csv(f)
    ent_by_team[team_of(mid)].append(g.entropy_g.dropna().to_numpy())
bc_a = sarle_bc(np.concatenate(ent_by_team["startup_a"]))
bc_b = sarle_bc(np.concatenate(ent_by_team["startup_b"]))
add("bimodality_coefficient", "Sarle BC on entropy_g (<0.555 = unimodal/continuum)", "Study 2",
    float(bc_a), float(bc_b), note="both well below 0.555 threshold = continuum in both teams")

# ============================================================ 3. Supra-AR excursion ratio (Study 2)
print("\n=== 3. Supra-autoregressive excursion ratio (rerunning AR1/VAR1 surrogate per team) ===")
M = Path(LSH) / "data/processed/metrics_startup"
def load_team(team, ns=200):
    meet = {}
    for mp in sorted(M.glob("*_entropy.csv")):
        mid = mp.name.replace("_entropy.csv", "")
        if team_of(mid) != team: continue
        meet[mid] = pd.read_csv(mp).sort_values("second").drop_duplicates("second").reset_index(drop=True)
    return meet

def feats(ent, det, k=2.0, w=90, sep=60):
    n = len(ent); thr = ent.mean() + k * ent.std(ddof=1); cand = []
    for i in range(1, n - 1):
        if ent[i] > thr and ent[i] >= ent[i - 1] and ent[i] >= ent[i + 1]:
            cand.append((i, ent[i]))
    cand.sort(key=lambda x: -x[1]); kept = []; u = []
    for i, v in cand:
        if all(abs(i - x) >= sep for x in u): kept.append(i); u.append(i)
    r = []
    for i in kept:
        if i - w < 0 or i + w >= n: continue
        r.append(ent[i + 1:i + w + 1].mean() - ent[i - w:i].mean())
    return r

def fit_ar1(x):
    x = np.asarray(x, float); y = x[1:]; X = np.column_stack([np.ones(len(x) - 1), x[:-1]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]; res = y - (b[0] + b[1] * x[:-1])
    return b[1], b[0], np.std(res, ddof=1)

def sim_ar1(n, phi, c, sig, rng, x0):
    o = np.empty(n); o[0] = x0
    for i in range(1, n): o[i] = c + phi * o[i - 1] + rng.normal(0, sig)
    return o

def supra_ar_ratio(team, ns=200, seed=42):
    meet = load_team(team)
    obs = []
    for mid, d in meet.items():
        obs += feats(d["entropy_lsh"].to_numpy(float), d["det_lsh"].to_numpy(float))
    obs_sd = float(np.std(obs, ddof=1))
    rng = np.random.default_rng(seed)
    par = {m: (fit_ar1(d["entropy_lsh"]), len(d), d["entropy_lsh"].mean()) for m, d in meet.items()}
    sds = []
    for _ in range(ns):
        vals = []
        for m, (ae, n, e0) in par.items():
            e = sim_ar1(n, *ae, rng, e0)
            vals += feats(e, e)  # det unused for SD(entropy) ratio; feed entropy twice, only ent used
        if len(vals) < 8: continue
        sds.append(np.std(vals, ddof=1))
    null_mean = float(np.mean(sds))
    return obs_sd, null_mean, obs_sd / null_mean, len(obs)

ratio_a = supra_ar_ratio("startup_a"); ratio_b = supra_ar_ratio("startup_b")
add("supra_ar_ratio", "SD(Δentropy) observed / AR(1) null (>1 = supra-autoregressive)", "Study 2",
    round(ratio_a[2], 3), round(ratio_b[2], 3),
    note=f"A: obs={ratio_a[0]:.3f} null={ratio_a[1]:.3f} n={ratio_a[3]}; "
         f"B: obs={ratio_b[0]:.3f} null={ratio_b[1]:.3f} n={ratio_b[3]}")

print("\nPart 1/2 (LSH, BC, supra-AR) complete. Continuing with taxonomy/floor/boundary/L10/S7/S9/S8 in part 2.")
rows_df = pd.DataFrame(rows)
rows_df.to_csv(f"{OUT}/replication_ledger_part1.csv", index=False)
print(f"wrote {OUT}/replication_ledger_part1.csv ({len(rows_df)} rows so far)")
