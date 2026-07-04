"""T1 continued - items 4-12 of the replication ledger. Appends to replication_ledger_part1.csv."""
import glob, os, re, json, unicodedata, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr, wilcoxon, kendalltau, pearsonr, chi2_contingency
from statsmodels.stats.multitest import multipletests
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from team_utils import team_of, TEAMS, NICE

LSH = os.path.expanduser("~/lsh-work")
GM = f"{LSH}/data/metrics_gorman_l8"
OUT = os.path.dirname(__file__) + "/../data"
rows = []


def add(stat_id, description, study, a, b, pooled=None, a_sig=None, b_sig=None, note=""):
    same_dir = None; mag_ratio = None
    if a is not None and b is not None and not (isinstance(a, float) and np.isnan(a)) and not (isinstance(b, float) and np.isnan(b)):
        same_dir = bool(np.sign(a) == np.sign(b)) if (a != 0 and b != 0) else None
        if a != 0 and b != 0:
            mag_ratio = min(abs(a), abs(b)) / max(abs(a), abs(b))
    both_sig = (a_sig is True and b_sig is True) if (a_sig is not None and b_sig is not None) else None
    rows.append(dict(stat_id=stat_id, description=description, study=study,
                      team_a=a, team_b=b, pooled=pooled, team_a_sig=a_sig, team_b_sig=b_sig,
                      same_direction=same_dir, both_significant=both_sig, magnitude_ratio=mag_ratio, note=note))
    print(f"[{stat_id}] A={a}  B={b}  same_dir={same_dir}  note={note}")


def l10_onsets(mid):
    f = f"{LSH}/data/l10_stages/{mid}.json"; tp = f"{LSH}/data/text_startup/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d = json.load(open(f)); tx = pd.read_csv(tp)
    on = pd.to_numeric(tx.onset_seconds, errors="coerce").to_numpy()
    def norm(s):
        s = unicodedata.normalize("NFKD", str(s).lower()); s = "".join(c for c in s if not unicodedata.combining(c))
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()
    nt = [norm(t) for t in tx.text]; seg = []; prev = 0
    for st in d["stages"]:
        q = norm(st["quote"])[:60]; idx = None
        for i in range(prev, len(nt)):
            if q and q in nt[i]: idx = i; break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx = i; break
        if idx is not None: seg.append(float(on[idx])); prev = idx + 1
    return seg


# ============================================================ 4. Taxonomy fingerprint (Study 3): summary
print("\n=== 4. Taxonomy fingerprint (40 categories, per-team lift; full vector saved for T2) ===")
CATS2 = ['arguable','converge','disagree','delim','nonarg','iam1','iam2','iam3','iam4','iam5',
         'disput','cumul','explor','bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin',
         'basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']
CATS1 = ['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans',
         'coop','qset','qprop','directive','commissive','feedback']
def load_cb(folder, suf):
    d = {}
    for f in glob.glob(str(Path(LSH) / folder / f"*_{suf}.json")):
        mid = os.path.basename(f).replace(f"_{suf}.json", "")
        d[mid] = {int(w["t"]): w for w in json.load(open(f))["windows"]}
    return d
