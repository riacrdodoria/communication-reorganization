"""Whole-session entropy and %DET trajectories of one surgical session (the Figure 1 excerpt session) under the true
standard series, pure LSH and the word-timed reconstruction (LSH-WD), with the archival metric code.
Output: results/fig1_traces.csv"""
import os, numpy as np, pandas as pd
src = open(os.path.join(os.path.dirname(__file__), "lsh_convergent_current_params.py")).read(); src = src[:src.index("inv = pd.read_csv")]
ns = {}; exec(src, ns)
z = np.load(os.path.join(os.path.dirname(__file__), "results/lsh_variants_excerpt.npz")); std = z["standard"]; nsp = len(set(std[std > 0]))
out = []
for key, lab, nmax in [("standard", "true standard", nsp + 1), ("LSH", "pure LSH", nsp), ("LSH-WD", "LSH-WD", nsp + 1)]:
    m = ns["metrics"](z[key], nmax); m["rep"] = lab; out.append(m[["second", "entropy", "det", "rep"]])
D = pd.concat(out); D.to_csv(os.path.join(os.path.dirname(__file__), "results/fig1_traces.csv"), index=False)
w = D.pivot_table(index="second", columns="rep", values=["entropy", "det"])
for v in ["entropy", "det"]:
    print(v, {r: round(np.corrcoef(w[(v, "true standard")], w[(v, r)])[0, 1], 3) for r in ["pure LSH", "LSH-WD"]})
