"""Figure — Where emotions and decisions concentrate (model- and lexicon-based signals; not human-validated).
A: emotions by floor state and by agenda stage (mean within-meeting standardized difference; filled = Wilcoxon p < .05).
B: emotions around reorganization events, observed minus surrogate events (z); dots = outside the surrogate 95 % band.
C: decision utterances by floor state (share in that state / share of all utterances); filled = chi-square p < .05.
D: explicit agreement around events (rate relative to the meeting rate, 15-s bins); grey band = surrogate events 95 %."""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import wilcoxon, chisquare
import paper_style as ps
ps.setup(); R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results")
EM = pd.read_csv(f"{R}/ped_emotions_meeting.csv"); SG = pd.read_csv(f"{R}/ped_emo_signature.csv"); DF = pd.read_csv(f"{R}/ped_decision_floor.csv"); PE = pd.read_csv(f"{R}/ped_decision_peth.csv")
BLUE, ORANGE, INK, MUTED = "#1f6fb4", "#d95f02", ps.INK, ps.NEUTRAL
EMO = ["approval", "disapproval", "admiration", "optimism", "realization", "curiosity", "confusion"]
fig = plt.figure(figsize=(7.2, 6.0)); gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.25], hspace=.62, wspace=.55)
axA, axB, axC, axD = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
# --- A
y = np.arange(len(EMO))[::-1]
for yy, e in zip(y, EMO):
    for col, mk, off, lab in [(f"emo_{e}_F2mF1", "o", .13, "collaborative − single-speaker floor"), (f"emo_{e}_IDSmREV", "s", -.13, "IDS − review")]:
        x = EM[col].dropna(); p = wilcoxon(x).pvalue; c = BLUE if mk == "o" else ORANGE
        axA.scatter(x.mean(), yy + off, marker=mk, s=22, facecolor=c if p < .05 else "white", edgecolor=c, lw=.9, zorder=3, label=lab if yy == y[0] else None)
axA.axvline(0, color=MUTED, lw=.7, ls=":"); axA.set_yticks(y); axA.set_yticklabels(EMO, fontsize=6.6); axA.grid(axis="y", visible=False)
axA.set_xlabel("standardized difference (z)", fontsize=6.6); axA.tick_params(axis="x", labelsize=6)
axA.legend(fontsize=5.4, frameon=False, loc="upper center", bbox_to_anchor=(.45, -.2), ncol=1)
axA.set_title("A. Where emotions concentrate", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
# --- B
STY = {"approval": (BLUE, "-"), "disapproval": (BLUE, "--"), "curiosity": (ORANGE, "-"), "confusion": (ORANGE, "--")}
for e, (c, ls) in STY.items():
    d = SG[SG.emotion == e].sort_values("lag"); ex = d.observed - d.sur_mean; out = (d.observed > d.hi) | (d.observed < d.lo)
    axB.plot(d.lag, ex, ls, color=c, lw=1.4); axB.scatter(d.lag[out], ex[out], s=9, color=c, zorder=3)
    axB.text(d.lag.iloc[-1] + 4, ex.iloc[-1], e, fontsize=6, color=INK, va="center")
axB.axhline(0, color=MUTED, lw=.7, ls=":"); axB.axvline(0, color=INK, lw=.6, ls="--"); axB.set_xlim(-125, 165)
axB.set_xticks([-120, -60, 0, 60, 120]); axB.tick_params(labelsize=6); axB.set_xlabel("seconds from event onset", fontsize=6.6); axB.set_ylabel("observed − surrogate events (z)", fontsize=6.6)
axB.set_title("B. Emotions around reorganization events", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
axB.text(-120, axB.get_ylim()[1] * .92, "dots: outside surrogate 95 % band", fontsize=5.4, color=MUTED)
# --- C
KINDS = [("agreement", "agreement ('fica combinado')"), ("commitment", "commitment ('eu faço')"), ("deadline", "deadline / assignment")]
yc = np.arange(3)[::-1]
for yy, (k, lab) in zip(yc, KINDS):
    d = DF[DF.kind == k].set_index("state"); n = d.n.sum(); exp_share = (d.n / n) / d.ratio; exp_share = exp_share / exp_share.sum()
    p = chisquare(d.n.to_numpy(), f_exp=exp_share.to_numpy() * n).pvalue
    for s_, mk, c, off in [("F1", "o", INK, .12), ("F2", "s", BLUE, -.12)]:
        axC.scatter(d.ratio[s_], yy + off, marker=mk, s=24, facecolor=c if p < .05 else "white", edgecolor=c, lw=.9, zorder=3)
    axC.text(1.62, yy, f"n = {n}", fontsize=5.6, color=MUTED, va="center")
axC.axvline(1, color=MUTED, lw=.7, ls=":"); axC.set_yticks(yc); axC.set_yticklabels([l for _, l in KINDS], fontsize=6.4); axC.set_xlim(.4, 1.8); axC.grid(axis="y", visible=False)
axC.set_xlabel("share in floor state / share of all utterances", fontsize=6.4); axC.tick_params(axis="x", labelsize=6)
axC.scatter([], [], marker="o", color=INK, label="single-speaker floor (F1)"); axC.scatter([], [], marker="s", color=BLUE, label="collaborative floor (F2)")
axC.legend(fontsize=5.4, frameon=False, loc="upper center", bbox_to_anchor=(.35, -.2), ncol=1)
axC.set_title("C. Where decisions are spoken", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
# --- D
d = PE[PE.kind == "agreement"].sort_values("bin_start"); x = d.bin_start + 7.5
axD.fill_between(x, d.lo, d.hi, color="#d9dee4", step="mid", label="surrogate events, 95 %")
axD.bar(x, d.observed, width=12, color=[BLUE if (o > h) else "#9fb6d6" for o, h in zip(d.observed, d.hi)], zorder=3, label="observed")
axD.axhline(1, color=MUTED, lw=.7, ls=":"); axD.axvline(0, color=INK, lw=.6, ls="--"); axD.set_xticks([-120, -60, 0, 60, 120]); axD.tick_params(labelsize=6)
axD.set_xlabel("seconds from event onset", fontsize=6.6); axD.set_ylabel("agreement rate / meeting rate", fontsize=6.6)
axD.legend(fontsize=5.4, frameon=False, loc="upper left")
axD.set_title("D. Explicit agreement follows reorganization", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/fig_emotion_decision.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok")
