"""Meeting-to-meeting dependence with a two-sided permutation null.
Lag-1 Spearman rho between consecutive meetings, averaged over the two teams, against 5,000 permutations of meeting
order within team. Reads results/longit_panel.csv (from longitudinal_panel.py); writes results/longit_lag1_perm.csv."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
import common as CM

R = CM.RES
VARS = ["det", "entropy", "fac_word_share", "centralization", "collective"]
N_PERM = 5000

if __name__ == "__main__":
    D = pd.read_csv(f"{R}/longit_panel.csv").sort_values(["team", "week"])
    rng = np.random.default_rng(1)
    lag = lambda xs: np.mean([spearmanr(x[:-1], x[1:])[0] for x in xs])
    rows = []
    for v in VARS:
        xs = [g[v].to_numpy(float) for _, g in D.groupby("team")]
        o = lag(xs); null = np.array([lag([rng.permutation(x) for x in xs]) for _ in range(N_PERM)])
        p2 = (np.sum(np.abs(null) >= abs(o)) + 1) / (N_PERM + 1)
        rows.append(dict(var=v, lag1_rho=o, null_mean=null.mean(), p_two_sided=p2))
        print(f"{v:16s} rho {o:+.3f}  null mean {null.mean():+.3f}  two-sided p {p2:.3f}")
    pd.DataFrame(rows).to_csv(f"{R}/longit_lag1_perm.csv", index=False)
