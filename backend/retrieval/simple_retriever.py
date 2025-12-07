from __future__ import annotations

from typing import List


# Toy in-memory corpus mimicking Pratt handbook excerpts.
_CORPUS: List[str] = [
    "ECE majors must complete a set of core courses including EGR 103, MATH 218D or equivalent, PHYSICS 152L, and ECE 110L before taking most upper-level ECE electives.",
    "Pratt students may request an overload above 5.5 credits only if they have a strong academic record and approval from their academic dean. First-year students are rarely approved for overloads.",
    "Study abroad courses may count toward Pratt major requirements if pre-approved through the global education office and your director of undergraduate studies. Students should plan ahead to ensure core sequences like math and physics stay on track.",
    "Mechanical Engineering majors typically complete a sequence of design courses, culminating in a senior capstone. At least two technical electives must be in advanced ME topics.",
    "Electrical & Computer Engineering students must complete a minimum number of ECE electives at the 3xx level or above, including at least one course with a substantial design component.",
]


def _simple_keyword_score(query: str, text: str) -> float:
    """Very naive similarity: count overlapping lowercase tokens.

    This is intentionally simple but structured so it can later be replaced by
    a proper embedding-based similarity function.
    """

    q_tokens = set(query.lower().split())
    t_tokens = set(text.lower().split())
    if not q_tokens:
        return 0.0
    overlap = q_tokens.intersection(t_tokens)
    return len(overlap) / len(q_tokens)


async def retrieve(question: str, intent: str, k: int = 5) -> List[str]:
    """Retrieve up to k handbook-like chunks relevant to the question.

    For now this uses a trivial keyword overlap score over a small, hardcoded
    corpus. In the future, this function will use embeddings and a vector
    index built from the real Pratt handbooks placed under backend/data.
    """

    scored = [(_simple_keyword_score(question, chunk), chunk) for chunk in _CORPUS]
    scored.sort(key=lambda x: x[0], reverse=True)
    top_chunks = [c for s, c in scored if s > 0][:k]

    # Fallback: if nothing overlaps, just return the first few chunks
    if not top_chunks:
        top_chunks = _CORPUS[: min(k, len(_CORPUS))]

    return top_chunks
