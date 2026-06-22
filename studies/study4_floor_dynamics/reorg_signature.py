"""Does the TRIGGER change the reorganization signature? Classify every reorg event as
  TRANSITION   - center within +/-30s of a boundary (topic-episode start U EOS L10 onset)
  INT_HANDOFF  - interior, and the dominant floor-holder changes before->after
  INT_OTHER    - interior, no handoff
and compare the metric magnitude at each event (entropy_g, det_g over +/-10s; rmse peak z).
Per-meeting z-scored to remove meeting baselines, pooled; Kruskal-Wallis + pairwise Mann-Whitney."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
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
    # cluster
    ev=[]; cur=[]
    for s in evsec:
        if cur and s-cur[-1]>8: ev.append(cur);cur=[]
        cur.append(s)
    if cur: ev.append(cur)
    for e in ev:
        c=float(np.mean(e)); trans=any(abs(c-b)<=30 for b in bd)
        m=(sec>=c-10)&(sec<=c+10)
        if m.sum()<3: continue
        if trans: cls="TRANSITION"
        else:
            db=dom(tx,c-30,c); da=dom(tx,c,c+30); cls="INT_HANDOFF" if (db and da and db!=da) else "INT_OTHER"
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
D.to_csv("reorg_signature.csv",index=False)
print("\nwrote reorg_signature.csv")
