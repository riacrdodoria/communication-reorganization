"""Composite Figure 1 — Computational structure of communication reorganization (Study 1; tests P1).
Story: naturalistic reorganization is real - the metric is faithful, the dynamic is a graded
continuum (not two regimes), and its excursions are more frequent than turn-preserving chance.
Panel A reuses the per-meeting LSH-vs-standard correlation distribution (Study 1 logic).
Panel B is a new panel: pooled entropy distribution + Gaussian overlay + Sarle BC, with an inset
comparing %DET saturation at L_min=2 (old/artefact) vs L_min=8 (current) - this inset was an
explicit user decision (not the house default of "unimodality alone").
Panel C reuses the supra-autoregressive surrogate comparison (Study 2 logic).
Panel D is a new panel (added in response to reviewer feedback asking for an entropy+%DET time
series): a representative ~25-minute slice of one meeting showing both metrics together with
reorganization event onsets marked, run via `_build_fig1_panel_d_data.py`.
No source figure script (fig_paper_S1.py / fig_paper_S2.py) is modified; this script independently
recomputes/reuses the same underlying data."""
import glob, os, sys
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, skew, kurtosis, norm
sys.path.insert(0, os.path.expanduser("~/lsh-work"))
import gorman_reimpl as gr
import paper_style as ps
ps.setup()

L = os.path.expanduser("~/lsh-work")
GM = f"{L}/data/metrics_gorman_l8"
HZ = 2; WIN = 60 * HZ; STEP = HZ


def winent(state, nsp):
    denom = np.log2(2 ** nsp) if nsp > 0 else 1
    out = []
    for a in range(0, len(state) - WIN, STEP):
        seg = state[a:a + WIN]; _, c = np.unique(seg, return_counts=True); p = c / c.sum()
        out.append(-(p * np.log2(p)).sum() / denom * 100 if denom > 0 else 0)
    return np.array(out)


# ============================================================ Panel A data (Study 1 logic)
rows = []
for f in sorted(glob.glob(f"{L}/data/text_startup/*_transcript.csv")):
    mid = os.path.basename(f).replace("_transcript.csv", "")
    try:
        df = pd.read_csv(f); std, nsp = gr.build_states(df)
    except Exception:
        continue
    if nsp < 2 or len(std) < WIN + 10:
        continue
    lsh = std.copy(); last = 0
    for i in range(len(lsh)):
        if lsh[i] == 0: lsh[i] = last
        else: last = lsh[i]
    es = winent(std, nsp); el = winent(lsh, nsp); n = min(len(es), len(el))
    if n < 30: continue
    rows.append(dict(mid=mid, r=pearsonr(es[:n], el[:n])[0]))
R = pd.DataFrame(rows)

# ============================================================ Panel B data (Study 2 logic + Lmin inset)
ent = []
for f in glob.glob(f"{GM}/*_gorman.csv"):
    g = pd.read_csv(f); ent.append(g.entropy_g.to_numpy(float))
E = np.concatenate(ent); E = E[np.isfinite(E)]
# Sarle BC = (g1^2+1) / (excess_kurtosis + 3(n-1)^2/((n-2)(n-3))); fixed 2026-09-05 (Pearson kurtosis had been used, inflating the denominator by 3)
g1 = skew(E); k = kurtosis(E); n = len(E)
BC = (g1 ** 2 + 1) / (k + (3 * (n - 1) ** 2) / ((n - 2) * (n - 3)))
LM = pd.read_csv(os.path.dirname(__file__) + "/_cache_lmin_det.csv")

# ============================================================ Panel C data (Study 2 logic)
# 2026-09-05: read the L8 surrogate results written by surrogate_validation.py (units: %MaxEnt); the earlier
# hardcoded 0.405/0.190 came from the retired 1 Hz raw-bits pipeline.
_sv=pd.read_csv(f"{L}/surrogate_validation_results.csv").iloc[0]
obs=float(_sv.obs_sd); ar=(float(_sv.AR1_sd_mean),float(_sv.AR1_sd_lo),float(_sv.AR1_sd_hi)); var=(float(_sv.VAR1_sd_mean),float(_sv.VAR1_sd_lo),float(_sv.VAR1_sd_hi))
_ratio=obs/ar[0]
# 2026-10-30: run-order shuffle null (state totals and run lengths kept = turn-length mix kept), 200 surrogate corpora,
# from study13_metric_extensions/runshuffle_study1.py
_rs=pd.read_csv(f"{L}/study13_metric_extensions/results/runshuffle_study1.csv", keep_default_na=False); _o=_rs[_rs.kind=="observed"].iloc[0]; _n=_rs[_rs.kind=="null"]
def _ratio_row(col):
    m=_n[col].mean(); lo,hi=np.percentile(_n[col],[2.5,97.5]); return _o[col]/m, lo/m, hi/m
