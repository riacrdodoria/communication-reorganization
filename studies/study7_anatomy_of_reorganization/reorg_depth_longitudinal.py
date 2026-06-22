"""What DOES change over time, if the anatomy doesn't? The INTENSITY/DEPTH of reorganization, border vs
interior. Per meeting, per class (BORDER = within +/-30s of a topic-episode start U EOS L10 onset;
INTERIOR = else), over reorg events (rmse_g peaks > mean+2.33SD), compute depth:
  peak_z   = prominence of the rmse spike, (peak - meeting mean)/SD
  ent_exc  = entropy at event (+/-10s) minus meeting baseline entropy   (higher = deeper)
  det_exc  = %DET at event minus meeting baseline %DET                  (more negative = deeper)
plus the event RATE per class. Kendall tau over weeks (per team n=17 + pooled). Writes
reorg_depth_longitudinal_panel.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import kendalltau
from statsmodels.stats.multitest import multipletests
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(ch for ch in s if not unicodedata.combining(ch))
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
def parse(mid):
    m=re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])",mid); y,mo,d,t=m.groups()
    return int(y)*10000+int(mo)*100+int(d),t
EP=pd.read_csv("episode_codes.csv")
rows=[]
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); sec=g.second.to_numpy(float)
    ent=g.entropy_g.to_numpy(float); det=g.det_g.to_numpy(float); rm=g.rmse_g.to_numpy(float)
    ok=np.isfinite(rm); sec,ent,det,rm=sec[ok],ent[ok],det[ok],rm[ok]
    if len(rm)<60: continue
    rmean,rsd=rm.mean(),rm.std(); peak=rm>rmean+2.33*rsd
    bd=sorted(set(EP[EP.mid==mid].sec_start.tolist())|set(l10_onsets(mid)))
    if not bd: continue
    near=np.zeros(len(sec),bool)
    for b in bd:
        if b>sec.min()+1: near|=(np.abs(sec-b)<=30)
    base=~peak  # meeting baseline (non-event)
    bent,bdet=ent[base].mean(),det[base].mean()
    # cluster events, classify, gather depth
    evidx=np.where(peak)[0]
    cl={"BORDER":[],"INTERIOR":[]}
    if len(evidx):
        groups=[]; cur=[evidx[0]]
        for i in evidx[1:]:
            if sec[i]-sec[cur[-1]]>8: groups.append(cur);cur=[]
            cur.append(i)
        groups.append(cur)
        for grp in groups:
            c=sec[int(np.mean(grp))]; cls="BORDER" if any(abs(c-b)<=30 for b in bd) else "INTERIOR"
            w=(sec>=c-10)&(sec<=c+10)
            if w.sum()<3: continue
            cl[cls].append(dict(peak_z=(rm[w].max()-rmean)/rsd,
                ent_exc=ent[w].mean()-bent, det_exc=det[w].mean()-bdet, ent_abs=ent[w].mean()))
    date,team=parse(mid); dur=(sec.max()-sec.min())
    rec=dict(mid=mid,date=date,team=team)
    for cls in ["BORDER","INTERIOR"]:
        L=cl[cls]
        rec[f"{cls}_n"]=len(L)
        rec[f"{cls}_rate"]=100*len(L)/(dur/60)  # events per minute *100? -> per-meeting count rate
        for k in ["peak_z","ent_exc","det_exc","ent_abs"]:
            rec[f"{cls}_{k}"]=np.mean([d[k] for d in L]) if L else np.nan
    rec["base_ent"]=bent; rec["base_det"]=bdet
    rows.append(rec)
P=pd.DataFrame(rows).sort_values(["team","date"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()
P.to_csv("reorg_depth_longitudinal_panel.csv",index=False)
def mk(sub,col):
    s=sub.dropna(subset=[col])
    if len(s)<6: return ("   --",np.nan)
    t,p=kendalltau(s.week,s[col]); st="**" if p<.01 else "*" if p<.05 else ""
    return (f"{t:+.2f}({p:.2f}){st}",p)
COLS=["BORDER_peak_z","INTERIOR_peak_z","BORDER_ent_exc","INTERIOR_ent_exc","BORDER_det_exc","INTERIOR_det_exc",
      "BORDER_ent_abs","INTERIOR_ent_abs","base_ent","base_det"]
print("=== DEPTH/intensity of reorganization over weeks — Kendall tau (per team | pooled) ===")
print(f"{'measure':18s} | {'startup_a':>13s} | {'startup_b':>13s} | {'pooled':>13s}")
pooled_ps=[]
for col in COLS:
    a=mk(P[P.team=='startup_a'],col); b=mk(P[P.team=='startup_b'],col); pl=mk(P,col)
    pooled_ps.append((col,pl[1]))
    print(f"{col:18s} | {a[0]:>13s} | {b[0]:>13s} | {pl[0]:>13s}")
ps=[p for _,p in pooled_ps if not np.isnan(p)]; labs=[c for c,p in pooled_ps if not np.isnan(p)]
q=multipletests(ps,method="fdr_bh")[1]
print(f"\npooled trends surviving BH-FDR: {(q<.05).sum()}/{len(q)}",
      "->",[labs[i] for i in range(len(q)) if q[i]<.05] or "none")
print("\nEarly vs late means (pooled):")
P["half"]=np.where(P.week<P.groupby('team').week.transform('median'),"early","late")
print(P.groupby("half")[["BORDER_peak_z","INTERIOR_peak_z","BORDER_ent_exc","INTERIOR_ent_exc",
      "base_ent","base_det","BORDER_n","INTERIOR_n"]].mean().round(2).to_string())
print(f"\n(peak_z=spike prominence in SD; ent_exc=entropy above baseline; n meetings={len(P)})")
