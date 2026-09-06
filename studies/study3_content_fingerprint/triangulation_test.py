"""Test: does each coding-free TEXT measure track the reorganization metrics?
Stouffer Z across meetings, within-meeting circular-shift null (like gorman_vs_content), BH-FDR across
measures within each reorg metric.

2026-09-05 revision (AUDIT_REPORT.md, S3 #1/#2/#4): every measure is now ALSO tested after partialling
out turn length AND turns-per-window within meeting (the same control METHODS §7 applies to LSM/LIWC),
because utterance segmentation is the very turn structure the %DET/RMSE detector consumes. Only effects
that survive that control count as content evidence. The BP-LIWC2015 LSM (`liwc_lsm`) and the curated
LSM (`lsm_curated`) are both reported under their own names. The headline cross-check is r(sem_rec, det_g);
the null semantic-%DET cross is reported alongside. This script no longer rewrites the input CSV."""
import numpy as np,pandas as pd
from scipy.stats import norm
df=pd.read_csv("triangulation_windows.csv")
MEAS=["sem_det","sem_rec","coh","nov","word_entropy","ttr","mtld","hapax","lsm_curated","liwc_lsm",
      "turn_len","latency","transition_entropy","n_turns","connective","content_overlap"]
MEAS=[m for m in MEAS if m in df.columns]
LAB={"sem_det":"Semantic %DET (TF-IDF recurrence)","sem_rec":"Semantic %REC",
"coh":"Turn-to-turn coherence","nov":"Novelty (topic-shift)","word_entropy":"Word entropy",
"ttr":"Type-token ratio","mtld":"MTLD lexical diversity","hapax":"Hapax ratio",
"lsm_curated":"LSM (curated function words)","liwc_lsm":"LSM (BP-LIWC2015)","turn_len":"Turn length (words)","latency":"Response latency",
"transition_entropy":"Speaker-transition entropy","n_turns":"Turns per window",
"connective":"Connective density (CohM-PT)","content_overlap":"Content-word overlap (CohM-PT)"}
REORG=["entropy_g","det_g","rmse_g"]
CTRL=["turn_len"]           # primary control (METHODS §7; same as liwc_map.py)
CTRL2=["turn_len","n_turns"] # sensitivity: also turns-per-window (collinear with %DET, r≈-.8; risk of over-adjustment)
NPERM=500
def z(a):
    a=a-np.nanmean(a); s=np.nanstd(a); return a/s if s>0 else None
def resid(v,C):
    """residualize v on the columns of C (with intercept already removed by z-scoring)."""
    b=np.linalg.lstsq(C,v,rcond=None)[0]; return v-C@b
def stouffer(feat,metric,ctrl=None,seed=0):
    rng=np.random.default_rng(seed)  # per-call seed: Z no longer depends on loop order
    zs=[]
    for mid,g in df.groupby("mid"):
        cols=[feat,metric]+([c for c in ctrl if c!=feat] if ctrl else [])
        g=g.dropna(subset=cols); n=len(g)
        if n<8: continue
        zx=z(g[feat].to_numpy(float)); zy=z(g[metric].to_numpy(float))
        if zx is None or zy is None: continue
        if ctrl:
            cs=[z(g[c].to_numpy(float)) for c in ctrl if c!=feat]
            cs=[c for c in cs if c is not None]
            if cs:
                C=np.column_stack(cs); zx=resid(zx,C); zy=resid(zy,C)
        obs=float(zx@zy)/n
        sh=rng.integers(2,n-2,size=NPERM); idx=(np.arange(n)[None,:]-sh[:,None])%n
        nl=(zy[idx]@zx)/n; sd=nl.std()
        if sd>0: zs.append((obs-nl.mean())/sd)
    zs=np.array(zs); return (zs.sum()/np.sqrt(len(zs)) if len(zs) else np.nan), len(zs)
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
star=lambda z:'***' if abs(z)>3.29 else '**' if abs(z)>2.58 else '*' if abs(z)>1.96 else ''
rows=[]
for feat in MEAS:
    r=dict(feat=feat,label=LAB[feat])
    for metric in REORG:
        r[f"Z_{metric}_raw"],r["n_mtg"]=stouffer(feat,metric)
        r[f"Z_{metric}_ctrl"],_=stouffer(feat,metric,ctrl=CTRL)
        r[f"Z_{metric}_ctrl2"],_=stouffer(feat,metric,ctrl=CTRL2)
    rows.append(r)
