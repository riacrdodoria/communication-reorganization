"""Longitudinally, do reorganizations move toward the BORDER (topic/agenda transitions) or toward the
INTERIOR over the ~26 weeks? Per meeting: border share, interior reorg-event rate, border enrichment
(lift), total reorg rate, and controls (n boundaries, duration). Order meetings by date within team;
Kendall-tau (Mann-Kendall) trend per team and pooled. Writes reorg_longitudinal_panel.csv."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import kendalltau
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
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
def parse(mid):
    m=re.match(r"(\d{4})\.(\d{2})\.(\d{2})(startup_[ab])",mid)
    y,mo,d,team=m.groups(); return int(y)*10000+int(mo)*100+int(d),team
EP=pd.read_csv("episode_codes.csv")
rows=[]
for f in sorted(glob.glob(f"{GM}/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    g=pd.read_csv(f); sec=g.second.to_numpy(float); rm=g.rmse_g.to_numpy(float)
    ok=~np.isnan(rm); sec,rm=sec[ok],rm[ok]
    if len(rm)<60: continue
    ev=rm>(rm.mean()+2.33*rm.std())
    tb=sorted(EP[EP.mid==mid].sec_start.tolist()); lb=l10_onsets(mid)
    bd=sorted(set(tb)|set(lb))
    if not bd or ev.sum()<5: continue
    inz=np.zeros(len(sec),bool)
    for b in bd:
        if b>sec.min()+1: inz|=(np.abs(sec-b)<=30)
    Tz=inz.sum(); Ti=(~inz).sum()
    if Tz<5 or Ti<5: continue
    rz=ev[inz].mean(); ri=ev[~inz].mean(); Et=ev.sum()
    border=100*(rz-ri)*Tz/Et
    date,team=parse(mid)
    rows.append(dict(mid=mid,date=date,team=team,
        border_share=border, interior_share=100-border,
        r_int=100*ri, r_zone=100*rz, lift=rz/ri if ri>0 else np.nan,
        total_rate=100*ev.mean(), n_bounds=len(bd), n_topic=len(set(tb)), n_l10=len(set(lb)),
        dur_min=(sec.max()-sec.min())/60))
P=pd.DataFrame(rows).sort_values(["team","date"]).reset_index(drop=True)
P["week"]=P.groupby("team").cumcount()
P.to_csv("reorg_longitudinal_panel.csv",index=False)

MET=["border_share","interior_share","r_int","lift","total_rate","n_bounds","dur_min"]
def mk(sub,col):
    s=sub.dropna(subset=[col]);
    if len(s)<6: return (np.nan,np.nan,len(s))
    t,p=kendalltau(s.week,s[col]); return (t,p,len(s))
print("=== Trend over weeks (Kendall tau; *p<.05 **p<.01) ===")
print(f"{'metric':14s} | {'startup_a tau (p)':>20s} | {'startup_b tau (p)':>20s} | {'pooled tau (p)':>18s}")
for col in MET:
    cells=[]
    for team in ["startup_a","startup_b",None]:
        sub=P if team is None else P[P.team==team]
        t,p,n=mk(sub,col); star="**" if p<.01 else "*" if p<.05 else "" if not np.isnan(p) else ""
        cells.append(f"{t:+.2f} ({p:.3f}){star}" if not np.isnan(t) else "   --")
    print(f"{col:14s} | {cells[0]:>20s} | {cells[1]:>20s} | {cells[2]:>18s}")
print("\nMeans by half (early vs late weeks), pooled:")
P["half"]=np.where(P.week< P.groupby('team').week.transform('median'),"early","late")
print(P.groupby("half")[["border_share","interior_share","r_int","lift","total_rate","n_bounds","dur_min"]].mean().round(1).to_string())
print(f"\nn meetings: {len(P)}  (startup_a {sum(P.team=='startup_a')}, startup_b {sum(P.team=='startup_b')})")
