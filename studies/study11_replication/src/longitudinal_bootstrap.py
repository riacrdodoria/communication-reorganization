"""T3 - Longitudinal replication: per-team Kendall tau for the 5 established longitudinal trends
(Study 5: mean_entropy, net_central, part_entropy; Study 7: base_ent, BORDER_ent_exc), each with a
meeting-clustered bootstrap CI (resample meetings with replacement WITHIN team, recompute tau, 2000
reps, percentile CI), and an explicit replicate / non-replicate / indeterminate verdict per trend."""
import os, sys
import numpy as np, pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(__file__))
from team_utils import team_of, TEAMS, NICE

LSH = os.path.expanduser("~/lsh-work")
OUT = os.path.dirname(__file__) + "/../data"
rng_seed = 1100
N_BOOT = 2000

P1 = pd.read_csv(f"{LSH}/longitudinal_panel.csv")
P2 = pd.read_csv(f"{LSH}/reorg_depth_longitudinal_panel.csv")

TRENDS = [
    ("long_tau_entropy", "Study 5", P1, "mean_entropy", "Kendall tau: mean entropy vs week"),
    ("long_tau_netcentral", "Study 5", P1, "net_central", "Kendall tau: network centralization vs week"),
    ("long_tau_partentropy", "Study 5", P1, "part_entropy", "Kendall tau: participation entropy vs week"),
    ("s7_tau_baseline", "Study 7", P2, "base_ent", "Kendall tau: baseline (resting) entropy vs week"),
    ("s7_tau_excursion", "Study 7", P2, "BORDER_ent_exc", "Kendall tau: border-event excursion above baseline vs week"),
]


def boot_tau(sub, col, seed):
    x = sub["week"].to_numpy(); y = sub[col].to_numpy()
    ok = np.isfinite(x) & np.isfinite(y); x = x[ok]; y = y[ok]
    tau_obs = kendalltau(x, y)[0]
    rr = np.random.default_rng(seed); n = len(x)
    boots = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rr.integers(0, n, n)
        t = kendalltau(x[idx], y[idx])[0]
        boots[i] = t if np.isfinite(t) else np.nan
    boots = boots[np.isfinite(boots)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return tau_obs, lo, hi, n


rows = []
print("=" * 100)
for stat_id, study, panel, col, desc in TRENDS:
    print(f"\n{desc}  [{stat_id}, {study}]")
    res = {}
    for team in TEAMS:
        sub = panel[panel.team == team]
        tau, lo, hi, n = boot_tau(sub, col, seed=rng_seed + hash(stat_id + team) % 10000)
        excl_zero = (lo > 0) or (hi < 0)
        res[team] = dict(tau=tau, lo=lo, hi=hi, n=n, excl_zero=excl_zero)
        print(f"  {NICE[team]}: tau={tau:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  (n={n})  "
              f"{'excludes zero' if excl_zero else 'CI includes zero'}")
    same_dir = np.sign(res["startup_a"]["tau"]) == np.sign(res["startup_b"]["tau"])
    both_excl = res["startup_a"]["excl_zero"] and res["startup_b"]["excl_zero"]
    either_excl = res["startup_a"]["excl_zero"] or res["startup_b"]["excl_zero"]
    if same_dir and both_excl:
        verdict = "REPLICATES (same direction, both CIs exclude zero)"
    elif same_dir and either_excl:
        verdict = "PARTIAL REPLICATION (same direction, only one team's CI excludes zero)"
    elif same_dir:
        verdict = "SAME DIRECTION but neither CI excludes zero (underpowered, not a contradiction)"
    else:
        verdict = "NON-REPLICATION (opposite direction across teams)"
    print(f"  VERDICT: {verdict}")
    rows.append(dict(stat_id=stat_id, study=study, description=desc,
                      team_a_tau=res["startup_a"]["tau"], team_a_ci_lo=res["startup_a"]["lo"], team_a_ci_hi=res["startup_a"]["hi"],
                      team_b_tau=res["startup_b"]["tau"], team_b_ci_lo=res["startup_b"]["lo"], team_b_ci_hi=res["startup_b"]["hi"],
                      same_direction=bool(same_dir), both_ci_exclude_zero=bool(both_excl), verdict=verdict))

df = pd.DataFrame(rows)
df.to_csv(f"{OUT}/longitudinal_bootstrap.csv", index=False)
print("\n" + "=" * 100)
print(f"wrote {OUT}/longitudinal_bootstrap.csv ({len(df)} rows)")
print(f"replicate/partial: {sum(v.startswith(('REPLICATES','PARTIAL')) for v in df.verdict)}/{len(df)}")