RS_amp=_ratio_row("sd_excursion"); RS_n=_ratio_row("n_peaks")

# ============================================================ Panel D data (new: representative
# meeting entropy + %DET time series with reorganization events marked)
TS = pd.read_csv(os.path.dirname(__file__) + "/_cache_fig1_timeseries.csv")
EV = pd.read_csv(os.path.dirname(__file__) + "/_cache_fig1_timeseries_events.csv")

# ============================================================ Layout: 2 rows (A|B|C top, D bottom
# spanning full width), ~7.0 x 5.0 in
fig = plt.figure(figsize=(7.0, 5.0))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 0.85], hspace=.62, wspace=.55)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1]); axC = fig.add_subplot(gs[0, 2])
axD = fig.add_subplot(gs[1, :])

# --- A: substrate validity ---
rng = np.random.default_rng(0); jit = rng.uniform(-.08, .08, len(R))
axA.scatter(jit, R.r, s=20, color=ps.COORD, alpha=.8, edgecolor="white", lw=.4, zorder=3)
axA.boxplot(R.r, positions=[0], widths=.34, vert=True, showfliers=False,
            medianprops=dict(color=ps.INK, lw=1.3), boxprops=dict(color=ps.NEUTRAL),
            whiskerprops=dict(color=ps.NEUTRAL), capprops=dict(color=ps.NEUTRAL))
