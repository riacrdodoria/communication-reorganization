"""Paper figure — Study 11: the intensive longitudinal replication ledger (Team A vs Team B).
Every headline effect size in the program, normalized within-pair (divide both by max(|a|,|b|), keep
sign) so magnitude_ratio is directly readable as distance from the y=x line, and cross-team sign
agreement is directly readable as which diagonal quadrant a point falls in. Distinct marker SHAPES per
family (not just color) for grayscale legibility."""
import numpy as np, pandas as pd, os
import matplotlib.pyplot as plt
import paper_style as ps
ps.setup()

LSH = os.path.expanduser("~/lsh-work")
S11 = f"{LSH}/study11_replication/data"

ledger = pd.read_csv(f"{S11}/replication_ledger.csv")
tax = pd.read_csv(f"{S11}/taxonomy_lift_by_team.csv")
rvi = pd.read_csv(f"{S11}/review_vs_ids_by_team.csv")
bi = pd.read_csv(f"{S11}/border_interior_by_team.csv")
lon = pd.read_csv(f"{S11}/longitudinal_bootstrap.csv")

FAMS = []  # (label, marker, color, list of (a,b))
FAMS.append(("Taxonomy fingerprint (40 cat.)", "o", ps.COORD,
             list(zip(tax.team_a_lift, tax.team_b_lift))))
FAMS.append(("Review-vs-IDS content contrast (41 cat.)", "^", "#7b3294",
             list(zip(rvi.team_a_delta, rvi.team_b_delta))))
FAMS.append(("Border-vs-interior content contrast (40 cat.)", "D", "#1b7837",
             list(zip(bi.team_a_contrast, bi.team_b_contrast))))
floor = ledger[ledger.stat_id.str.startswith("floor_")]
FAMS.append(("Floor / network measures (9)", "s", ps.DELIB,
             list(zip(floor.team_a, floor.team_b))))
FAMS.append(("Longitudinal trends, Kendall tau (5)", "P", "#b2182b",
             list(zip(lon.team_a_tau, lon.team_b_tau))))
excl = {"taxonomy_fingerprint_sign_agreement"} | set(floor.stat_id) | set(lon.stat_id)
head = ledger[~ledger.stat_id.isin(excl) & ledger.team_a.notna() & ledger.team_b.notna()]
FAMS.append(("Headline validity / mechanism stats (13)", "*", ps.NEUTRAL,
             list(zip(head.team_a, head.team_b))))

fig, ax = plt.subplots(figsize=(7.6, 7.4))
ax.plot([-1.15, 1.15], [-1.15, 1.15], color=ps.INK, lw=1.1, ls="--", zorder=1, alpha=.75)
ax.axhline(0, color=ps.GRID, lw=.9, zorder=0); ax.axvline(0, color=ps.GRID, lw=.9, zorder=0)

n_same = 0; n_tot = 0
for label, marker, color, pairs in FAMS:
    na, nb = [], []
    for a, b in pairs:
        if a is None or b is None or not np.isfinite(a) or not np.isfinite(b) or (a == 0 and b == 0):
            continue
        m = max(abs(a), abs(b))
        na.append(a / m); nb.append(b / m)
        n_tot += 1; n_same += int(np.sign(a) == np.sign(b))
    ax.scatter(na, nb, marker=marker, s=72 if marker in ("*", "P") else 46, facecolor=color,
               edgecolor="white", linewidth=.6, alpha=.85, zorder=3, label=f"{label}  (n={len(na)})")

ax.set_xlim(-1.15, 1.15); ax.set_ylim(-1.15, 1.15)
ax.set_xlabel("Team A effect size  (sign-preserved, normalized by max(|A|,|B|) per statistic)")
ax.set_ylabel("Team B effect size  (same normalization)")
ax.set_title("Study 11 — Cross-team replication ledger: does Team B's effect\nmatch Team A's, in sign and magnitude?", loc="left")
ax.legend(loc="lower right", fontsize=7.6, markerscale=1.05, handletextpad=.5, labelspacing=.55,
          bbox_to_anchor=(1.02, -0.02))
ps.statbox(ax, f"Same-sign agreement (all families pooled):\n{n_same}/{n_tot} statistics "
                f"({100*n_same/n_tot:.0f}%)\nPoints near the dashed y=x line replicate in both\n"
                "sign AND magnitude; off-diagonal but same-\nquadrant points replicate in sign only.",
           loc="upper left")
ps.caption(fig, "Figure 11. n = 145 headline statistics spanning validity checks, content-taxonomy "
    "profiles, floor-structure measures, and longitudinal trends, each computed independently in Team "
    "A and Team B using identical methods (Studies 1-10). Values are normalized per statistic (divide "
    "both teams' estimates by whichever is larger in magnitude, preserving sign), so the y=x line "
    "represents perfect cross-team replication and quadrant membership (top-right / bottom-left vs. "
    "top-left / bottom-right) directly shows sign agreement. Two known, explicitly flagged non-"
    "replications (initiator-rank stability; facilitator-share longitudinal trend) sit in the off-"
    "diagonal quadrants among the gray stars/plus markers.", y=-0.045)
fig.tight_layout(rect=[0, 0.05, 1, 1])
ps.save(fig, "fig_paper_S11_replication_ledger")
