"""T3 - Facilitator vs members.
- Permutation test: is the facilitator's initiated-event share above what talk-time share alone predicts?
  Null: shuffle which member "counts" as initiator for each event, drawing (per meeting) proportional
  to that member's talk-time share in that meeting; 1000 seeded runs; compare observed facilitator share to
  the null distribution.
- Event class x initiator-type (facilitator vs member): chi-square / Fisher (2x3 -> use chi-square with a
  Monte Carlo p if any expected cell < 5)."""
import os
import numpy as np, pandas as pd
from scipy.stats import chi2_contingency

BASE = os.path.expanduser("~/lsh-work/study9_initiators")
D = pd.read_csv(f"{BASE}/data/events_initiators.csv")
TT = pd.read_csv(f"{BASE}/data/talk_time_share.csv")
DEFS = ["init_primary", "init_floor", "init_question"]
rng = np.random.default_rng(9)
NPERM = 1000

print("=" * 90, "\nPART A - Permutation test: facilitator-initiated share vs talk-time-weighted null\n" + "=" * 90)
perm_rows = []
for defn in DEFS:
    sub = D.dropna(subset=[defn]).copy()
    obs_share = (sub[defn] == sub.facilitator).mean()
    # build per-meeting talk-share lookup for the facilitator
    null_shares = []
    tt_by_mid = {mid: g.set_index("member").talk_share.to_dict() for mid, g in TT.groupby("mid")}
    for _ in range(NPERM):
        draws = []
        for mid, g in sub.groupby("mid"):
            shares = tt_by_mid.get(mid, {})
            members = list(shares.keys())
            if not members: continue
            p = np.array([shares[m] for m in members]); p = p / p.sum()
            facilitator_m = g.facilitator.iloc[0]
            picks = rng.choice(members, size=len(g), p=p)
            draws.extend((picks == facilitator_m).tolist())
        null_shares.append(np.mean(draws))
    null_shares = np.array(null_shares)
    # Phipson & Smyth (2010): p = (b+1)/(N+1), so p is never reported as 0 (minimum 1/(N+1))
    b = int(np.sum(null_shares >= obs_share)) if obs_share >= null_shares.mean() else int(np.sum(null_shares <= obs_share))
    p_perm = (b + 1) / (len(null_shares) + 1)
    p_two = min(1.0, 2 * p_perm)
    perm_rows.append(dict(definition=defn, n=len(sub), observed_facilitator_share=obs_share,
                           null_mean=null_shares.mean(), null_sd=null_shares.std(),
                           null_ci_lo=np.percentile(null_shares, 2.5), null_ci_hi=np.percentile(null_shares, 97.5),
                           p_perm_two_sided=p_two))
    print(f"{defn:14s}: observed facilitator share={obs_share:.3f}  talk-time-weighted null={null_shares.mean():.3f} "
          f"+/-{null_shares.std():.3f} (95% null CI [{np.percentile(null_shares,2.5):.3f},{np.percentile(null_shares,97.5):.3f}])"
          f"  {('p<' + format(2/NPERM, '.3f')) if p_two < 2/NPERM else 'p=' + format(p_two, '.3f')}  seed=9, {NPERM} runs")
PERM = pd.DataFrame(perm_rows)
PERM.to_csv(f"{BASE}/data/permutation_facilitator_share.csv", index=False)

print("\n" + "=" * 90, "\nPART B - Event class x initiator-type (facilitator vs member)\n" + "=" * 90)
class_rows = []
for defn in DEFS:
    sub = D.dropna(subset=[defn]).copy()
    sub["init_type"] = np.where(sub[defn] == sub.facilitator, "facilitator", "member")
    tab = pd.crosstab(sub.event_class, sub.init_type)
    chi2, p, dof, exp = chi2_contingency(tab)
    print(f"\n--- {defn} ---")
    print(tab)
    print(f"row %:\n{(100*tab.div(tab.sum(1),axis=0)).round(1)}")
    print(f"chi2({dof})={chi2:.2f}  p={p:.4g}  min_expected={exp.min():.1f}")
    class_rows.append(dict(definition=defn, chi2=chi2, dof=dof, p=p, min_expected=exp.min()))
pd.DataFrame(class_rows).to_csv(f"{BASE}/data/class_by_initiator_type.csv", index=False)
print("\nwrote permutation_facilitator_share.csv, class_by_initiator_type.csv")
