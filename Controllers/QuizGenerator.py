from typing import List
import random
import re

from Schemas.QuizGenerator import QuizRequest, QuizResponse, QuizItem


_DEF_DISTRACTORS = [
    "None of the above",
    "All of the above",
    "Not enough information",
    "It depends",
]

def _sentences_from_text(text: str) -> List[str]:
    # Naive sentence split
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 10]

def _make_question_from_sentence(s: str, difficulty: str) -> QuizItem:
    """
    Turn a sentence into a simple factual question by masking a noun-ish word.
    Super lightweight placeholder; swap with an LLM later if desired.
    """
    words = s.split()
    if len(words) < 6:
        # fallback generic Q
        q = f"What is the main idea of: \"{s[:120]}\"?"
        correct = "The central point of the sentence"
        distractors = random.sample(_DEF_DISTRACTORS, k=min(3, len(_DEF_DISTRACTORS)))
        options = [correct] + distractors
        random.shuffle(options)
        answer_index = options.index(correct)
        return QuizItem(question=q, options=options, answer_index=answer_index, explanation=s)

    idx = len(words) // 2
    answer = re.sub(r'[^\w\-]+', '', words[idx]) or "term"
    masked = words.copy()
    masked[idx] = "_____"
    q = "Fill in the blank: " + " ".join(masked)

    pool = set()
    for w in words:
        wclean = re.sub(r'[^\w\-]+', '', w)
        if wclean and wclean.lower() != answer.lower():
            pool.add(wclean)
    pool = list(pool)

    distractors = []
    random.shuffle(pool)
    for w in pool:
        if len(distractors) >= 3:
            break
        if w.lower() != answer.lower():
            distractors.append(w)

    for d in _DEF_DISTRACTORS:
        if len(distractors) >= 3:
            break
        if d not in distractors and d.lower() != answer.lower():
            distractors.append(d)

    options = [answer] + distractors[:3]
    random.shuffle(options)
    answer_index = options.index(answer)

    exp = f"The missing word was '{answer}'. Original: {s}"
    return QuizItem(question=q, options=options, answer_index=answer_index, explanation=exp)

def _fallback_questions(topic: str, n: int, difficulty: str) -> List[QuizItem]:
    base = [
        ("Which statement best describes {}?", [
            f"A core concept related to {topic}",
            f"An unrelated concept to {topic}",
            "A historical anecdote",
            "A statistical artifact",
        ], 0),
        ("What is a common application of {}?", [
            f"Real-world use case of {topic}",
            "Rarely used technique",
            "Purely fictional scenario",
            "Deprecated practice",
        ], 0),
        ("Which of the following is TRUE about {}?", [
            f"Key fact about {topic}",
            "Misconception about it",
            "Unsupported claim",
            "Irrelevant detail",
        ], 0),
    ]
    items: List[QuizItem] = []
    for i in range(n):
        template = base[i % len(base)]
        q = template[0].format(topic)
        options = template[1].copy()
        random.shuffle(options)
        correct = [o for o in template[1] if topic in o or "TRUE" in template[0] or "core" in o][0]
        answer_index = options.index(correct) if correct in options else 0
        items.append(QuizItem(question=q, options=options, answer_index=answer_index, explanation=f"Topic: {topic}"))
    return items


def generate_quiz(payload: QuizRequest) -> QuizResponse:
    rnd = random.Random(42) 
    items: List[QuizItem] = []
    if payload.source_text:
        sentences = _sentences_from_text(payload.source_text)
        rnd.shuffle(sentences)
        selected = sentences[:payload.num_questions] if sentences else []
        for s in selected:
            items.append(_make_question_from_sentence(s, payload.difficulty))

    if len(items) < payload.num_questions and payload.topic:
        items.extend(_fallback_questions(payload.topic, payload.num_questions - len(items), payload.difficulty))

    if not items:
        items = _fallback_questions(payload.topic or "the topic", payload.num_questions, payload.difficulty)

    return QuizResponse(items=items, message="Quiz generated successfully")
