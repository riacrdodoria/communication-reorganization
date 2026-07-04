"""T2 - Profile replication: the strong test. For each of 4 family-level profiles (taxonomy fingerprint
40 categories, floor measures 9, review-vs-IDS 41 categories, border-vs-interior 40 categories), compute
the per-team effect-size vector, then Spearman r between Team A and Team B vectors + a permutation null
(shuffle category labels, 10000 seeded runs) + a sign-agreement binomial test."""
import glob, os, re, json, unicodedata, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr, binomtest
from statsmodels.stats.multitest import multipletests
sys.path.insert(0, os.path.dirname(__file__))
from team_utils import team_of, TEAMS

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
OUT = os.path.dirname(__file__) + "/../data"
TCRIT = 2.33
rng = np.random.default_rng(1100)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s).lower()); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def l10_onsets(mid):
    f = f"{LSH}/data/l10_stages/{mid}.json"; tp = f"{LSH}/data/text_startup/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d = json.load(open(f)); tx = pd.read_csv(tp)
    on = pd.to_numeric(tx.onset_seconds, errors="coerce").to_numpy(); nt = [norm(t) for t in tx.text]
    seg = []; prev = 0
    for st in d["stages"]:
        q = norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(nt)):
            if q and q in nt[i]: idx = i; break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx = i; break
        if idx is not None: seg.append(float(on[idx])); prev = idx + 1
    return seg


def stage_bounds(mid):
    f = f"{LSH}/data/l10_stages/{mid}.json"; tp = f"{LSH}/data/text_startup/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return None
    d = json.load(open(f)); tx = pd.read_csv(tp)
    on = pd.to_numeric(tx["onset_seconds"], errors="coerce").to_numpy(); ntx = [norm(t) for t in tx["text"]]
    seg = []; prev = 0
    for st in d["stages"]:
        q = norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(ntx)):
            if q and q in ntx[i]: idx = i; break
        if idx is None:
            for i in range(len(ntx)):
                if q and q in ntx[i]: idx = i; break
        if idx is not None: seg.append((st["name"], float(on[idx]))); prev = idx + 1
    if not seg: return None
    bounds = [s[1] for s in seg] + [float(np.nanmax(on)) + 5]
    return [(seg[k][0], seg[k][1], bounds[k + 1]) for k in range(len(seg))]


CATS2 = ['arguable', 'converge', 'disagree', 'delim', 'nonarg', 'iam1', 'iam2', 'iam3', 'iam4', 'iam5',
         'disput', 'cumul', 'explor', 'bgiveinfo', 'bgiveopin', 'bgivesug', 'baskinfo', 'baskopin',
         'basksug', 'bsolid', 'btension', 'bagree', 'bdisagree', 'btensh', 'bantag']
CATS1 = ['namep', 'linkp', 'names', 'links', 'linkc', 'cprod', 'proact', 'struct', 'ginfo', 'ktrans',
         'coop', 'qset', 'qprop', 'directive', 'commissive', 'feedback']


def perm_test_spearman(a, b, n_perm=10000, seed=1100):
    r_obs, _ = spearmanr(a, b)
    rr = np.random.default_rng(seed)
    n = len(a); null = np.empty(n_perm)
    for i in range(n_perm):
        perm = rr.permutation(n)
        null[i] = spearmanr(a, np.asarray(b)[perm])[0]
    p_perm = np.mean(np.abs(null) >= abs(r_obs))
    return r_obs, p_perm, null


def sign_binomial(a, b, label):
    a = np.asarray(a); b = np.asarray(b)
    ok = (a != 0) & (b != 0) & np.isfinite(a) & np.isfinite(b)
    same = int((np.sign(a[ok]) == np.sign(b[ok])).sum()); n = int(ok.sum())
    res = binomtest(same, n, 0.5, alternative="greater")
    print(f"  sign agreement [{label}]: {same}/{n} ({100*same/n:.0f}%)  binomial p={res.pvalue:.2e}")
    return dict(profile=label, n_same=same, n_total=n, pct=100 * same / n, binom_p=res.pvalue)


summary_rows = []

