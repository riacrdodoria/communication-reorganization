"""Local per-utterance emotion probabilities (NOT for distribution). pysentimiento/bert-pt-emotion: 28 GoEmotions
categories (Demszky et al., 2020) in Portuguese, multi-label (sigmoid). Domain shift: trained on social-media text.
Output: data/semantic_cache/<mid>_emo.npz"""
import sys, os, numpy as np, torch
sys.path.insert(0, os.path.dirname(__file__)); import common as CM
from transformers import AutoTokenizer, AutoModelForSequenceClassification
CACHE = f"{CM.L}/data/semantic_cache"; dev = "mps" if torch.backends.mps.is_available() else "cpu"
name = "pysentimiento/bert-pt-emotion"; tk = AutoTokenizer.from_pretrained(name); md = AutoModelForSequenceClassification.from_pretrained(name).to(dev).eval()
labels = [md.config.id2label[i] for i in range(md.config.num_labels)]
for m in CM.meetings():
    out = f"{CACHE}/{m}_emo.npz"
    if os.path.exists(out): continue
    tx = CM.transcript(m); texts = tx[tx.text.notna()].text.astype(str).tolist(); P = []
    with torch.no_grad():
        for i in range(0, len(texts), 32):
            enc = tk(texts[i:i + 32], padding=True, truncation=True, max_length=128, return_tensors="pt").to(dev); P.append(torch.sigmoid(md(**enc).logits).cpu().numpy())
    P = np.vstack(P); np.savez_compressed(out, emo=P, labels=np.array(labels))
    top = np.argsort(-P.mean(0))[:4]; print(m, {labels[k]: round(float(P.mean(0)[k]), 3) for k in top}, flush=True)
