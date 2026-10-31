"""Local per-utterance features (NOT for distribution; derived from transcript text).
Sentiment: pysentimiento/bertweet-pt-sentiment (Pérez et al., 2021; trained on Portuguese tweets, so domain shift
applies): probabilities NEG / NEU / POS.
Function-word classes for language style matching (Ireland & Pennebaker, 2010), from spaCy pt_core_news_sm tags:
personal pronouns, impersonal pronouns, articles, conjunctions, prepositions, auxiliary verbs, adverbs, negations,
quantifiers; plus token count. Output: data/semantic_cache/<mid>_feat.npz"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
import torch, spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification
CACHE = f"{CM.L}/data/semantic_cache"; dev = "mps" if torch.backends.mps.is_available() else "cpu"
name = "pysentimiento/bertweet-pt-sentiment"; tokz = AutoTokenizer.from_pretrained(name); mdl = AutoModelForSequenceClassification.from_pretrained(name).to(dev).eval()
labels = [mdl.config.id2label[i] for i in range(mdl.config.num_labels)]
nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])
NEG = {"não", "nao", "nunca", "nem", "jamais", "nada", "ninguém"}; QNT = {"muito", "pouco", "todo", "toda", "todos", "todas", "algum", "alguma", "nenhum", "nenhuma", "mais", "menos", "vários", "várias", "bastante", "cada"}
CATS = ["ppron", "ipron", "article", "conj", "prep", "auxverb", "adverb", "negate", "quant"]
def classes(doc):
    c = dict.fromkeys(CATS, 0); n = 0
    for t in doc:
        if not t.is_alpha: continue
        n += 1; low = t.text.lower(); pt = t.morph.get("PronType")
        if t.pos_ == "PRON": c["ppron" if "Prs" in pt else "ipron"] += 1
        if t.pos_ == "DET" and "Art" in pt: c["article"] += 1
        if t.pos_ in ("CCONJ", "SCONJ"): c["conj"] += 1
        if t.pos_ == "ADP": c["prep"] += 1
        if t.pos_ == "AUX": c["auxverb"] += 1
        if t.pos_ == "ADV" and low not in NEG: c["adverb"] += 1
        if low in NEG: c["negate"] += 1
        if low in QNT: c["quant"] += 1
    return [c[k] for k in CATS] + [n]
for m in CM.meetings():
    out = f"{CACHE}/{m}_feat.npz"
    if os.path.exists(out): continue
    tx = CM.transcript(m); texts = tx[tx.text.notna()].text.astype(str).tolist(); probs = []
    with torch.no_grad():
        for i in range(0, len(texts), 32):
            enc = tokz(texts[i:i + 32], padding=True, truncation=True, max_length=128, return_tensors="pt").to(dev)
            probs.append(torch.softmax(mdl(**enc).logits, -1).cpu().numpy())
    P = np.vstack(probs); F = np.array([classes(d) for d in nlp.pipe(texts, batch_size=64)])
    np.savez_compressed(out, sent=P, sent_labels=np.array(labels), fw=F, fw_labels=np.array(CATS + ["ntok"]))
    print(m, len(texts), "mean", dict(zip(labels, P.mean(0).round(3))), flush=True)
