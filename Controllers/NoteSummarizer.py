import re
from collections import Counter
from typing import List, Tuple

_STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while","for","to",
    "from","of","in","on","at","by","with","as","is","are","was","were","be","been",
    "being","it","its","this","that","these","those","i","you","he","she","we","they",
    "them","me","my","our","your","their","not","no","so","too","very","can","could",
    "should","would","may","might","will","just","than","also","into","about","over",
    "under","again","once","because","what","which","who","whom","where","why","how"
}

_SENT_SPLIT_REGEX = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')  # simple sentence splitter
_WORD_REGEX = re.compile(r"[A-Za-z0-9']+")

def _split_sentences(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    parts = _SENT_SPLIT_REGEX.split(text)
    return [s.strip() for s in parts if s.strip()]

def _tokenize(sentence: str) -> List[str]:
    return [w.lower() for w in _WORD_REGEX.findall(sentence)]

def _build_frequency(sentences: List[str]) -> Counter:
    c = Counter()
    for s in sentences:
        for w in _tokenize(s):
            if w not in _STOPWORDS and len(w) > 1:
                c[w] += 1
    if not c:
        return c
    max_f = max(c.values())
    for k in list(c.keys()):
        c[k] = c[k] / max_f
    return c

def _score_sentence(sentence: str, freq: Counter) -> float:
    tokens = _tokenize(sentence)
    if not tokens:
        return 0.0
    score = sum(freq.get(t, 0.0) for t in tokens)
    return score / (1 + len(tokens) ** 0.25)

def summarize_text(text: str, max_sentences: int = 3) -> Tuple[str, List[str]]:
    sentences = _split_sentences(text)
    if not sentences:
        return "", []

    if len(sentences) <= max_sentences:
        return " ".join(sentences), sentences

    freq = _build_frequency(sentences)
    scored = [(i, s, _score_sentence(s, freq)) for i, s in enumerate(sentences)]
    top = sorted(scored, key=lambda x: x[2], reverse=True)[:max_sentences]
    top_sorted = [s for _, s, _ in sorted(top, key=lambda x: x[0])]
    return " ".join(top_sorted), top_sorted
