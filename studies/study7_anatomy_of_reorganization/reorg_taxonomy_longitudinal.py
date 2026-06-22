"""Does the CONTENT (taxonomy) of reorganization vary over the ~26 weeks? Three cuts:
 (1) topic-border vs L10-border content, separately;
 (2) longitudinally (Kendall tau over weeks, per team);
 (3) CONTINUOUS reorganization (rmse_g) as well as event-based lift.
Per second we take window-level (90s codebook) category densities, z-score each within meeting, and build a
coordination-minus-deliberation composite C(t) (category signs inherited from reorg_taxonomy_borderinterior:
border_lift>0 = coordination, <0 = deliberation). Per meeting we then compute, and track over weeks:
  axis_cont   = corr(rmse_g, C)                         # continuous alignment (cut 3)
  axis_event  = C[rmse peaks] - C[baseline]             # event-based lift (SD units)
  Ctopic_bord = mean C in +/-30s of topic boundaries    # content AT topic borders (cut 1)
  Cl10_bord   = mean C in +/-30s of L10 onsets          # content AT L10 borders   (cut 1)
  Cinterior   = mean C in the interior
and per-taxonomy axis_event. Writes reorg_taxonomy_longitudinal_panel.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import kendalltau,pearsonr
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
COD2="data/codebooks2"; COD1="data/codebooks"
CATS2=['arguable','converge','disagree','delim','nonarg','iam1','iam2','iam3','iam4','iam5','disput','cumul',
 'explor','bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin','basksug','bsolid','btension','bagree',
 'bdisagree','btensh','bantag']
CATS1=['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans','coop','qset',
 'qprop','directive','commissive','feedback']
TAX={**{c:"CACS" for c in ['arguable','converge','disagree','delim','nonarg']},
 **{c:"IAM" for c in ['iam1','iam2','iam3','iam4','iam5']},**{c:"Mercer" for c in ['disput','cumul','explor']},
 **{c:"Bales" for c in ['bgiveinfo','bgiveopin','bgivesug','baskinfo','baskopin','basksug','bsolid','btension','bagree','bdisagree','btensh','bantag']},
 **{c:"act4teams" for c in ['namep','linkp','names','links','linkc','cprod','proact','struct','ginfo','ktrans','coop']},
 **{c:"ISO" for c in ['qset','qprop','directive','commissive','feedback']}}
# category signs from the border/interior fingerprint
BI=pd.read_csv("reorg_taxonomy_borderinterior.csv").set_index("cat")
SIGN={c:(1 if BI.loc[c,"border_lift"]>0 else -1) for c in BI.index if c in TAX}
COORD=[c for c,s in SIGN.items() if s>0]; DELIB=[c for c,s in SIGN.items() if s<0]
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def load(folder):
    d={}
    for f in glob.glob(f"{folder}/*_passA.json"):
        mid=os.path.basename(f).replace("_passA.json","")
        d[mid]={int(w["t"]):w for w in json.load(open(f))["windows"]}
    return d
c2=load(COD2); c1=load(COD1)
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
    if mid not in c2: continue
    g=pd.read_csv(f); sec=g.second.to_numpy(float); rm=g.rmse_g.to_numpy(float)
    ok=np.isfinite(rm); sec,rm=sec[ok],rm[ok]
    if len(rm)<60: continue
    win=lambda s:int(s//90*90)
    def col(cat):
        cd=c2[mid] if cat in CATS2 else c1.get(mid,{})
        v=np.array([cd.get(win(s),{}).get(cat,0) for s in sec],float)
        sd=v.std(); return (v-v.mean())/sd if sd>0 else None
    def composite(cats_pos,cats_neg):
        pos=[col(c) for c in cats_pos]; neg=[col(c) for c in cats_neg]
        pos=[v for v in pos if v is not None]; neg=[v for v in neg if v is not None]
        if not pos and not neg: return None
        P=np.mean(pos,axis=0) if pos else 0; N=np.mean(neg,axis=0) if neg else 0
        return P-N
    C=composite(COORD,DELIB)
    if C is None: continue
    peak=rm>(rm.mean()+2.33*rm.std()); base=~peak
    tb=sorted(EP[EP.mid==mid].sec_start.tolist()); lb=l10_onsets(mid)
    def zone(bs):
        z=np.zeros(len(sec),bool)
        for b in bs:
            if b>sec.min()+1: z|=(np.abs(sec-b)<=30)
        return z
    zt=zone(tb); zl=zone(lb); inter=~(zt|zl)
    date,team=parse(mid)
    r_cont=pearsonr(rm,C)[0]
    rec=dict(mid=mid,date=date,team=team,
        axis_cont=r_cont,
        axis_event=(C[peak].mean()-C[base].mean()) if peak.sum()>=5 else np.nan,
        Ctopic=C[zt].mean() if zt.sum()>=5 else np.nan,
        Cl10=C[zl].mean() if zl.sum()>=5 else np.nan,
        Cinterior=C[inter].mean() if inter.sum()>=5 else np.nan)
    # per-taxonomy event-axis
    for t in ["CACS","IAM","Mercer","Bales","act4teams","ISO"]:
        cp=[c for c in COORD if TAX[c]==t]; cn=[c for c in DELIB if TAX[c]==t]
        Ct=composite(cp,cn)
        rec[f"axis_{t}"]=(Ct[peak].mean()-Ct[base].mean()) if (Ct is not None and peak.sum()>=5) else np.nan
    rows.append(rec)
P=pd.DataFrame(rows).sort_values(["team","date"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()
P.to_csv("reorg_taxonomy_longitudinal_panel.csv",index=False)
def mk(sub,col):
    s=sub.dropna(subset=[col])
    if len(s)<6: return "   --"
    t,p=kendalltau(s.week,s[col]); st="**" if p<.01 else "*" if p<.05 else ""
    return f"{t:+.2f}({p:.2f}){st}"
print(f"COORD cats ({len(COORD)}): {sorted(COORD)[:6]}...   DELIB cats ({len(DELIB)})")
print("\n=== Does the CONTENT of reorganization drift over weeks? Kendall tau (per team | pooled) ===")
print(f"{'measure':16s} | {'startup_a':>14s} | {'startup_b':>14s} | {'pooled':>14s}")
for col in ["axis_cont","axis_event","Ctopic","Cl10","Cinterior",
            "axis_CACS","axis_IAM","axis_Mercer","axis_Bales","axis_act4teams","axis_ISO"]:
    print(f"{col:16s} | {mk(P[P.team=='startup_a'],col):>14s} | {mk(P[P.team=='startup_b'],col):>14s} | {mk(P,col):>14s}")
print("\nEarly vs late means (pooled):")
P["half"]=np.where(P.week<P.groupby('team').week.transform('median'),"early","late")
print(P.groupby("half")[["axis_cont","axis_event","Ctopic","Cl10","Cinterior"]].mean().round(3).to_string())
print(f"\n(+ = more coordination-flavored;  axis_cont = corr(rmse,coord-delib composite); n={len(P)})")
