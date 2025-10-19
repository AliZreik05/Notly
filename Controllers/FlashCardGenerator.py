import re
from typing import List
from Schemas.Flashcards import FlashcardRequest, FlashcardResponse, Flashcard

def _split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n|(?:\r?\n){2,}", text or "") if p.strip()]

def _from_bullets(bullets: List[str], cap: int) -> List[Flashcard]:
    cards: List[Flashcard] = []
    for b in bullets:
        b = (b or "").strip()
        if not b:
            continue
        if ":" in b:
            head, rest = b.split(":", 1)
            q = head.strip().rstrip("?") + "?"
            a = rest.strip() or b
        else:
            words = b.split()
            head = " ".join(words[:6]) if words else "Term"
            q = f"What is {head}?"
            a = b
        cards.append(Flashcard(front=q, back=a))
        if len(cards) >= cap:
            break
    return cards

def _from_text(text: str, cap: int) -> List[Flashcard]:
    cards: List[Flashcard] = []
    text = text or ""

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for i, ln in enumerate(lines):
        if ln.endswith(":") or len(ln.split()) <= 6:
            ans = " ".join(lines[i+1:i+4]).strip()
            if ans:
                cards.append(Flashcard(front=ln.rstrip(":") + "?", back=ans))
        if len(cards) >= cap:
            return cards

    sents = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    for s in sents:
        s = s.strip()
        if len(s.split()) > 8:
            q = "What is " + " ".join(s.split()[:6]) + "?"
            cards.append(Flashcard(front=q, back=s))
            if len(cards) >= cap:
                return cards

    for p in _split_paragraphs(text):
        head = " ".join(p.split()[:6]) or "this topic"
        cards.append(Flashcard(front=f"Explain: {head}…", back=p))
        if len(cards) >= cap:
            break
    return cards

def generate_flashcards(payload: FlashcardRequest) -> FlashcardResponse:
    items: List[Flashcard] = []
    if payload.bullets:
        items.extend(_from_bullets(payload.bullets, payload.max_cards))
    if payload.source_text and len(items) < payload.max_cards:
        remaining = payload.max_cards - len(items)
        items.extend(_from_text(payload.source_text, remaining))
    return FlashcardResponse(items=items[:payload.max_cards])