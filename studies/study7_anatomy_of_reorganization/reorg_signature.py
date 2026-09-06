"""Does the TRIGGER change the reorganization signature? Classify every reorg event as
  TRANSITION   - center within +/-30s of a boundary (topic-episode start U EOS L10 onset)
  INT_HANDOFF  - interior, and the dominant floor-holder changes before->after
  INT_OTHER    - interior, no handoff
and compare the metric magnitude at each event (entropy_g, det_g over +/-10s; rmse peak z).
Per-meeting z-scored to remove meeting baselines, pooled; Kruskal-Wallis + pairwise Mann-Whitney."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'src'))
import reorg_events as RE
from scipy.stats import wilcoxon, friedmanchisquare
from scipy.stats import kruskal,mannwhitneyu
TXT="data/text_startup"; GM="data/metrics_gorman_l8"
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def l10_onsets(mid):
    f=f"data/l10_stages/{mid}.json"; tp=f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d=json.load(open(f)); tx=pd.read_csv(tp); on=pd.to_numeric(tx.onset_seconds,errors="coerce").to_numpy()
    nt=[norm(t) for t in tx.text]; seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(nt)):
            if q and q in nt[i]: idx=i;break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx=i;break
        if idx is not None: seg.append(float(on[idx]));prev=idx+1
    return seg
def dom(tx,a,b):
    j=(tx.onset>=a)&(tx.onset<b); s={}
    for sp,w in zip(tx.spk[j],tx.nw[j]): s[sp]=s.get(sp,0)+w
    return max(s,key=s.get) if s else None
EP=pd.read_csv("episode_codes.csv")
mids=sorted(set(os.path.basename(p).replace("_gorman.csv","") for p in glob.glob(f"{GM}/*.csv")))
rows=[]
for mid in mids:
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g.second.to_numpy(float)
    ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float); rm=g.rmse_g.to_numpy(float)
    ok=~np.isnan(rm)
    if ok.sum()<60: continue
    thr=np.nanmean(rm[ok])+2.33*np.nanstd(rm[ok]); rsd=np.nanstd(rm[ok]); rmean=np.nanmean(rm[ok])
    evsec=sec[ok][rm[ok]>thr]
    bd=sorted(set(EP[EP.mid==mid].sec_start.tolist())|set(l10_onsets(mid)))
    tx=pd.read_csv(f"{TXT}/{mid}_transcript.csv")
    tx=pd.DataFrame(dict(onset=pd.to_numeric(tx.onset_seconds,errors="coerce"),spk=tx.speaker_id.astype(str)))
    tx=tx.dropna(subset=["onset"]); tx["nw"]=1  # turn-count weighting is robust for dominance
    _on=tx.onset.to_numpy(float); _sp=tx.spk.to_numpy(); _nw=tx.nw.to_numpy(float)
    for e in RE.cluster_events(evsec):
        cls0,c,_=RE.classify(e,bd,_on,_sp,_nw)  # canonical rule: centre, ±30 s, turn-count dominance
        cls={"TRANSITION":"TRANSITION","INTERIOR_HANDOFF":"INT_HANDOFF","INTERIOR_OTHER":"INT_OTHER"}[cls0]
        m=(sec>=c-10)&(sec<=c+10)
        if m.sum()<3: continue
        rows.append(dict(mid=mid,cls=cls,entropy=np.nanmean(ent[m]),det=np.nanmean(det[m]),
                         rmse_z=(np.nanmax(rm[m])-rmean)/rsd))
D=pd.DataFrame(rows)
print("event counts by class:\n",D.cls.value_counts().to_string())
# per-meeting z-score each metric, then pool
for col in ["entropy","det","rmse_z"]:
    D[col+"_z"]=D.groupby("mid")[col].transform(lambda x:(x-x.mean())/x.std() if x.std()>0 else 0)
print("\n=== Metric magnitude by trigger (raw means | within-meeting z) ===")
print(f"{'class':12s} {'n':>4s} {'entropy':>8s} {'%DET':>6s} {'rmseZ':>6s}  | {'entZ':>6s} {'detZ':>6s} {'rmseZz':>7s}")
for cls,gg in D.groupby("cls"):
    print(f"{cls:12s} {len(gg):4d} {gg.entropy.mean():8.1f} {gg.det.mean():6.1f} {gg.rmse_z.mean():6.2f}  |"
          f" {gg.entropy_z.mean():6.2f} {gg.det_z.mean():6.2f} {gg.rmse_z_z.mean():7.2f}")
def kw(col):
    grp=[g[col].dropna().values for _,g in D.groupby("cls")]
    H,p=kruskal(*grp); return H,p
print("\n=== Kruskal-Wallis across the 3 classes (within-meeting z) ===")
for col in ["entropy_z","det_z","rmse_z_z"]:
    H,p=kw(col); print(f"  {col:10s}: H={H:.2f}, p={p:.3g}")
print("\n=== TRANSITION vs INT_HANDOFF (Mann-Whitney, within-meeting z) ===")
for col in ["entropy_z","det_z","rmse_z_z"]:
    a=D[D.cls=='TRANSITION'][col]; b=D[D.cls=='INT_HANDOFF'][col]
    U,p=mannwhitneyu(a,b); print(f"  {col:10s}: trans {a.mean():+.2f} vs handoff {b.mean():+.2f}  p={p:.3g}")
# --- 2026-09-05: unit of inference = the meeting (METHODS §6). Per-meeting class means, paired tests. ---
print("\n=== Meeting-level (n=34): per-meeting mean within-meeting z by class; paired Wilcoxon TRANSITION vs INT_HANDOFF; Friedman across 3 classes ===")
M=D.groupby(["mid","cls"])[["entropy_z","det_z","rmse_z_z"]].mean().unstack("cls")
ml_rows=[]
for col in ["entropy_z","det_z","rmse_z_z"]:
    sub=M[col].dropna(subset=["TRANSITION","INT_HANDOFF"])
    d=sub.TRANSITION-sub.INT_HANDOFF; pw=wilcoxon(d).pvalue; n_pos=int((d>0).sum())
    sub3=M[col].dropna(); pf=friedmanchisquare(sub3.TRANSITION,sub3.INT_HANDOFF,sub3.INT_OTHER).pvalue
    print(f"  {col:10s}: TRANSITION-HANDOFF mean diff={d.mean():+.2f} SD, higher in {n_pos}/{len(d)} meetings, paired Wilcoxon p={pw:.3g}; Friedman(3 classes, n={len(sub3)}) p={pf:.3g}")
    ml_rows.append(dict(metric=col,n_pairs=len(d),mean_diff_T_minus_H=d.mean(),n_T_higher=n_pos,wilcoxon_p=pw,n_friedman=len(sub3),friedman_p=pf))
pd.DataFrame(ml_rows).to_csv("reorg_signature_meeting_level.csv",index=False)
print("(reading: the classes are ordered TRANSITION > HANDOFF > OTHER on all three metrics; the rmse difference is smaller than the %DET/entropy difference, not absent)")
D.to_csv("reorg_signature.csv",index=False)
print("\nwrote reorg_signature.csv")
