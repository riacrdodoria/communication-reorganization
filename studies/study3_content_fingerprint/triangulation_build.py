"""Triangulation: coding-free TEXT-dynamics measures per 90s window, aligned to the
reorganization metric grid (data/metrics_gorman_l8). Families:
  A. Conceptual/semantic recurrence (TF-IDF) -> sem_det, sem_rec  (Angus et al.)
  B. Turn-to-turn coherence & novelty (TF-IDF cosine)
  C. Lexical info-theoretic: word_entropy, ttr, mtld, hapax
  D. LSM (Language Style Matching) on PT function-word categories (curated, license-free)
  E. Structural turn stats: turn_len, latency, transition_entropy, gap, n_turns
  F. Coh-Metrix-PT subset: connective_density, content_overlap, words_per_sentence
Output: triangulation_windows.csv  (one row per 90s window per meeting)
No human/LLM coding; language-agnostic except D/F which use closed-class PT lists."""
import glob,os,re,numpy as np,pandas as pd
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

GM=Path("data/metrics_gorman_l8"); TXT=Path("data/text_startup")
WIN=90  # seconds, matches codebook windows

# ---------- PT closed-class lists (LSM 9 categories) ----------
FW={
"ppron":"eu me mim comigo tu te ti contigo você vocês ele ela eles elas lhe lhes nós nos conosco vós se si consigo agente".split(),
"ipron":"isto isso aquilo algo alguém ninguém nada tudo todo todos toda todas alguns algumas outro outra outros outras qual quais quem cada algum nenhum nenhuma".split(),
"article":"o a os as um uma uns umas".split(),
"prep":"de do da dos das em no na nos nas ao à aos às para pra por pelo pela pelos pelas com sem sobre sob entre até desde contra perante ante após".split(),
"auxverb":"ser é era foi são eram será sendo sido estar está estava estão estamos tá ter tem tinha têm temos haver há havia havido vai vou vamos vão ir foram seria teria".split(),
"conj":"e mas ou porque que se como quando então pois porém contudo todavia embora enquanto portanto logo assim nem ainda além".split(),
"negate":"não nunca jamais nada ninguém nenhum nenhuma nem tampouco".split(),
"quant":"muito muitos muita muitas pouco poucos mais menos tanto tantos vários várias bastante demais cada ambos meio".split(),
"adverb":"aqui ali lá cá agora já sempre hoje ontem amanhã bem mal assim talvez também só apenas depois antes sim onde".split(),
}
FWSET={k:set(v) for k,v in FW.items()}
CONN=set("e mas ou porque portanto então porém contudo todavia assim logo pois enquanto quando embora apesar além disso ou seja por isso no entanto entretanto dado que para que a fim de caso se que como porém".split())

WORD=re.compile(r"[a-zà-ÿ]+")
def toks(s): return WORD.findall(str(s).lower())

def shannon(counts):
    n=sum(counts.values())
    if n==0: return 0.0
    return -sum((c/n)*np.log2(c/n) for c in counts.values())

def mtld_one(tokens,thr=0.72):
    if len(tokens)<10: return np.nan
    def run(seq):
        factors=0; types=set(); n=0
        for w in seq:
            types.add(w); n+=1; ttr=len(types)/n
            if ttr<=thr:
                factors+=1; types=set(); n=0
        if n>0: factors+= (1-ttr)/(1-thr)
        return len(seq)/factors if factors>0 else np.nan
    a=run(tokens); b=run(tokens[::-1])
    return np.nanmean([a,b])

def lsm_pair(ta,tb):
    if not ta or not tb: return np.nan
    ca,cb=Counter(ta),Counter(tb); na,nb=len(ta),len(tb)
    vals=[]
    for k,s in FWSET.items():
        pa=sum(ca[w] for w in s if w in ca)/na
        pb=sum(cb[w] for w in s if w in cb)/nb
        if pa+pb>0: vals.append(1-abs(pa-pb)/(pa+pb))
    return np.nanmean(vals) if vals else np.nan

def det_from_R(R,lmin=2):
    n=R.shape[0]
    iu=np.triu_indices(n,1); rec=int(R[iu].sum())
    if rec==0: return 0.0,0.0
    tot=0
    for off in range(1,n):
        d=np.diagonal(R,off); run=0
        for v in d:
            if v: run+=1
            else:
                if run>=lmin: tot+=run
                run=0
        if run>=lmin: tot+=run
    return 100.0*tot/rec, 100.0*rec/len(iu[0])  # %DET, %REC