R=pd.DataFrame(rows)
for metric in REORG:
    for kind in ("raw","ctrl","ctrl2"):
        R[f"q_{metric}_{kind}"]=bh(2*norm.sf(np.abs(R[f"Z_{metric}_{kind}"].fillna(0))))
R["reorgZ_raw"]=(R.Z_entropy_g_raw-R.Z_det_g_raw+R.Z_rmse_g_raw)/np.sqrt(3)
R["reorgZ_ctrl"]=(R.Z_entropy_g_ctrl-R.Z_det_g_ctrl+R.Z_rmse_g_ctrl)/np.sqrt(3)
R["reorgZ_ctrl2"]=(R.Z_entropy_g_ctrl2-R.Z_det_g_ctrl2+R.Z_rmse_g_ctrl2)/np.sqrt(3)
R.to_csv("triangulation_Z.csv",index=False)
print(f"{'measure':34}| {'ENT raw':>8} {'ENT ctrl':>9}| {'%DET raw':>8} {'%DET ctrl':>9}| {'RMSE raw':>8} {'RMSE ctrl':>9}")
print("-"*100)
for _,r in R.iterrows():
    cells=[]
    for metric in REORG:
        cells.append(f"{r[f'Z_{metric}_raw']:>+6.2f}{star(r[f'Z_{metric}_raw']):<2} {r[f'Z_{metric}_ctrl']:>+6.2f}{star(r[f'Z_{metric}_ctrl']):<3}")
    print(f"{r.label[:33]:34}| {cells[0]}| {cells[1]}| {cells[2]}")
print(f"\n(+ = text measure co-varies with HIGHER reorg metric; ctrl = within-meeting partial on {CTRL}; *p<.05 **p<.01 ***p<.001)")
print(f"\nSensitivity (partial on {CTRL2}) — %DET Z:  " + "; ".join(f"{r.label[:22]} {r.Z_det_g_ctrl2:+.1f}" for _,r in R.iterrows()))
surv=R[(R.q_det_g_ctrl<.05)&(~R.feat.isin(CTRL))]
print(f"\nMeasures whose %DET association SURVIVES the turn-length/turn-count control (q<.05): {len(surv)}/{(~R.feat.isin(CTRL)).sum()}")
print("  " + ", ".join(f"{r.label} (Z={r.Z_det_g_ctrl:+.1f})" for _,r in surv.iterrows()))
print(f"Sensitivity survivors (q<.05, %DET, partial on {CTRL2}): {int(((R.q_det_g_ctrl2<.05)&(~R.feat.isin(CTRL2))).sum())}/{int((~R.feat.isin(CTRL2)).sum())}")
# headline crosses (window level, within-meeting z)
def within_r(a_col,b_col):
    zz=[]
    for mid,g in df.groupby("mid"):
        g=g.dropna(subset=[a_col,b_col])
        if len(g)<8: continue
        a=z(g[a_col].to_numpy(float)); b=z(g[b_col].to_numpy(float))
        if a is not None and b is not None: zz.append(np.corrcoef(a,b)[0,1])
    return np.nanmean(zz),len(zz)
r1,n1=within_r("sem_rec","det_g"); r0,n0=within_r("sem_det","det_g")
print(f"\nHEADLINE  mean within-meeting r(semantic recurrence, turn-taking %DET) = {r1:+.3f}  (n={n1} mtgs)  [raw; see ctrl Z above]")
print(f"          mean within-meeting r(semantic %DET, turn-taking %DET)     = {r0:+.3f}  (n={n0} mtgs)  [null]")
print("wrote triangulation_Z.csv (raw and turn-length/turn-count-controlled Stouffer Z, BH q, reorgZ)")
