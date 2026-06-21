"""Phase follow-ups:
(a) Hysteresis lag in seconds: cross-correlation of entropy_g(t) vs det_g(t+tau); the tau of strongest
    ANTI-correlation = how many seconds %DET lags entropy (entropy leads if tau>0).
(b) Floor x event: floor/centrality measures on turns within +-45s of each entropy PEAK vs VALLEY
    (event-centered snapshots), paired Wilcoxon across meetings. Confirms F2(peak) vs F1(valley) at the
    event level, using turn-structure measures (not just entropy)."""
import glob,os,re,numpy as np,pandas as pd
from scipy.signal import find_peaks
from scipy.stats import wilcoxon
GM="data/metrics_gorman_l8"; TXT="data/text_startup"
WORD=re.compile(r"[a-zà-ÿ]+")
def nw(s): return max(1,len(WORD.findall(str(s).lower())))
def gini(x):
    x=np.asarray(x,float); x=x[x>=0]
    if x.sum()==0 or len(x)<2: return np.nan
    xs=np.sort(x); n=len(x); idx=np.arange(1,n+1); return (2*np.sum(idx*xs)/(n*xs.sum()))-(n+1)/n
def shannon(p):
    p=np.asarray(p,float); p=p[p>0]; p=p/p.sum(); return -(p*np.log2(p)).sum() if len(p) else 0.0
def degcen(W):
    N=W.shape[0]
    if N<3: return np.nan
    deg=W.sum(0)+W.sum(1); s=deg.sum()
    if s==0: return np.nan
    deg=deg/s; return (deg.max()-deg).sum()/(N-1)
def inout(W):
    if W.shape[0]<2 or W.sum()==0: return np.nan
    return np.abs(W.sum(1)-W.sum(0)).max()/W.sum()
def floor_on(sub):
    sps=sorted(sub.sp.unique()); idx={s:i for i,s in enumerate(sps)}; nsp=len(sps)
    if nsp<2 or len(sub)<4: return None
    words=np.array([sub.loc[sub.sp==s,"nwd"].sum() for s in sps],float)
    seq=sub.sort_values("onset")["sp"].to_numpy(); W=np.zeros((nsp,nsp))
    for a,c in zip(seq[:-1],seq[1:]):
        if a!=c: W[idx[a],idx[c]]+=1
    return dict(top_share=words.max()/words.sum() if words.sum()>0 else np.nan,
        gini_words=gini(words), part_entropy=shannon(words), n_active=nsp,
        net_central=degcen(W), inout_asym=inout(W))

lags=[]
fl_peak={k:[] for k in ["top_share","gini_words","part_entropy","n_active","net_central","inout_asym"]}
fl_val={k:[] for k in fl_peak}
for f in sorted(glob.glob(GM+"/*_gorman.csv")):
    mid=os.path.basename(f).replace("_gorman.csv","")
    tp=f"{TXT}/{mid}_transcript.csv"
    if not os.path.exists(tp): continue
    g=pd.read_csv(f); e=g.entropy_g.to_numpy(float); d=g.det_g.to_numpy(float); sec=g["second"].to_numpy()
    # (a) cross-correlation lag
    e0=(e-e.mean())/(e.std()+1e-9); d0=(d-d.mean())/(d.std()+1e-9); n=len(e0); best=(0,1)
    for tau in range(-30,31):
        if tau>=0: c=np.corrcoef(e0[:n-tau],d0[tau:])[0,1] if n-tau>10 else 1
        else: c=np.corrcoef(e0[-tau:],d0[:n+tau])[0,1] if n+tau>10 else 1
        if c<best[1]: best=(tau,c)
    lags.append(best[0])
    # (b) floor snapshots at entropy peaks vs valleys
    sd=np.nanstd(e); pk,_=find_peaks(e,prominence=0.5*sd); vl,_=find_peaks(-e,prominence=0.5*sd)
    df=pd.read_csv(tp); df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]); df["sp"]=pd.to_numeric(df["speaker_id"],errors="coerce")
    df=df.dropna(subset=["sp"]).assign(sp=lambda x:x.sp.astype(int)); df["nwd"]=df["text"].apply(nw)
    def agg(idxs):
        vals={k:[] for k in fl_peak}
        for i in idxs:
            t=sec[i]; sub=df[(df.onset>=t-45)&(df.onset<=t+45)]
            r=floor_on(sub)
            if r:
                for k in vals: vals[k].append(r[k])
        return {k:(np.nanmean(v) if v else np.nan) for k,v in vals.items()}
    ap=agg(pk); av=agg(vl)
    for k in fl_peak:
        fl_peak[k].append(ap[k]); fl_val[k].append(av[k])

L=np.array(lags)
print("=== (a) Hysteresis lag: tau of strongest entropy–%DET anti-correlation ===")
print(f"   median lag = {np.median(L):+.0f} s   (positive = %DET LAGS entropy / entropy leads)")
print(f"   mean = {L.mean():+.1f}s   %meetings tau>0 = {100*np.mean(L>0):.0f}%   %tau>=0 = {100*np.mean(L>=0):.0f}%")
try: print(f"   Wilcoxon lag≠0: p={wilcoxon(L).pvalue:.4f}")
except: pass

print("\n=== (b) Floor at entropy PEAK vs VALLEY (event-centered ±45s; paired Wilcoxon, n mtgs) ===")
print(f"   {'measure':14}| {'peak':>8} | {'valley':>8} | {'Δ(peak−val)':>12} | p")
def bh(p):
    p=np.array(p); n=len(p); o=np.argsort(p); r=p[o]*n/(np.arange(n)+1)
    q=np.minimum.accumulate(r[::-1])[::-1]; out=np.empty(n); out[o]=np.clip(q,0,1); return out
rows=[]; ps=[]
for k in fl_peak:
    a=np.array(fl_peak[k]); b=np.array(fl_val[k]); m=np.isfinite(a)&np.isfinite(b); a,b=a[m],b[m]
    p=wilcoxon(a,b).pvalue if len(a)>=10 and not np.allclose(a,b) else 1
    rows.append((k,a.mean(),b.mean(),(a-b).mean(),p)); ps.append(p)
q=bh(ps)
for (k,pa,va,dd,p),qq in zip(rows,q):
    print(f"   {k:14}| {pa:>8.3f} | {va:>8.3f} | {dd:>+12.3f} | q={qq:.3f}{'*' if qq<.05 else ''}")
print("\n(F2/reorg expected at PEAK: top_share↓, gini↓, net_central↓, inout↓, n_active↑, part_entropy↑)")