rows=[]
for f in sorted(glob.glob(str(TXT/"*_transcript.csv"))):
    mid=os.path.basename(f).replace("_transcript.csv","")
    gp=GM/f"{mid}_gorman.csv"
    if not gp.exists(): continue
    df=pd.read_csv(f).reset_index(drop=True)
    df["onset"]=pd.to_numeric(df["onset_seconds"],errors="coerce")
    df=df.dropna(subset=["onset"]).reset_index(drop=True)
    df["tok"]=df["text"].apply(toks)
    df["nw"]=df["tok"].apply(len).clip(lower=1)
    df["offset"]=df["onset"]+0.5*df["nw"]
    df["bin"]=(df["onset"]//WIN*WIN).astype(int)
    # meeting-level TF-IDF (idf shared) on utterances with >=1 token
    texts=[" ".join(t) for t in df["tok"]]
    vec=TfidfVectorizer(token_pattern=r"[a-zà-ÿ]+",min_df=1)
    try: X=vec.fit_transform(texts)
    except ValueError: continue
    Xn=X.toarray()
    norms=np.linalg.norm(Xn,axis=1,keepdims=True); norms[norms==0]=1
    Xu=Xn/norms
    # pairwise turn-to-turn coherence / novelty / lsm / latency
    coh=np.full(len(df),np.nan); nov=np.full(len(df),np.nan); lsmv=np.full(len(df),np.nan); lat=np.full(len(df),np.nan)
    for i in range(1,len(df)):
        coh[i]=float(Xu[i]@Xu[i-1])
        k0=max(0,i-5); nov[i]=1-max((float(Xu[i]@Xu[j]) for j in range(k0,i)),default=0.0)
        lsmv[i]=lsm_pair(df["tok"][i],df["tok"][i-1])
        lat[i]=df["onset"][i]-df["offset"][i-1]
    df["coh"]=coh; df["nov"]=nov; df["lsm"]=lsmv; df["lat"]=lat
    # reorg metrics aggregated to 90s bins
    g=pd.read_csv(gp); g["bin"]=(g["second"]//WIN*WIN).astype(int)
    gagg=g.groupby("bin")[["entropy_g","det_g","rmse_g"]].mean()
    # per-window text features
    for b,sub in df.groupby("bin"):
        if b not in gagg.index or len(sub)<3: continue
        idx=sub.index.to_numpy()
        alltok=[w for t in sub["tok"] for w in t]
        cnt=Counter(alltok); ntok=len(alltok)
        # semantic recurrence on this window's utterance vectors
        V=Xu[idx]; Rsim=V@V.T; R=(Rsim>=0.15).astype(int); np.fill_diagonal(R,0)
        sdet,srec=det_from_R(R)
        # structural
        sp=sub["speaker_id"].to_numpy()
        trans=Counter(zip(sp[:-1],sp[1:])); tent=shannon(trans)
        # cohmetrix subset
        conn=sum(1 for w in alltok if w in CONN)/max(1,ntok)
        # content overlap between adjacent utterances (content = non-function tokens)
        FWall=set().union(*FWSET.values())
        def content(t): return set(w for w in t if w not in FWall and len(w)>3)
        ov=[]
        toklist=list(sub["tok"])
        for i in range(1,len(toklist)):
            a,bb=content(toklist[i-1]),content(toklist[i])
            if a or bb: ov.append(len(a&bb)/max(1,len(a|bb)))
        rows.append(dict(mid=mid,bin=int(b),
            entropy_g=gagg.loc[b,"entropy_g"],det_g=gagg.loc[b,"det_g"],rmse_g=gagg.loc[b,"rmse_g"],
            sem_det=sdet,sem_rec=srec,
            coh=np.nanmean(sub["coh"]),nov=np.nanmean(sub["nov"]),
            word_entropy=shannon(cnt),ttr=len(cnt)/max(1,ntok),mtld=mtld_one(alltok),
            hapax=sum(1 for c in cnt.values() if c==1)/max(1,len(cnt)),
            lsm=np.nanmean(sub["lsm"]),
            turn_len=sub["nw"].mean(),latency=np.nanmean(sub["lat"]),
            transition_entropy=tent,n_turns=len(sub),
            connective=conn,content_overlap=np.nanmean(ov) if ov else np.nan,
            words_per_turn=sub["nw"].mean()))
    print(f"  {mid}: windows={sum(1 for r in rows if r['mid']==mid)}",flush=True)
out=pd.DataFrame(rows)
out.to_csv("triangulation_windows.csv",index=False)
print(f"\nsaved triangulation_windows.csv  rows={len(out)}  meetings={out.mid.nunique()}")
print(out.describe().loc[['mean','std','min','max']].round(3).T.to_string())
