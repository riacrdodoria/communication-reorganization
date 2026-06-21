"""Validate unsupervised (TextTiling) vs LLM topic segmentation on the 8-meeting subset.
Boundary F1 within tolerance + WindowDiff, vs a random-boundary baseline.
Caveat: LLM row indices may carry a small header/0-vs-1 offset; the tolerance window absorbs it."""
import numpy as np,pandas as pd
llm={
"2024.10.14startup_a":[12,24,79,128,195,267,365,385,444,475],
"2024.12.09startup_a":[45,97,144,203,238,261,337,372,431,476,495],
"2025.02.24startup_a":[19,41,78,100,125,220,287,351],
"2025.04.14startup_a":[27,92,162,433,460,472],
"2024.10.14startup_b":[40,86,263,421,613,806],
"2024.12.16startup_b":[57,91,113,177,214,257,291,305,373,421,477,557,601],
"2025.02.24startup_b":[22,62,158,203,391],
"2025.04.14startup_b":[111,232,350,384]}
E=pd.read_csv("episodes_unsup.csv")
rng=np.random.default_rng(0); TOL=15
def f1(ref,hyp,tol):
    if not ref or not hyp: return 0.0
    mr=sum(any(abs(r-h)<=tol for h in hyp) for r in ref)
    mh=sum(any(abs(h-r)<=tol for r in ref) for h in hyp)
    prec=mh/len(hyp); rec=mr/len(ref)
    return 2*prec*rec/(prec+rec) if prec+rec>0 else 0.0
def windowdiff(ref,hyp,n,k):
    e=0;t=0
    for i in range(max(1,n-k)):
        rc=sum(1 for b in ref if i<b<=i+k); hc=sum(1 for b in hyp if i<b<=i+k)
        e+=(rc!=hc); t+=1
    return e/t if t else np.nan
print(f"{'meeting':22}| {'#unsup':>6} {'#llm':>5} | {'F1(±15)':>8} {'F1rand':>7} | {'WDiff':>6} {'WDrand':>7}")
F=[];Fr=[];W=[];Wr=[]
for mid,lb in llm.items():
    sub=E[E.mid==mid].sort_values("utt_start"); ub=[int(x) for x in sub.utt_start.tolist() if x>0]
    n=int(sub.utt_end.max())+1
    f=f1(lb,ub,TOL); k=max(5,n//(2*max(1,len(lb))))
    wd=windowdiff(lb,ub,n,k)
    # random baseline: same count as unsup, random positions
    fr=[];wr=[]
    for _ in range(200):
        rb=sorted(rng.choice(range(20,n-20),size=min(len(ub),max(1,n-40)),replace=False).tolist())
        fr.append(f1(lb,rb,TOL)); wr.append(windowdiff(lb,rb,n,k))
    fr=np.mean(fr);wr=np.mean(wr)
    F.append(f);Fr.append(fr);W.append(wd);Wr.append(wr)
    print(f"{mid:22}| {len(ub):>6} {len(lb):>5} | {f:>8.2f} {fr:>7.2f} | {wd:>6.2f} {wr:>7.2f}")
print("-"*72)
print(f"{'MEAN':22}| {'':>6} {'':>5} | {np.mean(F):>8.2f} {np.mean(Fr):>7.2f} | {np.mean(W):>6.2f} {np.mean(Wr):>7.2f}")
print(f"\nBoundary F1 vs random: {np.mean(F):.2f} vs {np.mean(Fr):.2f}  (higher=better, agreement above chance)")
print(f"WindowDiff vs random:  {np.mean(W):.2f} vs {np.mean(Wr):.2f}  (LOWER=better)")
