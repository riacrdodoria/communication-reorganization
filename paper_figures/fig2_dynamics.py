"""Figure 2 — What kind of dynamic (Paper 1, Study 2).
A: pooled %MaxEnt distribution with Gaussian fit and Sarle bimodality coefficient (a continuum, not two regimes).
B: entropy excursions at peaks relative to three nulls: size vs AR(1), VAR(1) and run-order shuffle; count vs shuffle.
C: share of segments with periodicity (1-5 min) beyond the run-shuffle null, by cut; dotted line = 5 % chance.
D: share of %MaxEnt variance between agenda stages (eta2), observed vs run-shuffled meeting, per meeting.
E: 40 minutes of one meeting: %MaxEnt with agenda stages shaded and reorganization event onsets marked."""
import os, sys, glob, json, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, norm, wilcoxon
import paper_style as ps
ps.setup(); L = os.path.expanduser("~/lsh-work"); R = f"{L}/study13_metric_extensions/results"; sys.path.insert(0, f"{L}/study13_metric_extensions/src"); import common as CM
BLUE, ORANGE, INK, MUTED = "#1f6fb4", "#d95f02", ps.INK, ps.NEUTRAL; TEAM = {"A": BLUE, "B": ORANGE}
fig = plt.figure(figsize=(7.2, 5.6)); gs = fig.add_gridspec(2, 4, height_ratios=[1, .8], hspace=.55, wspace=.75)
axA, axB, axC, axD = [fig.add_subplot(gs[0, k]) for k in range(4)]; axE = fig.add_subplot(gs[1, :])
# A
E = np.concatenate([pd.read_csv(f).entropy_g.to_numpy(float) for f in glob.glob(f"{L}/data/metrics_gorman_l8/*_gorman.csv")]); E = E[np.isfinite(E)]
n = E.size; BC = (skew(E) ** 2 + 1) / (kurtosis(E) + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))); xs = np.linspace(E.min(), E.max(), 200)
axA.hist(E, bins=40, density=True, color=ps.COORD, alpha=.5, edgecolor="white", lw=.2); axA.plot(xs, norm.pdf(xs, E.mean(), E.std()), color=INK, lw=1.2)
axA.text(.97, .97, f"BC = {BC:.3f}\n(< 0.555:\nunimodal)", transform=axA.transAxes, ha="right", va="top", fontsize=5.6, color=INK)
axA.set_xlabel("%MaxEnt", fontsize=6.4); axA.set_yticks([]); axA.tick_params(labelsize=5.8); axA.grid(False)
axA.set_title("A. A continuum", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# B
sv = pd.read_csv(f"{L}/surrogate_validation_results.csv").iloc[0]; rs = pd.read_csv(f"{R}/runshuffle_study1.csv", keep_default_na=False); o = rs[rs.kind == "observed"].iloc[0]; nl = rs[rs.kind == "null"]
rows = [("size\nAR(1)", sv.obs_sd / sv.AR1_sd_mean, sv.AR1_sd_lo / sv.AR1_sd_mean, sv.AR1_sd_hi / sv.AR1_sd_mean),
        ("size\nVAR(1)", sv.obs_sd / sv.VAR1_sd_mean, sv.VAR1_sd_lo / sv.VAR1_sd_mean, sv.VAR1_sd_hi / sv.VAR1_sd_mean)]
for c, lab in [("sd_excursion", "size\nshuffle"), ("n_peaks", "count\nshuffle")]:
    m = nl[c].mean(); lo, hi = np.percentile(nl[c], [2.5, 97.5]); rows.append((lab, o[c] / m, lo / m, hi / m))
for i, (lab, v, lo, hi) in enumerate(rows):
    axB.plot([i, i], [lo, hi], color="#b9c2cc", lw=5, solid_capstyle="butt"); axB.scatter(i, v, s=24, color=INK if v > hi else "white", edgecolor=INK, zorder=3)
    axB.text(i, v + .12, f"{v:.2f}×", ha="center", fontsize=5.6, color=INK)
axB.axhline(1, color=MUTED, ls=":", lw=.8); axB.set_xticks(range(4)); axB.set_xticklabels([r[0] for r in rows], fontsize=5.6); axB.set_ylim(.5, 2.7); axB.tick_params(axis="y", labelsize=5.8)
axB.set_ylabel("observed / null mean", fontsize=6.2); axB.set_title("B. More frequent,\nnot larger", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# C
Pp = pd.read_csv(f"{R}/system_cuts_periodicity.csv").dropna(subset=["p"]); order = [("fixed_5min", "5"), ("fixed_10min", "10"), ("fixed_20min", "20"), ("stage", "stage")]
sh = [(Pp[Pp.cut == c].p < .05).mean() for c, _ in order]; ns = [(Pp.cut == c).sum() for c, _ in order]
axC.bar(range(4), sh, .6, color="#9fb6d6"); axC.axhline(.05, color=INK, ls=":", lw=.9); axC.text(3.45, .052, "chance", fontsize=5.4, ha="right", va="bottom", color=INK)
for i, (v, k) in enumerate(zip(sh, ns)): axC.text(i, v + .003, f"n={k}", ha="center", fontsize=5.0, color=MUTED)
axC.set_xticks(range(4)); axC.set_xticklabels([l for _, l in order], fontsize=5.8); axC.set_xlabel("cut (min) or agenda stage", fontsize=6.0); axC.set_ylim(0, .08); axC.set_ylabel("share periodic (1-5 min)", fontsize=6.2); axC.tick_params(axis="y", labelsize=5.8)
axC.set_title("C. No periodicity\n(System I)", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# D
Et = pd.read_csv(f"{R}/system_cuts_eta.csv")
for t, g in Et.groupby("team"):
    for _, r in g.iterrows(): axD.plot([0, 1], [r.eta_stage_null, r.eta_stage], color=TEAM[t], lw=.6, alpha=.6)
    axD.scatter(np.zeros(len(g)), g.eta_stage_null, s=6, color=TEAM[t]); axD.scatter(np.ones(len(g)), g.eta_stage, s=6, color=TEAM[t], label=f"Team {t}")
p = wilcoxon(Et.eta_stage - Et.eta_stage_null).pvalue
axD.set_xticks([0, 1]); axD.set_xticklabels(["shuffled\nmeeting", "observed"], fontsize=5.8); axD.set_xlim(-.4, 1.4); axD.tick_params(axis="y", labelsize=5.8)
axD.set_ylabel("variance between stages (η²)", fontsize=6.2); axD.text(.5, .97, f"p = {p:.0e}", transform=axD.transAxes, ha="center", va="top", fontsize=5.6, color=INK)
axD.legend(fontsize=5.2, frameon=False, loc="upper left", bbox_to_anchor=(0, .9)); axD.set_title("D. The setpoint\nmoves by stage", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
# E
m = "2024.12.09startup_a"; g = CM.metrics(m); g = g[(g.second >= 0) & (g.second <= 2400)]; segs = CM.stage_segments(m); ev = CM.events(); ev = ev[ev.mid == m].event_onset_s
LAB = {"segue": "check-in", "scorecard": "scorecard", "rock_review": "rocks", "headlines": "headlines", "todo": "to-dos", "ids": "IDS", "conclude": "close"}
for k, (nm, a, b) in enumerate(segs):
    if a > 2400: continue
    axE.axvspan(a / 60, min(b, 2400) / 60, color="#eceae6" if k % 2 == 0 else "#f7f6f3", lw=0); axE.text((a + min(b, 2400)) / 120, 71, LAB.get(nm, nm), ha="center", fontsize=5.6, color=MUTED)
axE.plot(g.second / 60, g.entropy_g, color=ps.COORD, lw=1)
for e in ev[ev <= 2400]: axE.axvline(e / 60, color=INK, lw=.6, ls="--", alpha=.7)
axE.set_xlim(0, 40); axE.set_ylim(0, 76); axE.set_xlabel("meeting time (min)", fontsize=6.6); axE.set_ylabel("%MaxEnt", fontsize=6.6); axE.tick_params(labelsize=5.8); axE.grid(axis="x", visible=False)
axE.set_title("E. Forty minutes of one meeting: agenda stages (shaded) and reorganization event onsets (dashed)", loc="left", fontsize=8.4, fontweight="bold", color=ps.COORD)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/fig2_dynamics.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok", round(BC, 3))