# ============================================================ A. Taxonomy fingerprint (40 categories)
print("=" * 90, "\nA. Taxonomy fingerprint profile replication (40 categories)\n" + "=" * 90)
TAX = pd.read_csv(f"{OUT}/taxonomy_lift_by_team.csv")
r_tax, p_tax, null_tax = perm_test_spearman(TAX.team_a_lift, TAX.team_b_lift)
print(f"Spearman r(Team A lift, Team B lift) across {len(TAX)} categories = {r_tax:.3f}  "
      f"permutation p = {p_tax:.2e}  (null 95% range [{np.percentile(null_tax,2.5):.2f},{np.percentile(null_tax,97.5):.2f}])")
summary_rows.append(dict(profile="taxonomy_fingerprint_40cat", n_items=len(TAX), spearman_r=r_tax, perm_p=p_tax))
sign_binomial(TAX.team_a_lift, TAX.team_b_lift, "taxonomy_fingerprint_40cat")

# ============================================================ B. Floor measures (9)
print("\n" + "=" * 90, "\nB. Floor-measure profile replication (9 measures)\n" + "=" * 90)
LEDGER = pd.read_csv(f"{OUT}/replication_ledger.csv")
FLOOR = LEDGER[LEDGER.stat_id.str.startswith("floor_")]
r_floor, p_floor, null_floor = perm_test_spearman(FLOOR.team_a, FLOOR.team_b)
print(f"Spearman r(Team A r, Team B r) across {len(FLOOR)} floor measures = {r_floor:.3f}  permutation p = {p_floor:.3f}")
summary_rows.append(dict(profile="floor_measures_9", n_items=len(FLOOR), spearman_r=r_floor, perm_p=p_floor))
sign_binomial(FLOOR.team_a, FLOOR.team_b, "floor_measures_9")

# ============================================================ C. Review-vs-IDS (41 categories), per team
print("\n" + "=" * 90, "\nC. Review-vs-IDS content contrast, per team (41 categories)\n" + "=" * 90)
EP = pd.read_csv(f"{LSH}/episode_codes.csv")
REVIEW = {"scorecard", "rock_review", "todo"}
EP2 = EP.copy(); EP2["l10"] = None
for mid, g in EP2.groupby("mid"):
    sb = stage_bounds(mid)
    if not sb: continue
    for i, r in g.iterrows():
        for name, s0, s1 in sb:
            if s0 <= r["sec_start"] < s1: EP2.at[i, "l10"] = name; break
EP2 = EP2[EP2["l10"].notna()].copy()
EP2["team"] = EP2.mid.apply(team_of)
ALLCATS = [c for c in CATS2 + CATS1 if c in EP2.columns]

def review_vs_ids_vector(team):
    sub = EP2[EP2.team == team]
    rows = []
    for mid, g in sub.groupby("mid"):
        rv = g[g.l10.isin(REVIEW)]; iv = g[g.l10 == "ids"]
        if not len(rv) or not len(iv): continue
        nut_r = rv["n_utt"].sum(); nut_i = iv["n_utt"].sum()
        rows.append((mid, {c: rv[c].sum() / nut_r if nut_r else np.nan for c in ALLCATS},
                    {c: iv[c].sum() / nut_i if nut_i else np.nan for c in ALLCATS}))
    out = {}
    for c in ALLCATS:
        rv_vals = np.array([r[1][c] for r in rows]); iv_vals = np.array([r[2][c] for r in rows])
        ok = ~(np.isnan(rv_vals) | np.isnan(iv_vals))
        if ok.sum() < 8: continue
        out[c] = 100 * (np.nanmean(rv_vals[ok]) - np.nanmean(iv_vals[ok]))
    return out

rvi_a = review_vs_ids_vector("startup_a"); rvi_b = review_vs_ids_vector("startup_b")
common = sorted(set(rvi_a) & set(rvi_b))
va = [rvi_a[c] for c in common]; vb = [rvi_b[c] for c in common]
pd.DataFrame({"cat": common, "team_a_delta": va, "team_b_delta": vb}).to_csv(f"{OUT}/review_vs_ids_by_team.csv", index=False)
r_rvi, p_rvi, null_rvi = perm_test_spearman(va, vb)
print(f"Spearman r(Team A Δ, Team B Δ) across {len(common)} categories = {r_rvi:.3f}  permutation p = {p_rvi:.3f}")
summary_rows.append(dict(profile="review_vs_ids_41cat", n_items=len(common), spearman_r=r_rvi, perm_p=p_rvi))
sign_binomial(va, vb, "review_vs_ids_41cat")

