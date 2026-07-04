"""T2 - Simple discriminability check: event-pre vs matched-baseline, leave-one-meeting-out CV.

Two models, reported side by side (important honesty split):
  FULL       - all 6 features, including entropy_slope/det_slope. These two are mechanically expected
               to show a precursor pattern (a window ending just before an entropy peak / %DET valley
               will tend to show a rising/falling local trend by construction of approaching an
               extremum), so a high FULL-model AUC partly reflects the detector's own trajectory being
               self-predictive - not surprising, and not the interesting claim.
  BEHAVIORAL - only switch_rate, turnlen_trend, question_density, gap_trend: turn-taking/text features
               with no direct mechanical tie to how entropy_g/det_g/rmse_g are computed. This is the
               genuinely informative test for Wiltshire's real-time-support framing: can an early-warning
               signal be read off observable talk behavior alone, without first computing the reorg
               metric.

Leave-one-meeting-out CV (34 folds). ANTI-LEAKAGE RULES (see RESULTS.md for the full audit):
  1. Features use only [-W,0)s before the event/baseline pseudo-onset - nothing at or after.
  2. The reorg-event threshold (mean+2.33SD of RMSE) is computed per meeting from that meeting's own
     RMSE series only (established convention throughout this program) - it never pools across
     meetings, so it cannot leak between folds by construction.
  3. Standardization is done WITHIN each meeting independently (train and held-out fold alike), using
     only that meeting's own event+baseline rows - no cross-meeting statistic is used for scaling.
  4. The held-out meeting contributes ZERO rows to model fitting in its own fold.
Logistic regression with a single fixed regularization default (C=1.0, no tuning/search)."""
import os
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve

BASE = os.path.dirname(__file__) + "/.."
D = pd.read_csv(f"{BASE}/data/preevent_features.csv")
FULL_FEATS = ["entropy_slope", "det_slope", "switch_rate", "turnlen_trend", "question_density", "gap_trend"]
BEHAV_FEATS = ["switch_rate", "turnlen_trend", "question_density", "gap_trend"]
rng = np.random.default_rng(10)


def zscore_within_meeting(df, feats):
    out = df.copy()
    for mid, g in df.groupby("mid"):
        for f in feats:
            mu, sd = g[f].mean(), g[f].std()
            idx = g.index
            out.loc[idx, f] = (g[f] - mu) / sd if sd and sd > 0 else 0.0
    return out


def lomo_cv(feats, label):
    Dz = zscore_within_meeting(D.dropna(subset=feats + ["label"]).copy(), feats)
    mids = Dz.mid.unique()
    preds = pd.Series(index=Dz.index, dtype=float)
    for held in mids:
        train = Dz[Dz.mid != held]
        test = Dz[Dz.mid == held]
        if test.label.nunique() < 2 or train.label.nunique() < 2:
            continue  # can't evaluate / can't train
        clf = LogisticRegression(C=1.0, max_iter=1000)
        clf.fit(train[feats], train.label)
        p = clf.predict_proba(test[feats])[:, 1]
        preds.loc[test.index] = p
    valid = preds.notna()
    y = Dz.loc[valid, "label"]; p = preds[valid]
    auc = roc_auc_score(y, p)
    # cluster (meeting) bootstrap CI
    boot = []
    used_mids = Dz.loc[valid, "mid"].unique()
    for _ in range(2000):
        samp_mids = rng.choice(used_mids, size=len(used_mids), replace=True)
        idx = np.concatenate([Dz.loc[valid & (Dz.mid == m)].index.to_numpy() for m in samp_mids])
        yb, pb = Dz.loc[idx, "label"], preds.loc[idx]
        if yb.nunique() < 2:
            continue
        boot.append(roc_auc_score(yb, pb))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    fpr, tpr, _ = roc_curve(y, p)
    print(f"{label:12s} (features={feats}): pooled AUC={auc:.3f}  95% CI(meeting-bootstrap)=[{lo:.3f},{hi:.3f}]  "
          f"n_rows={valid.sum()}  n_meetings={Dz.mid.nunique()}")
    return dict(label=label, auc=auc, ci_lo=lo, ci_hi=hi, n_rows=int(valid.sum()),
                n_meetings=int(Dz.mid.nunique())), (fpr, tpr), (y.to_numpy(), p.to_numpy())


print("=" * 90, "\nT2 - Leave-one-meeting-out CV discriminability (event-pre vs matched baseline)\n" + "=" * 90)
res_full, roc_full, yp_full = lomo_cv(FULL_FEATS, "FULL")
res_behav, roc_behav, yp_behav = lomo_cv(BEHAV_FEATS, "BEHAVIORAL")

RES = pd.DataFrame([res_full, res_behav])
RES.to_csv(f"{BASE}/data/cv_auc_results.csv", index=False)
np.savez(f"{BASE}/data/roc_curves.npz", fpr_full=roc_full[0], tpr_full=roc_full[1],
         fpr_behav=roc_behav[0], tpr_behav=roc_behav[1])
print("\nwrote cv_auc_results.csv, roc_curves.npz")

# per-feature single-predictor AUC, for interpretability (which behavioral feature carries the signal)
print("\n--- single-feature AUCs (behavioral features only, LOMO-CV) ---")
single_rows = []
for f in BEHAV_FEATS:
    res, _, _ = lomo_cv([f], f)
    single_rows.append(dict(feature=f, auc=res["auc"], ci_lo=res["ci_lo"], ci_hi=res["ci_hi"]))
pd.DataFrame(single_rows).to_csv(f"{BASE}/data/single_feature_auc.csv", index=False)
