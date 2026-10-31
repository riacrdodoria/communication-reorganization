"""Figure 4 — What a reorganization event looks like, against events produced by the detection procedure alone.
A: event-anchored statistics, observed relative to surrogate events (20 run-shuffled sets per meeting).
B: event signature of content and language channels (within-meeting z, observed minus surrogate-event mean) at lags
   -120..+120 s; dots mark lags where the observed value lies outside all surrogate sets' 95 % band."""
import os, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import paper_style as ps
BLUE_, ORANGE_ = "#1f6fb4", "#d95f02"
ps.setup(); R = os.path.expanduser("~/lsh-work/study13_metric_extensions/results")
S = pd.read_csv(f"{R}/evnull_stats.csv").set_index("stat"); SG = pd.read_csv(f"{R}/evnull_signature.csv")
LAB = {"agenda_coinc": "agenda transition within ±30 s", "agenda_anticip": "next agenda stage 15–60 s later", "llm_coinc": "LLM topic boundary within ±30 s*",
       "member_q45": "member questions in next 45 s", "open_question": "opening turn is a question", "open_dur": "opening turn duration",
       "floor_coinc": "extended floor turn within ±30 s", "init_fac": "initiated by facilitator", "init_quiet": "initiated by quietest member"}
order = ["member_q45", "open_question", "open_dur", "floor_coinc", "init_fac", "init_quiet"]
CHL = {"topic_entropy_res": "topic mixing", "ret_res": "return to earlier subject", "sem_shift": "semantic shift", "novelty_res": "lexical novelty",
       "question": "questions", "collective": "'a gente / nós'", "lsm_res": "style matching", "ttr_res": "lexical richness"}
fig = plt.figure(figsize=(7.2, 6.6)); gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.45], height_ratios=[1, .75], wspace=.85, hspace=.6)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1]); axC = fig.add_subplot(gs[1, :])
y = np.arange(len(order))[::-1]
for yy, k in zip(y, order):
    r = S.loc[k]; sig = r.p_high < .05 or r.p_low < .05; lo = (r.surrogate_mean - 1.96 * r.surrogate_sd) / r.surrogate_mean; hi = (r.surrogate_mean + 1.96 * r.surrogate_sd) / r.surrogate_mean
    axA.plot([lo, hi], [yy, yy], color="#b9c2cc", lw=5, solid_capstyle="butt", zorder=1)
    axA.scatter(r.ratio, yy, s=30, color=ps.INK if sig else "white", edgecolor=ps.INK, lw=.8, zorder=3)
    axA.text(1.75, yy, f"{r.ratio:.2f}×", va="center", fontsize=6, color=ps.INK)
axA.axvline(1, color=ps.NEUTRAL, ls=":", lw=.8); axA.set_yticks(y); axA.set_yticklabels([LAB[k] for k in order], fontsize=6.2)
axA.set_xlim(.6, 1.9); axA.set_xlabel("observed / surrogate events", fontsize=6.8); axA.grid(axis="y", visible=False)
axA.set_title("A. Who and what opens an event", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD, x=-1.0)
axA.text(-1.0, -.24, "filled = outside all 20 surrogate sets; grey = surrogate ±1.96 SD", fontsize=5.2, color=ps.NEUTRAL, transform=axA.transAxes); axA.tick_params(axis="x", labelsize=6)
chs = list(CHL); lags = sorted(SG.lag.unique()); M = np.array([[SG[(SG.channel == c) & (SG.lag == l)].excess.iloc[0] for l in lags] for c in chs])
cmap = LinearSegmentedColormap.from_list("div", ["#2166ac", "#92c5de", "#f0efec", "#f4a582", "#b2182b"])
axB.imshow(M, aspect="auto", cmap=cmap, norm=TwoSlopeNorm(0, -.3, .3)); axB.grid(False)
for i, c in enumerate(chs):
    for j, l in enumerate(lags):
        r = SG[(SG.channel == c) & (SG.lag == l)].iloc[0]
        if r.observed > r.hi or r.observed < r.lo: axB.scatter(j, i, s=6, color=ps.INK, zorder=3)
axB.set_yticks(range(len(chs))); axB.set_yticklabels([CHL[c] for c in chs], fontsize=6.2)
tick = [j for j, l in enumerate(lags) if l % 60 == 0]; axB.set_xticks(tick); axB.set_xticklabels([f"{lags[j]:+d}" for j in tick], fontsize=6.2)
axB.axvline(lags.index(0), color=ps.INK, lw=.6, ls="--"); axB.set_xlabel("seconds from event onset", fontsize=6.8)
cb = fig.colorbar(axB.images[0], ax=axB, fraction=.04, pad=.02, ticks=[-.3, 0, .3]); cb.ax.set_yticklabels(["−0.3", "0", "+0.3 z"], fontsize=5.6)
axB.set_title("B. Content and language around events\n(observed minus surrogate events)", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)
# --- C: turn-taking and content, moment by moment (34 meetings; bars = mean within-meeting rho, dots = teams) ---
CC = pd.read_csv(f"{R}/channels_crosscorr.csv"); G = pd.read_csv(f"{R}/channels_grid.csv")
sys_import = __import__("sys"); sys_import.path.insert(0, os.path.expanduser("~/lsh-work/study13_metric_extensions/src")); import common as CM
G["F1"] = (G.state == "F1").astype(float); G["F2"] = (G.state == "F2").astype(float)
PAIRS = [("switch", "ret_res", "speaker switching ~ return to earlier subject"), ("switch", "topic_entropy_res", "speaker switching ~ topic mixing"),
         ("det", "ret_res", "%DET ~ return to earlier subject"), ("F1", "ret_res", "single-speaker floor ~ return"), ("switch", "sem_shift", "speaker switching ~ semantic shift"),
         ("F1", "topic_entropy_res", "single-speaker floor ~ topic mixing")]
for i, (a, b, lab) in enumerate(PAIRS):
    r = CC[(CC.a == a) & (CC.b == b)].iloc[0]; axC.barh(i, r.rho, .6, color=BLUE_ if r.rho > 0 else "#8a939e", alpha=.8)
    for t, mk in [("A", "o"), ("B", "s")]:
        v = np.mean([g[[a, b]].dropna().corr(method="spearman").iloc[0, 1] for m, g in G.groupby("mid") if CM.team(m) == t]); axC.scatter(v, i, marker=mk, s=14, color=ps.INK, zorder=3, label=f"Team {t}" if i == 0 else None)
    axC.text(0.42, i, f"{r.same_sign}/{r.n} meetings same sign", va="center", fontsize=5.6, color=ps.NEUTRAL)
axC.axvline(0, color=ps.NEUTRAL, lw=.7); axC.set_yticks(range(len(PAIRS))); axC.set_yticklabels([p[2] for p in PAIRS], fontsize=6.2); axC.invert_yaxis(); axC.set_xlim(-.45, .62)
axC.set_xlabel("mean within-meeting Spearman correlation (5-s grid)", fontsize=6.4); axC.tick_params(axis="x", labelsize=5.8); axC.grid(axis="y", visible=False); axC.legend(fontsize=5.4, frameon=False, loc="upper left", bbox_to_anchor=(0, -.16), ncol=2)
axC.set_title("C. When the floor opens, the group returns to and mixes what is already on the table", loc="left", fontsize=8.6, fontweight="bold", color=ps.COORD)

for ext in ("png", "pdf"): fig.savefig(f"{os.path.dirname(__file__)}/fig4_event_signature.{ext}", bbox_inches="tight", facecolor="white", dpi=600 if ext == "png" else None)
print("ok")