axA.set_xticks([]); axA.set_xlim(-.5, .5); axA.set_ylim(min(.78, R.r.min() - .02), 1.0)
axA.set_ylabel("within-meeting r\n(LSH-WD vs LSH-filled entropy)", fontsize=8)
axA.set_title("A. Substrate validity", loc="left", fontsize=9, fontweight="bold", color=ps.COORD)
axA.text(.5, .04, f"median r = {R.r.median():.2f}\n(all meetings ≥ {R.r.min():.2f})",
          transform=axA.transAxes, ha="center", va="bottom", fontsize=6.6, color=ps.INK,
          bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1", lw=.6))

# --- B: continuum, not two regimes (with Lmin inset) ---
xs = np.linspace(E.min(), E.max(), 200)
axB.hist(E, bins=50, density=True, color=ps.COORD, alpha=.55, edgecolor="white", lw=.2, zorder=2)
axB.plot(xs, norm.pdf(xs, E.mean(), E.std()), color=ps.INK, lw=1.4, zorder=3, label="Gaussian fit")
axB.set_xlabel("team-state entropy (%MaxEnt)", fontsize=7.6)
axB.set_ylabel("density", fontsize=8)
axB.set_title("B. Continuum\n(not two regimes)", loc="left", fontsize=9, fontweight="bold", color=ps.COORD)
axB.text(.03, .97, f"BC={BC:.2f} (<0.555 = unimodal)", transform=axB.transAxes, ha="left", va="top",
          fontsize=6.4, color=ps.INK, bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1", lw=.6))
# inset: %DET saturation, Lmin=2 (old) vs Lmin=8 (current) - simple % >=95 bar comparison
# (clearer than overlapping histograms at this small size)
axIns = axB.inset_axes([0.53, 0.42, 0.44, 0.34])
pct2 = 100 * (LM.det_lmin2 >= 95).mean(); pct8 = 100 * (LM.det_lmin8 >= 95).mean()
axIns.bar([0, 1], [pct2, pct8], color=[ps.DELIB, ps.COORD], width=.6, zorder=3)
axIns.text(0, pct2 + 5, f"{pct2:.0f}%", ha="center", fontsize=5.6, fontweight="bold")
axIns.text(1, pct8 + 5, f"{pct8:.0f}%", ha="center", fontsize=5.6, fontweight="bold")
axIns.set_xticks([0, 1]); axIns.set_xticklabels(["L_min=2\n(old)", "L_min=8\n(now)"], fontsize=5.2)
axIns.set_ylim(0, 112); axIns.set_yticks([]); axIns.tick_params(length=2)
axIns.set_title("windows ≥95% DET", fontsize=5.4, pad=1.5)

# --- C: amplitude vs three nulls, frequency vs the turn-preserving null (ratio observed / null mean) ---
labs=["size\nAR(1)","size\nVAR(1)","size\nshuffle","count\nshuffle"]
vals=[obs/ar[0], obs/var[0], RS_amp[0], RS_n[0]]
nlo=[ar[1]/ar[0], var[1]/var[0], RS_amp[1], RS_n[1]]; nhi=[ar[2]/ar[0], var[2]/var[0], RS_amp[2], RS_n[2]]
xc=np.arange(4)
for i in xc:
    axC.plot([i,i],[nlo[i],nhi[i]],color="#9aa5b1",lw=5,solid_capstyle="butt",zorder=2)
    beyond = vals[i]>nhi[i]
    axC.scatter(i,vals[i],s=34,color=ps.DELIB if beyond else ps.NEUTRAL,edgecolor="white",lw=.5,zorder=3)
    axC.text(i,vals[i]+.1,f"{vals[i]:.2f}×",fontsize=6.2,ha="center",va="bottom",color=ps.INK)
axC.axhline(1,color=ps.INK,lw=.7,ls=":")
axC.set_xticks(xc); axC.set_xticklabels(labs,fontsize=6.4); axC.set_xlim(-.5,3.5); axC.set_ylim(0.5,2.7)
axC.set_ylabel("observed / null mean\n(grey bar = null 95% interval)",fontsize=7.2)
axC.set_title("C. Excursions: more frequent,\nnot larger, than chance",loc="left",fontsize=9,fontweight="bold",color=ps.COORD)

# --- D: representative meeting, entropy + %DET time series, events marked ---
tmin = (TS.second - TS.second.min()) / 60
axD.plot(tmin, TS.entropy_g, color=ps.COORD, lw=1.3, label="entropy (%MaxEnt)")
axD2 = axD.twinx()
axD2.plot(tmin, TS.det_g, color=ps.DELIB, lw=1.3, label="%DET")
for e in EV.event_onset_s:
    axD.axvline((e - TS.second.min()) / 60, color=ps.INK, lw=.8, ls="--", alpha=.6, zorder=1)
axD.set_xlabel("meeting time (min)", fontsize=8)
axD.set_ylabel("entropy (%MaxEnt)", fontsize=8, color=ps.COORD)
axD2.set_ylabel("%DET", fontsize=8, color=ps.DELIB)
axD.tick_params(axis="y", labelcolor=ps.COORD, labelsize=7.5)
axD2.tick_params(axis="y", labelcolor=ps.DELIB, labelsize=7.5)
axD.tick_params(axis="x", labelsize=7.5)
axD.set_title("D. Representative meeting: entropy rises and %DET falls together at reorganization events",
              loc="left", fontsize=9, fontweight="bold", color=ps.COORD)
axD.text(.01, .04, "dashed lines = reorganization event onsets\n(RMSE > mean+2.33 SD); entropy rises, "
         "%DET falls, in step", transform=axD.transAxes, fontsize=6.4, va="bottom", ha="left", color=ps.INK,
         bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1", lw=.6))

fig.suptitle("Figure 1 — Computational structure of communication reorganization", fontsize=10.5,
             fontweight="bold", x=.01, ha="left", y=1.04)
ps.caption(fig, "Figure 1. Computational structure of communication reorganization (Study 1). (A) "
    "Within-meeting correlation between the word-timed (LSH-WD) team-state series and its "
    "pure-LSH counterpart, across 34 meetings (median r = .94; all ≥ .90). (B) Distribution of "
    "team-state entropy across pooled meeting-seconds, with Gaussian fit overlay; the Sarle bimodality "
    f"coefficient (BC = {BC:.2f}) falls well below the bimodality threshold (0.555) - a single graded continuum. "
    "Inset: the earlier apparent bimodality was a %DET-saturation artefact at L_min=2 (92% of windows "
    "≥95% DET), resolved by the current L_min=8 correction (28% ≥95%). (C) Entropy excursions at peaks, observed relative to the null mean: "
    "the amplitude (SD of the pre-to-post change) exceeds AR(1) and VAR(1) surrogates but not the run-order shuffle that keeps "
    "the turn-length mix; the number of excursions exceeds the run-order shuffle (200 surrogate corpora). "
    "Size = SD of the pre-to-post entropy change at peaks; count = number of peaks; grey bars = null 95% intervals. (D) A representative ~25-minute "
    "slice of one meeting: entropy (teal) and %DET (orange) move in step, with entropy rising and %DET "
    "falling at each reorganization event onset (dashed lines).", y=-0.17, fontsize=6.4)
fig.tight_layout(rect=[0, 0.1, 1, 0.95])
for ext in ("png", "pdf"):
    fig.savefig(f"{os.path.dirname(__file__)}/fig1_computational_structure.{ext}", bbox_inches="tight",
                facecolor="white", dpi=600 if ext == "png" else None)
print("wrote fig1_computational_structure.{png,pdf}")
print(f"median r={R.r.median():.3f}  BC={BC:.3f}  Lmin2 sat%={100*(LM.det_lmin2>=95).mean():.0f}  "
      f"Lmin8 sat%={100*(LM.det_lmin8>=95).mean():.0f}")
