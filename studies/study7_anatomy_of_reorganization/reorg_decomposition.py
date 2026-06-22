"""How much of reorganization is TRANSITION vs INTERIOR, and what is the interior?

PART A - attributable-fraction decomposition. Per meeting: reorg events = seconds with rmse_g above
mean+2.33SD. A 'transition zone' = +/-W s of any boundary (topic-episode start U EOS L10 stage onset).
With r_zone, r_int the event rates inside/outside zones and T_zone, T_int their durations:
  transition share = (r_zone - r_int)*T_zone / E_total      # excess concentrated at transitions
  interior  share  =  r_int*T_total          / E_total      # background rate present everywhere
(these sum to 1 exactly). Reported event-based (primary) and on continuous rmse mass (robustness),
for topic-only / L10-only / union boundaries, swept over W.

PART B - what is the interior reorganization? Among INTERIOR seconds only (outside every zone), compare
reorg vs non-reorg seconds on floor/turn-taking and content features (per-meeting standardized mean
difference, Wilcoxon across meetings, BH-FDR). Plus a logistic attribution: pseudo-R2 of (zone only) vs
(zone + features) to size the interior-feature contribution beyond transitions."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm

GM="data/metrics_gorman_l8"; TXT="data/text_startup"
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ]"," ",s)).strip()
def l10_onsets(mid):
    f=f"data/l10_stages/{mid}.json"; tp=f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d=json.load(open(f)); tx=pd.read_csv(tp)
    on=pd.to_numeric(tx["onset_seconds"],errors="coerce").to_numpy(); ntx=[norm(t) for t in tx["text"]]
    seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(ntx)):
            if q and q in ntx[i]: idx=i; break
        if idx is None:
            for i in range(len(ntx)):
                if q and q in ntx[i]: idx=i; break
        if idx is not None: seg.append(float(on[idx])); prev=idx+1
    return seg

EP=pd.read_csv("episode_codes.csv")
mids=sorted(set(os.path.basename(p).replace("_gorman.csv","") for p in glob.glob(f"{GM}/*.csv")))

# ---------- PART A ----------
def zones(sec,bounds,W):
    z=np.zeros(len(sec),bool)
    for b in bounds:
        if b>sec.min()+1: z|=(np.abs(sec-b)<=W)
    return z
def decomp(which,W):
    rows=[]
    for mid in mids:
        g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g["second"].to_numpy(float)
        rm=g["rmse_g"].to_numpy(float); ok=~np.isnan(rm)
        sec,rm=sec[ok],rm[ok]
        if len(rm)<30: continue
        ev=rm>(rm.mean()+2.33*rm.std())
        tb=sorted(EP[EP.mid==mid]["sec_start"].tolist())
        lb=l10_onsets(mid)
        bd={"topic":tb,"l10":lb,"union":sorted(set(tb)|set(lb))}[which]
        if not bd: continue
        inz=zones(sec,bd,W); Tz=inz.sum(); Ti=(~inz).sum()
        if Tz<5 or Ti<5 or ev.sum()<3: continue
        rz=ev[inz].mean(); ri=ev[~inz].mean(); Et=ev.sum()
        tr=(rz-ri)*Tz; itl=ri*len(sec)
        # continuous (rmse mass above interior-mean)
        mz=rm[inz].mean(); mi=rm[~inz].mean()
        c_tr=(mz-mi)*Tz; c_int=mi*len(sec); c_tot=rm.sum()
        rows.append(dict(mid=mid,Et=Et,pct_tr=100*tr/Et,pct_int=100*itl/Et,lift=rz/ri if ri>0 else np.nan,
                         c_tr=100*c_tr/c_tot,c_int=100*c_int/c_tot,Tz_frac=100*Tz/len(sec)))
    return pd.DataFrame(rows)

print("="*78,"\nPART A  Decomposition: transition vs interior share of reorganization\n"+"="*78)
for W in (15,30,45):
    print(f"\n--- zone half-width W={W}s ---")
    for which in ("topic","l10","union"):
        d=decomp(which,W)
        print(f"  {which:6s} (n={len(d)}): events  TRANSITION {d.pct_tr.mean():4.1f}%  | INTERIOR {d.pct_int.mean():4.1f}%"
              f"   (zone covers {d.Tz_frac.mean():4.1f}% of time; event lift x{d.lift.mean():.2f})"
              f"   || rmse-mass  transition {d.c_tr.mean():4.1f}% | interior {d.c_int.mean():4.1f}%")
dW=decomp("union",30)
dW.to_csv("reorg_decomposition_union_W30.csv",index=False)
print(f"\nPrimary (union, W=30): of all reorganization events, {dW.pct_tr.mean():.0f}% is transition-driven "
      f"excess and {dW.pct_int.mean():.0f}% is interior/background (n={len(dW)} meetings).")

# ---------- PART B ----------
print("\n"+"="*78,"\nPART B  What is the INTERIOR reorganization? (interior seconds only)\n"+"="*78)
FW=pd.read_csv("floor_windows.csv"); TW=pd.read_csv("triangulation_windows.csv")
WIN=pd.merge(FW[["mid","bin","n_active","top_share","net_central"]],
             TW[["mid","bin","transition_entropy","n_turns","sem_rec","nov","latency"]],on=["mid","bin"],how="outer")
def content(mid):
    e=EP[EP.mid==mid].copy()
    for nm,cols in {"disagree":["bdisagree","disagree","bantag"],"humor":["btension"],
                    "question":["qset","qprop","baskinfo","baskopin"],"directive":["directive"],
                    "explor":["explor","iam2"]}.items():
        e[nm]=e[[c for c in cols if c in e]].sum(1)/e["n_utt"].clip(lower=1)
    return e
rows=[]
for mid in mids:
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g["second"].to_numpy(float); rm=g["rmse_g"].to_numpy(float)
    ok=~np.isnan(rm); sec,rm=sec[ok],rm[ok]
    if len(rm)<30: continue
    ev=(rm>(rm.mean()+2.33*rm.std())).astype(int)
    tb=sorted(EP[EP.mid==mid]["sec_start"].tolist()); lb=l10_onsets(mid)
    bd=sorted(set(tb)|set(lb)); inz=zones(sec,bd,30)
    df=pd.DataFrame(dict(mid=mid,second=sec,reorg=ev,in_zone=inz))
    df["bin"]=(df.second//90*90).astype(int)
    df=df.merge(WIN[WIN.mid==mid],on=["mid","bin"],how="left")
    # content per second via episode
    ce=content(mid); df["disagree"]=df["humor"]=df["question"]=df["directive"]=df["explor"]=np.nan
    for _,r in ce.iterrows():
        m=(df.second>=r.sec_start)&(df.second<r.sec_end)
        for nm in ["disagree","humor","question","directive","explor"]: df.loc[m,nm]=r[nm]
    # local turnover from transcript (+/-15s)
    tp=f"{TXT}/{mid}_transcript.csv"
    if os.path.exists(tp):
        tx=pd.read_csv(tp); o=pd.to_numeric(tx["onset_seconds"],errors="coerce").to_numpy()
        sp=tx["speaker_id"].astype(str).to_numpy(); good=~np.isnan(o); o,sp=o[good],sp[good]
        nsw=[];nspk=[]
        for s in df.second:
            j=(o>=s-15)&(o<=s+15); spp=sp[j]
            nspk.append(len(set(spp))); nsw.append(int(np.sum(spp[1:]!=spp[:-1])) if len(spp)>1 else 0)
        df["loc_nspk"]=nspk; df["loc_switch"]=nsw
    rows.append(df)
D=pd.concat(rows,ignore_index=True)
FEATS=["top_share","net_central","n_active","loc_nspk","loc_switch","transition_entropy","n_turns",
       "sem_rec","nov","latency","disagree","humor","question","directive","explor"]
NICE={"top_share":"top-speaker share (floor concentration)","net_central":"network centralization",
 "n_active":"active speakers / 90s","loc_nspk":"distinct speakers (+/-15s)","loc_switch":"speaker switches (+/-15s)",
 "transition_entropy":"speaker-transition entropy","n_turns":"turns / 90s","sem_rec":"semantic recurrence",
 "nov":"lexical novelty","latency":"turn latency","disagree":"disagreement (content)","humor":"humor / tension-release",
 "question":"questions (content)","directive":"directives (content)","explor":"exploratory talk (content)"}
# interior only: per-meeting standardized mean diff reorg vs non-reorg
INT=D[~D.in_zone]
res=[]
for f in FEATS:
    diffs=[]
    for mid,g in INT.groupby("mid"):
        a=g.loc[g.reorg==1,f].dropna(); b=g.loc[g.reorg==0,f].dropna()
        if len(a)<5 or len(b)<20: continue
        sd=g[f].std()
        if not sd or np.isnan(sd): continue
        diffs.append((a.mean()-b.mean())/sd)
    diffs=[d for d in diffs if not np.isnan(d)]
    if len(diffs)<8: continue
    p=wilcoxon(diffs).pvalue
    res.append(dict(feature=f,label=NICE[f],n=len(diffs),d=np.mean(diffs),p=p))
R=pd.DataFrame(res); R["q"]=multipletests(R["p"],method="fdr_bh")[1]
R["sig"]=R["q"].apply(lambda q:"***" if q<.001 else "**" if q<.01 else "*" if q<.05 else "")
R=R.sort_values("d",ascending=False)
R.round(3).to_csv("reorg_interior_drivers.csv",index=False)
print("\nInterior reorg vs interior baseline (standardized mean diff d; +d = elevated during interior reorg):")
print(R[["label","n","d","p","q","sig"]].to_string(index=False))

# logistic attribution: zone-only vs zone+features
Z=D.dropna(subset=FEATS+["in_zone","reorg"]).copy()
for f in FEATS: Z[f]=(Z[f]-Z[f].mean())/Z[f].std()
def llf(X):
    m=sm.Logit(Z["reorg"],sm.add_constant(X)).fit(disp=0); return m.llf,m.llnull
ll0=sm.Logit(Z["reorg"],sm.add_constant(Z[["in_zone"]].astype(float))).fit(disp=0)
ll1=sm.Logit(Z["reorg"],sm.add_constant(Z[["in_zone"]+FEATS].astype(float))).fit(disp=0)
print(f"\nLogistic pseudo-R2 (McFadden): zone only = {1-ll0.llf/ll0.llnull:.3f}; "
      f"zone+features = {1-ll1.llf/ll1.llnull:.3f}; interior-feature increment = "
      f"{(ll0.llf-ll1.llf)/(ll0.llnull-0):+.3f} relative.")
print(f"  => beyond transition zones, floor+content features add predictive signal for reorganization.")
