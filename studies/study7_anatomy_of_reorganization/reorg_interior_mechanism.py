"""What interactional event IS an interior reorganization (mid-topic, not a transition)?

For each meeting: interior reorg events = clusters of reorg seconds (rmse_g > mean+2.33SD) that lie OUTSIDE
every +/-30s transition zone (topic-episode start U EOS L10 onset). Around each event center we read the
transcript and score interactional mechanisms (mostly identity/content based, so not tautological with the
turn-taking entropy):
  HANDOFF      - the speaker dominating the floor changes from before->after
  OPENING      - the floor de-concentrates (top-speaker word-share drops >=.15 and +>=1 active speaker)
  QUESTION     - a question ('?') occurs just before/at the event
  NEW_VOICE    - a speaker silent in the prior ~70s speaks at the event
  CONVERGENCE  - a cluster of short agreement/backchannel turns right after (sim/isso/exato/...)
  ROUNDROBIN   - >=3 distinct speakers each take a short turn in quick sequence
Each mechanism's prevalence among interior reorg events is compared to a matched set of interior NON-reorg
baseline windows (lift). A priority rule assigns one primary mechanism per event for a clean breakdown.
Also dumps exemplar windows (with text) to reorg_interior_exemplars.txt for qualitative reading (LOCAL ONLY
- contains transcript text, never published)."""
import glob,os,json,re,unicodedata,numpy as np,pandas as pd
TXT="data/text_startup"; GM="data/metrics_gorman_l8"
AGREE=set("sim isso exato certo verdade perfeito boa claro ta ta isso ahn uhum aham legal otimo show beleza".split())
def norm(s):
    s=unicodedata.normalize("NFKD",str(s).lower()); s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9 ?]"," ",s)).strip()
def l10_onsets(mid):
    f=f"data/l10_stages/{mid}.json"; tp=f"{TXT}/{mid}_transcript.csv"
    if not (os.path.exists(f) and os.path.exists(tp)): return []
    d=json.load(open(f)); tx=pd.read_csv(tp); on=pd.to_numeric(tx["onset_seconds"],errors="coerce").to_numpy()
    nt=[norm(t) for t in tx["text"]]; seg=[]; prev=0
    for st in d["stages"]:
        q=norm(st["quote"])[:60]; idx=None
        for i in range(prev,len(nt)):
            if q and q in nt[i]: idx=i;break
        if idx is None:
            for i in range(len(nt)):
                if q and q in nt[i]: idx=i;break
        if idx is not None: seg.append(float(on[idx]));prev=idx+1
    return seg
EP=pd.read_csv("episode_codes.csv")
mids=sorted(set(os.path.basename(p).replace("_gorman.csv","") for p in glob.glob(f"{GM}/*.csv")))

def speakers(tx,a,b):  # word count per speaker in [a,b)
    j=(tx.onset>=a)&(tx.onset<b); s={}
    for sp,w in zip(tx.spk[j],tx.nw[j]): s[sp]=s.get(sp,0)+w
    return s
def feats(tx,c):
    B=speakers(tx,c-30,c); A=speakers(tx,c,c+30)
    db=max(B,key=B.get) if B else None; da=max(A,key=A.get) if A else None
    tsB=max(B.values())/sum(B.values()) if B else np.nan
    tsA=max(A.values())/sum(A.values()) if A else np.nan
    prior=set(speakers(tx,c-90,c-20)); peri=set(speakers(tx,c-10,c+20))
    j=(tx.onset>=c-12)&(tx.onset<=c+8); qn=any("?" in t for t in tx.text[j])
    pj=(tx.onset>=c-10)&(tx.onset<=c+20); seq=tx.spk[pj].tolist()
    short=[(sp,t) for sp,t,w in zip(tx.spk[pj],tx.text[pj],tx.nw[pj]) if w<=3]
    agr=sum(1 for sp,t in short if any(x in norm(t).split() for x in AGREE))
    return dict(handoff=int(db is not None and da is not None and db!=da),
        opening=int((not np.isnan(tsB)) and (not np.isnan(tsA)) and tsB-tsA>=.15 and len(A)>=len(B)+1),
        question=int(qn), new_voice=int(len(peri-prior)>0),
        convergence=int(agr>=2), roundrobin=int(len(set(seq))>=3 and len(seq)>=4),
        n_spk_peri=len(peri), dom_b=db, dom_a=da)

