"""Local cache for the semantic topic analyses (NOT for distribution: derived from transcript text).
Per meeting: utterance onsets, speakers, word counts; sentence embeddings (paraphrase-multilingual-MiniLM-L12-v2,
L2-normalized; Reimers & Gurevych, 2019, 2020); content lemmas (spaCy pt_core_news_sm: NOUN, PROPN, VERB, ADJ; not
stopwords; >= 3 characters); cue-phrase flag (utterance opens with a Portuguese topic-transition marker).
Output: ~/lsh-work/data/semantic_cache/<mid>.npz and <mid>_lemmas.json (local only)."""
import sys, os, re, json, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import common as C
from sentence_transformers import SentenceTransformer
import spacy
OUT = f"{C.L}/data/semantic_cache"; os.makedirs(OUT, exist_ok=True)
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="mps")
nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])
SW = set(w.strip().lower() for w in open(f"{C.L}/data/stopwords-pt.txt", encoding="utf-8") if w.strip())
CUE = re.compile(r"^\W*(ent[aã]o|bom|beleza|agora|pr[oó]xim[oa]|vamos (para|pro|pra|falar)|passando|mudando de assunto|outro ponto|outra coisa|"
                 r"o seguinte|ok|t[aá] bom|pronto|enfim|falando nisso|voltando|deixa eu|e a[ií]|e sobre|sobre o|sobre a|com rela[cç][aã]o)\b", re.I)
for mid in C.meetings():
    if os.path.exists(f"{OUT}/{mid}.npz"): continue
    tx = C.transcript(mid); tx = tx[tx.text.notna()].reset_index(drop=True); texts = tx.text.astype(str).tolist()
    E = model.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    lem = [[t.lemma_.lower() for t in d if t.pos_ in ("NOUN", "PROPN", "VERB", "ADJ") and len(t.lemma_) >= 3 and t.lemma_.lower() not in SW and t.is_alpha]
           for d in nlp.pipe(texts, batch_size=64)]
    nw = np.array([len(t.split()) for t in texts]); cue = np.array([bool(CUE.match(t)) for t in texts])
    np.savez_compressed(f"{OUT}/{mid}.npz", onset=tx.onset_seconds.to_numpy(float), speaker=tx.speaker_id.astype(str).to_numpy(), nw=nw, emb=E.astype(np.float32), cue=cue)
    json.dump(lem, open(f"{OUT}/{mid}_lemmas.json", "w"), ensure_ascii=False)
    print(mid, len(texts), "utterances; cue share", round(cue.mean(), 3), flush=True)