c2 = load_cb("data/codebooks2", "passA"); c1 = load_cb("data/codebooks", "passA")
TCRIT = 2.33
lifts_by_team = {t: {cat: [] for cat in CATS2 + CATS1} for t in TEAMS}
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    if mid not in c2: continue
    team = team_of(mid)
    g = pd.read_csv(f); secs = g["second"].to_numpy(); x = g["rmse_g"].to_numpy(float)
    m = np.nanmean(x); sd = np.nanstd(x); mask = x > m + TCRIT * sd; base = ~mask & np.isfinite(x)
    if mask.sum() < 20 or base.sum() < 20: continue
    win = lambda s: int(s // 90 * 90)
    for cat in CATS2 + CATS1:
        cd = c2[mid] if cat in CATS2 else c1.get(mid, {})
        dens = np.array([cd.get(win(s), {}).get(cat, 0) for s in secs], float)
        if not np.isfinite(dens).any() or dens.sum() == 0: continue
        lift = dens[mask].mean() - dens[base].mean()
        lifts_by_team[team][cat].append(lift)
TAX_ROWS = []
for cat in CATS2 + CATS1:
    a_vals = lifts_by_team["startup_a"][cat]; b_vals = lifts_by_team["startup_b"][cat]
    if len(a_vals) < 5 or len(b_vals) < 5: continue
    TAX_ROWS.append(dict(cat=cat, team_a_lift=np.mean(a_vals), team_b_lift=np.mean(b_vals),
                         n_a=len(a_vals), n_b=len(b_vals)))
TAX = pd.DataFrame(TAX_ROWS)
TAX.to_csv(f"{OUT}/taxonomy_lift_by_team.csv", index=False)
n_same = int((np.sign(TAX.team_a_lift) == np.sign(TAX.team_b_lift)).sum())
add("taxonomy_fingerprint_sign_agreement", f"Taxonomy 40-category lift: categories with same sign, Team A vs B "
    f"({n_same}/{len(TAX)}; full 40-category profile correlation in Study 11 T2)", "Study 3",
    a=None, b=None, pooled=n_same / len(TAX), note=f"n_categories={len(TAX)}; full vector -> profile_replication.py")

# ============================================================ 5. 9 floor-measure associations (Study 4)
print("\n=== 5. Floor measures (9), per team, r with %DET ===")
F = pd.read_csv(f"{LSH}/floor_windows.csv")
F["team"] = F.mid.apply(team_of)
MEAS = ["top_share", "net_central", "eig_central", "gini_words", "gini_turns", "inout_asym",
        "turnlen_disp", "n_active", "part_entropy"]
for meas in MEAS:
    per_team = {}
    for team in TEAMS:
        rs = []
        for mid, g in F[F.team == team].groupby("mid"):
            gg = g.dropna(subset=[meas, "det_g"])
            if len(gg) < 8 or gg[meas].std() == 0: continue
            rs.append(pearsonr(gg[meas], gg.det_g)[0])
        rs = [r for r in rs if np.isfinite(r)]
        p = wilcoxon(rs).pvalue if len(rs) >= 5 else np.nan
        per_team[team] = (np.mean(rs) if rs else np.nan, p)
    add(f"floor_{meas}", f"Within-meeting r({meas}, %DET), Wilcoxon across meetings", "Study 4",
        round(per_team["startup_a"][0], 3), round(per_team["startup_b"][0], 3),
        a_sig=bool(per_team["startup_a"][1] < .05), b_sig=bool(per_team["startup_b"][1] < .05))

# ============================================================ 6. Boundary Δentropy/Δ%DET (Study 6)
print("\n=== 6. Topic-boundary perturbation (Δentropy, Δ%DET), per team ===")
EP = pd.read_csv(f"{LSH}/episode_codes.csv")
b_rows = []
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid = os.path.basename(f).replace("_gorman.csv", "")
    g = pd.read_csv(f); sec = g.second.to_numpy(float); ent = g.entropy_g.to_numpy(float); det = g.det_g.to_numpy(float)
    bnds = [b for b in sorted(EP[EP.mid == mid].sec_start.tolist()) if b > sec.min() + 30]
    if not bnds: continue
    near = np.zeros(len(sec), bool)
    for b in bnds: near |= (np.abs(sec - b) <= 30)
    if near.sum() < 5 or (~near).sum() < 5: continue
    b_rows.append(dict(mid=mid, team=team_of(mid), e_b=np.nanmean(ent[near]), e_i=np.nanmean(ent[~near]),
                       d_b=np.nanmean(det[near]), d_i=np.nanmean(det[~near])))
BD = pd.DataFrame(b_rows)
for team in TEAMS:
    sub = BD[BD.team == team]
    de = sub.e_b.mean() - sub.e_i.mean(); dd = sub.d_b.mean() - sub.d_i.mean()
    pe = wilcoxon(sub.e_b, sub.e_i).pvalue; pd_ = wilcoxon(sub.d_b, sub.d_i).pvalue
    if team == "startup_a":
        de_a, dd_a, pe_a, pd_a = de, dd, pe, pd_
    else:
        de_b, dd_b, pe_b, pd_b = de, dd, pe, pd_
add("boundary_delta_entropy", "Δentropy at topic boundary vs interior (±30s)", "Study 6",
    round(de_a, 2), round(de_b, 2), a_sig=bool(pe_a < .05), b_sig=bool(pe_b < .05))
add("boundary_delta_det", "Δ%DET at topic boundary vs interior (±30s)", "Study 6",
    round(dd_a, 2), round(dd_b, 2), a_sig=bool(pd_a < .05), b_sig=bool(pd_b < .05))

# ============================================================ 7. Review-vs-IDS (Study 6, L10)
print("\n=== 7. Review-vs-IDS (entropy, reorg-rate), per team ===")
P = pd.read_csv(f"{LSH}/l10_stage_metrics.csv")
P["team"] = P.mid.apply(team_of)
REVIEW = {"scorecard", "rock_review", "todo"}
for team in TEAMS:
    rec = []
    for mid, g in P[P.team == team].groupby("mid"):
        rv = g[g.stage.isin(REVIEW)]; iv = g[g.stage == "ids"]
        if len(rv) and len(iv):
            rec.append((np.average(rv.entropy, weights=rv.secs), iv.entropy.mean(),
                       np.average(rv.reorg_rate, weights=rv.secs), iv.reorg_rate.mean()))
    R = pd.DataFrame(rec, columns=["rev_e", "ids_e", "rev_r", "ids_r"])
    de = R.rev_e.mean() - R.ids_e.mean(); dr = R.rev_r.mean() - R.ids_r.mean()
    pe = wilcoxon(R.rev_e, R.ids_e).pvalue; pr = wilcoxon(R.rev_r, R.ids_r).pvalue
    if team == "startup_a":
        rde_a, rdr_a, rpe_a, rpr_a, n_a = de, dr, pe, pr, len(R)
    else:
        rde_b, rdr_b, rpe_b, rpr_b, n_b = de, dr, pe, pr, len(R)
add("review_vs_ids_entropy", "Δentropy review-stages minus IDS, per meeting (paired)", "Study 6",
    round(rde_a, 2), round(rde_b, 2), a_sig=bool(rpe_a < .05), b_sig=bool(rpe_b < .05), note=f"n_a={n_a} n_b={n_b}")
add("review_vs_ids_reorgrate", "Δreorg-event-rate review-stages minus IDS, per meeting (paired)", "Study 6",
    round(rdr_a, 2), round(rdr_b, 2), a_sig=bool(rpr_a < .05), b_sig=bool(rpr_b < .05))

# ============================================================ 8. Transition/interior split (Study 7)
print("\n=== 8. Transition/interior split (pct_tr, W=30), per team ===")
DEC = pd.read_csv(f"{LSH}/reorg_decomposition_union_W30.csv")
DEC["team"] = DEC.mid.apply(team_of)
pt_a = DEC[DEC.team == "startup_a"].pct_tr.mean(); pt_b = DEC[DEC.team == "startup_b"].pct_tr.mean()
add("transition_share_w30", "% of reorg events within ±30s of a topic/L10 boundary", "Study 7",
    round(pt_a, 1), round(pt_b, 1))

# ============================================================ 9. Longitudinal taus (Study 5)
print("\n=== 9. Longitudinal taus (entropy, centralization, participation entropy), per team ===")
LP = pd.read_csv(f"{LSH}/longitudinal_panel.csv")
for feat, sid, desc in [("mean_entropy", "long_tau_entropy", "Kendall tau: mean entropy vs week"),
                        ("net_central", "long_tau_netcentral", "Kendall tau: network centralization vs week"),
                        ("part_entropy", "long_tau_partentropy", "Kendall tau: participation entropy vs week")]:
    ta, pa = kendalltau(LP[LP.team == "startup_a"].week, LP[LP.team == "startup_a"][feat])
    tb, pb = kendalltau(LP[LP.team == "startup_b"].week, LP[LP.team == "startup_b"][feat])
    add(sid, desc, "Study 5", round(ta, 3), round(tb, 3), a_sig=bool(pa < .05), b_sig=bool(pb < .05))

# ============================================================ 10. Baseline-vs-excursion (Study 7)
print("\n=== 10. Baseline-vs-excursion decomposition taus, per team ===")
DEP = pd.read_csv(f"{LSH}/reorg_depth_longitudinal_panel.csv")
for feat, sid, desc in [("base_ent", "s7_tau_baseline", "Kendall tau: baseline (resting) entropy vs week"),
                        ("BORDER_ent_exc", "s7_tau_excursion", "Kendall tau: border-event EXCURSION above baseline vs week")]:
    sub_a = DEP[DEP.team == "startup_a"].dropna(subset=[feat]); sub_b = DEP[DEP.team == "startup_b"].dropna(subset=[feat])
    ta, pa = kendalltau(sub_a.week, sub_a[feat]); tb, pb = kendalltau(sub_b.week, sub_b[feat])
    add(sid, desc, "Study 7", round(ta, 3), round(tb, 3), a_sig=bool(pa < .05), b_sig=bool(pb < .05))

# ============================================================ 11. S9 facilitator items
print("\n=== 11. Study 9 facilitator/initiator items, per team ===")
EV9 = pd.read_csv(f"{LSH}/study9_initiators/data/events_initiators.csv")
LIFT9 = pd.read_csv(f"{LSH}/study9_initiators/data/initiation_lift.csv")
STAB9 = pd.read_csv(f"{LSH}/study9_initiators/data/stability_halves.csv")
FSW9 = pd.read_csv(f"{LSH}/study9_initiators/data/facilitator_share_vs_week.csv")

# 11a. facilitator initiation share vs talk-time-weighted permutation null, per team
TT9 = pd.read_csv(f"{LSH}/study9_initiators/data/talk_time_share.csv")
rng = np.random.default_rng(11)
for team in TEAMS:
    sub = EV9[(EV9.team == team)].dropna(subset=["init_primary"])
    obs = (sub.init_primary == sub.facilitator).mean()
    tt_by_mid = {mid: g.set_index("member").talk_share.to_dict() for mid, g in TT9.groupby("mid") if mid in sub.mid.unique()}
    null_shares = []
    for _ in range(1000):
        draws = []
        for mid, g in sub.groupby("mid"):
            shares = tt_by_mid.get(mid, {}); members = list(shares.keys())
            if not members: continue
            p = np.array([shares[m] for m in members]); p = p / p.sum()
            fac = g.facilitator.iloc[0]
            picks = rng.choice(members, size=len(g), p=p)
            draws.extend((picks == fac).tolist())
        null_shares.append(np.mean(draws))
    null_shares = np.array(null_shares)
    p_perm = 2 * min(np.mean(null_shares >= obs), np.mean(null_shares <= obs))
    if team == "startup_a":
        obs_a, null_a, p_a = obs, null_shares.mean(), p_perm
    else:
        obs_b, null_b, p_b = obs, null_shares.mean(), p_perm
add("facilitator_init_share_vs_null", "Facilitator-initiated share (observed) vs talk-time-weighted permutation null mean", "Study 9",
    round(obs_a - null_a, 3), round(obs_b - null_b, 3),
    a_sig=bool(p_a < .05), b_sig=bool(p_b < .05),
    note=f"A: obs={obs_a:.3f} null={null_a:.3f} p={p_a:.3f}; B: obs={obs_b:.3f} null={null_b:.3f} p={p_b:.3f} "
         f"(both n.s. = no facilitator initiation premium in EITHER team, the ledger-level replication)")

# 11b. quiet-member initiation lift, per team (S5 = quietest member by talk share)
q_lifts = {}
for team in TEAMS:
    sub = LIFT9[(LIFT9.team == team) & (LIFT9.definition == "init_primary")]
    quiet = sub.loc[sub.talk_share.idxmin()]
    q_lifts[team] = quiet.lift
add("quiet_member_init_lift", "Initiation lift of the least-talkative member (init_primary)", "Study 9",
    round(q_lifts["startup_a"], 3), round(q_lifts["startup_b"], 3),
    note="both >1 = quietest member over-initiates relative to talk-time in both teams")

# 11c. initiator-rank stability (Spearman rho, halves), per team
for team in TEAMS:
    sub = STAB9[(STAB9.team == team) & (STAB9.definition == "init_primary")]
    val = sub.rho.iloc[0] if len(sub) else np.nan
    if team == "startup_a": stab_a = val
    else: stab_b = val
add("initiator_rank_stability", "Spearman rho, member initiation ranks first-half vs second-half (init_primary)", "Study 9",
    round(stab_a, 2), round(stab_b, 2),
    note="NON-REPLICATION candidate: stability may differ sharply by team (see RESULTS.md)")

# 11d. longitudinal tau of facilitator initiation share, per team (KNOWN non-replication)
for team in TEAMS:
    sub = FSW9[(FSW9.team == team) & (FSW9.definition == "init_primary")]
    val_t = sub.tau.iloc[0]; val_p = sub.p.iloc[0]
    if team == "startup_a": fac_tau_a, fac_p_a = val_t, val_p
    else: fac_tau_b, fac_p_b = val_t, val_p
add("facilitator_share_vs_week_tau", "Kendall tau: facilitator-initiated share vs week (init_primary)", "Study 9",
    round(fac_tau_a, 3), round(fac_tau_b, 3), a_sig=bool(fac_p_a < .05), b_sig=bool(fac_p_b < .05),
    note="FLAGGED NON-REPLICATION: significant in Team B only (p=.02); Team A n.s. (p=.34). "
         "Not read as evidence for/against P5 (facilitator is external, shared across teams) - see RESULTS.md.")

# ============================================================ 12. S8 outcome null
print("\n=== 12. Study 8 baseline_entropy -> issue_resolution_rate, per team (documented null) ===")
PRED8 = pd.read_csv(f"{LSH}/study8_outcomes/data/predictors_per_meeting.csv")
OUT8 = pd.read_csv(f"{LSH}/study8_outcomes/data/outcomes_per_meeting.csv")
D8 = PRED8.merge(OUT8[["mid", "issue_resolution_rate_same_meeting"]], on="mid", how="inner")
for team in TEAMS:
    sub = D8[D8.team == team].dropna(subset=["baseline_entropy", "issue_resolution_rate_same_meeting"])
    r, p = spearmanr(sub.baseline_entropy, sub.issue_resolution_rate_same_meeting)
    if team == "startup_a": r_a, p_a8, n_a8 = r, p, len(sub)
    else: r_b, p_b8, n_b8 = r, p, len(sub)
add("s8_baseline_entropy_vs_issue_resolution", "Spearman rho: baseline_entropy -> issue_resolution_rate (Study 8)", "Study 8",
    round(r_a, 3), round(r_b, 3), a_sig=bool(p_a8 < .05), b_sig=bool(p_b8 < .05),
    note=f"DOCUMENTED NULL (pooled q=.223, did not survive FDR in Study 8): A n={n_a8} p={p_a8:.3f}; "
         f"B n={n_b8} p={p_b8:.3f}. Included per-team for completeness of the ledger, not as a new claim.")

# ============================================================ merge with part 1 and write final ledger
P1 = pd.read_csv(f"{OUT}/replication_ledger_part1.csv")
P2 = pd.DataFrame(rows)
LEDGER = pd.concat([P1, P2], ignore_index=True)
LEDGER.to_csv(f"{OUT}/replication_ledger.csv", index=False)
print(f"\nwrote {OUT}/replication_ledger.csv ({len(LEDGER)} rows total)")
print(f"same_direction: {LEDGER.same_direction.sum()}/{LEDGER.same_direction.notna().sum()} "
      f"(NA={LEDGER.same_direction.isna().sum()})")