# ============================================================ D. Border-vs-interior contrast (40 categories), per team
print("\n" + "=" * 90, "\nD. Border-vs-interior content contrast, per team (40 categories)\n" + "=" * 90)
def load_cb(folder):
    d = {}
    for f in glob.glob(f"{LSH}/{folder}/*_passA.json"):
        mid = os.path.basename(f).replace("_passA.json", ""); d[mid] = {int(w["t"]): w for w in json.load(open(f))["windows"]}
    return d
c2 = load_cb("data/codebooks2"); c1 = load_cb("data/codebooks")
from collections import defaultdict
bl_team = {t: defaultdict(list) for t in TEAMS}; il_team = {t: defaultdict(list) for t in TEAMS}
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    if mid not in c2: continue
    team = team_of(mid)
    g = pd.read_csv(f); secs = g.second.to_numpy(); x = g.rmse_g.to_numpy(float)
    m = np.nanmean(x); sd = np.nanstd(x); peak = (x > m + TCRIT * sd); base = ~peak & np.isfinite(x)
    bd = sorted(set(EP[EP.mid == mid].sec_start.tolist()) | set(l10_onsets(mid)))
    if not bd: continue
    near = np.zeros(len(secs), bool)
    for b in bd: near |= (np.abs(secs - b) <= 30)
    bpk = peak & near; ipk = peak & ~near
    if bpk.sum() < 6 or ipk.sum() < 6 or base.sum() < 20: continue
    win = lambda s: int(s // 90 * 90)
    for cat in CATS2 + CATS1:
        cd = c2[mid] if cat in CATS2 else c1.get(mid, {})
        dens = np.array([cd.get(win(s), {}).get(cat, 0) for s in secs], float)
        if dens.sum() == 0: continue
        b0 = dens[base].mean()
        bl_team[team][cat].append(dens[bpk].mean() - b0); il_team[team][cat].append(dens[ipk].mean() - b0)

def bord_int_contrast(team):
    out = {}
    for cat in CATS2 + CATS1:
        bl = bl_team[team][cat]; il = il_team[team][cat]
        if len(bl) < 8 or len(il) < 8: continue
        out[cat] = np.mean(bl) - np.mean(il)  # border-minus-interior contrast
    return out
bi_a = bord_int_contrast("startup_a"); bi_b = bord_int_contrast("startup_b")
common_bi = sorted(set(bi_a) & set(bi_b))
va2 = [bi_a[c] for c in common_bi]; vb2 = [bi_b[c] for c in common_bi]
pd.DataFrame({"cat": common_bi, "team_a_contrast": va2, "team_b_contrast": vb2}).to_csv(f"{OUT}/border_interior_by_team.csv", index=False)
r_bi, p_bi, null_bi = perm_test_spearman(va2, vb2)
print(f"Spearman r(Team A contrast, Team B contrast) across {len(common_bi)} categories = {r_bi:.3f}  permutation p = {p_bi:.3f}")
summary_rows.append(dict(profile="border_interior_40cat", n_items=len(common_bi), spearman_r=r_bi, perm_p=p_bi))
sign_binomial(va2, vb2, "border_interior_40cat")

# ============================================================ Overall combined sign-agreement (all 4 profiles + ledger directional items)
print("\n" + "=" * 90, "\nOverall combined sign-agreement (4 profile vectors pooled)\n" + "=" * 90)
all_a = list(TAX.team_a_lift) + list(FLOOR.team_a) + va + va2
all_b = list(TAX.team_b_lift) + list(FLOOR.team_b) + vb + vb2
overall = sign_binomial(all_a, all_b, "ALL_PROFILES_COMBINED")
pd.DataFrame(summary_rows).to_csv(f"{OUT}/profile_replication_summary.csv", index=False)
pd.DataFrame([overall]).to_csv(f"{OUT}/profile_sign_agreement_overall.csv", index=False)
print("\nwrote review_vs_ids_by_team.csv, border_interior_by_team.csv, profile_replication_summary.csv, "
      "profile_sign_agreement_overall.csv")