ev_rows=[]; base_rows=[]; exemplars=[]
rng=np.random.default_rng(0)
for mid in mids:
    g=pd.read_csv(f"{GM}/{mid}_gorman.csv"); sec=g.second.to_numpy(float); rm=g.rmse_g.to_numpy(float)
    ok=~np.isnan(rm); sec,rm=sec[ok],rm[ok]
    if len(rm)<60: continue
    ev=sec[rm>(rm.mean()+2.33*rm.std())]
    tb=sorted(EP[EP.mid==mid].sec_start.tolist()); bd=sorted(set(tb)|set(l10_onsets(mid)))
    def interior(s): return all(abs(s-b)>30 for b in bd)
    evi=sorted(s for s in ev if interior(s))
    # cluster reorg seconds into events (gap>8s -> new event)
    events=[]; cur=[]
    for s in evi:
        if cur and s-cur[-1]>8: events.append(cur);cur=[]
        cur.append(s)
    if cur: events.append(cur)
    centers=[float(np.mean(e)) for e in events]
    tx=pd.read_csv(f"{TXT}/{mid}_transcript.csv")
    tx=pd.DataFrame(dict(onset=pd.to_numeric(tx.onset_seconds,errors="coerce"),
        spk=tx.speaker_id.astype(str),text=tx.text.astype(str)))
    tx=tx.dropna(subset=["onset"]); tx["nw"]=tx.text.str.split().apply(len)
    # baseline: interior seconds far from any reorg event
    far=[s for s in sec if interior(s) and all(abs(s-c)>30 for c in centers)]
    bcent=rng.choice(far,size=min(len(centers),len(far)),replace=False) if far else []
    for c in centers:
        f=feats(tx,c); f["mid"]=mid; f["c"]=c; ev_rows.append(f)
    for c in bcent:
        f=feats(tx,float(c)); base_rows.append(f)
    # exemplars: a few strongest (closest reorg second to a clear handoff/opening/question)
    for c in centers[:3]:
        f=feats(tx,c); w=tx[(tx.onset>=c-22)&(tx.onset<=c+22)]
        txt="\n".join(f"   [{int(o):4d}s S{sp}] {t}" for o,sp,t in zip(w.onset,w.spk,w.text))
        tags=[k for k in ["handoff","opening","question","new_voice","convergence","roundrobin"] if f[k]]
        exemplars.append(f"### {mid} @ {int(c)}s  tags={tags}\n{txt}\n")
E=pd.DataFrame(ev_rows); Bs=pd.DataFrame(base_rows)
MECH=["handoff","opening","question","new_voice","convergence","roundrobin"]
print(f"interior reorg events: {len(E)}  ({E.mid.nunique()} meetings)   matched baseline windows: {len(Bs)}")
print("\n=== Mechanism prevalence among INTERIOR reorg events vs matched interior baseline ===")
print(f"{'mechanism':12s} {'reorg%':>8s} {'base%':>8s} {'lift':>6s}")
for m in MECH:
    r=100*E[m].mean(); b=100*Bs[m].mean() if len(Bs) else np.nan
    print(f"{m:12s} {r:8.0f} {b:8.0f} {r/b if b else np.nan:6.2f}")
# primary mechanism (priority: handoff > new_voice > question > opening > roundrobin > convergence)
def primary(r):
    for m in ["handoff","new_voice","question","opening","roundrobin","convergence"]:
        if r[m]: return m
    return "other/diffuse"
E["primary"]=E.apply(primary,axis=1)
print("\n=== Primary interactional type of interior reorganization (priority-assigned) ===")
pc=E.primary.value_counts(normalize=True).mul(100).round(0)
for k,v in pc.items(): print(f"  {k:14s} {v:4.0f}%")
print(f"\nmean distinct speakers in peri-window: reorg {E.n_spk_peri.mean():.2f} vs baseline {Bs.n_spk_peri.mean():.2f}")
E.drop(columns=["dom_b","dom_a"]).to_csv("reorg_interior_mechanism.csv",index=False)
open("reorg_interior_exemplars.txt","w").write("\n".join(exemplars))
print(f"\nwrote reorg_interior_mechanism.csv and {len(exemplars)} exemplars to reorg_interior_exemplars.txt (LOCAL)")
