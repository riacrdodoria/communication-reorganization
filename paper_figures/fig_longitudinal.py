"""Figure — Seventeen weeks of two teams: selected meeting-level trajectories (longitudinal_panel.py).
Each panel: one measure per meeting by week, both teams; Kendall tau per team in the corner. Bottom-right panel:
consecutive meetings alternate in their level of organization (lag-1 scatter of mean %DET)."""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import kendalltau, spearmanr
import paper_style as ps
ps.setup(); R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results"); D = pd.read_csv(f"{R}/longit_panel.csv")
TEAM = {"A": "#1f6fb4", "B": "#d95f02"}
PAN = [("active", "active speakers (per 60 s)"), ("F2", "time in collaborative floor"), ("fac_word_share", "facilitator share of words"),
       ("centralization", "turn-network centralization"), ("collective", "'a gente / nós' per 100 words"), ("recurrence_all_prior", "content from own earlier weeks"),
       ("event_rate", "reorganization events per hour")]
fig, axs = plt.subplots(2, 4, figsize=(7.2, 3.9)); axs = axs.ravel()
for ax, (v, lab) in zip(axs, PAN):
    txt = []
    for t in "AB":
        g = D[D.team == t].sort_values("week").dropna(subset=[v]); ax.plot(g.week, g[v], "-o", color=TEAM[t], ms=2.5, lw=1, label=f"Team {t}")
        tau, p = kendalltau(g.week, g[v]); txt.append(f"{t} τ={tau:+.2f}{'*' if p < .05 else ''}")
    ax.set_title(lab, fontsize=6.6, color=ps.INK, loc="left"); ax.tick_params(labelsize=5.6); ax.text(.02, .96, "\n".join(txt), transform=ax.transAxes, fontsize=5.2, va="top", color=ps.INK)
    ax.set_xlabel("week", fontsize=5.8)
fig.legend(*axs[0].get_legend_handles_labels(), fontsize=6, frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(.5, 1.04))
ax = axs[-1]
for t in "AB":
    g = D[D.team == t].sort_values("week"); x = g.det.to_numpy() - g.det.mean(); ax.scatter(x[:-1], x[1:], s=10, color=TEAM[t])
rho = np.mean([spearmanr(D[D.team == t].sort_values("week").det.to_numpy()[:-1], D[D.team == t].sort_values("week").det.to_numpy()[1:])[0] for t in "AB"])
ax.axhline(0, color=ps.NEUTRAL, lw=.5, ls=":"); ax.axvline(0, color=ps.NEUTRAL, lw=.5, ls=":")
ax.set_title("%DET: meeting w vs w+1 (team-centred)", fontsize=6.6, color=ps.INK, loc="left"); ax.set_xlabel("%DET, week w", fontsize=5.8); ax.set_ylabel("%DET, week w+1", fontsize=5.8)
ax.tick_params(labelsize=5.6); ax.text(.02, .96, f"lag-1 ρ={rho:+.2f}\npermutation p=.013", transform=ax.transAxes, fontsize=5.2, va="top", color=ps.INK)
fig.tight_layout(w_pad=.8, h_pad=1.0)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/fig_longitudinal.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok")
