from __future__ import annotations

from typing import List, Optional, Dict, Any

from .openrouter_client import OpenRouterClient
from .models import ChatRequest, ChatResponse, IntentResult, PrattProfile
from .rag.retriever import Retriever


INTENT_LABELS = [
    "major_requirements",
    "prerequisites_sequencing",
    "study_abroad_transfer",
    "overload_registration",
    "other",
]


async def classify_intent(llm: OpenRouterClient, question: str) -> IntentResult:
    """Use the LLM to classify a question into one of a few labels.

    This is a small, cheap call that returns just the label and a rough
    confidence score based on how strongly the model expressed its choice.
    """

    system_prompt = (
        "You are an intent classification assistant for a Duke Pratt School of Engineering "
        "advising chatbot. Classify the student's question into exactly ONE of these labels: "
        f"{', '.join(INTENT_LABELS)}. "
        "Respond with only the label, no extra words."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    raw = await llm.chat(messages, temperature=0.0)
    label = raw.strip().split()[0]
    if label not in INTENT_LABELS:
        label = "other"
    # Confidence is heuristic here; could be improved later.
    return IntentResult(intent=label, confidence=0.7)


async def retrieve_context(
    retriever: Retriever,
    question: str,
    pratt_profile: Optional[PrattProfile],
    intent: str,
    k: int = 5,
) -> List[str]:
    """Retrieve RAG context for a question using the real vector store."""

    docs = await retriever.retrieve(
        question=question,
        pratt_profile=pratt_profile,
        intent=intent,
        k=k,
    )

    return [d.text for d in docs]


async def retrieve_fewshot_examples(
    retriever: Retriever,
    question: str,
    pratt_profile: Optional[PrattProfile],
    k: int = 3,
) -> List[str]:
    """Retrieve few-shot example chunks to guide answer style/structure.

    These come from documents tagged with type="fewshot_example" and are not
    constrained by major so that global examples can be reused.
    """

    docs = await retriever.retrieve(
        question=question,
        pratt_profile=pratt_profile,
        intent=None,
        k=k,
        type_filter="fewshot_example",
    )

    return [d.text for d in docs]


async def generate_answer(
    llm: OpenRouterClient,
    request: ChatRequest,
    retrieved_chunks: List[str],
    intent: str,
    fewshot_chunks: Optional[List[str]] = None,
) -> ChatResponse:
    """Call the LLM with a RAG-style prompt to generate an answer.

    The prompt includes:
    - System description of the assistant
    - PrattProfile summary
    - Retrieved handbook/course context
    - Retrieved few-shot example patterns
    - Recent conversation history
    - Current question and intent
    """

    profile = request.prattProfile
    if profile:
        profile_summary = (
            "Pratt student profile:\n"
            f"- Major: {profile.major or 'unspecified'}\n"
            f"- Class year: {profile.classYear or 'unspecified'}\n"
            f"- Current / target semester: {profile.semester or 'unspecified'}\n"
            f"- Current courses: {', '.join(profile.currentCourses) or 'unspecified'}\n"
            f"- Completed core / prereqs: {', '.join(profile.completedCourses) or 'unspecified'}\n"
        )
    else:
        profile_summary = "Pratt student profile is not provided."

    handbook_block = "\n\n".join(
        f"[{i+1}] {chunk}" for i, chunk in enumerate(retrieved_chunks)
    ) or "(no handbook/course excerpts available)"

    fewshot_block = ""
    if fewshot_chunks:
        fewshot_block = "\n\n".join(
            f"Example {i+1}:\n{chunk}" for i, chunk in enumerate(fewshot_chunks)
        )

    system_prompt = (
        "You are an advising assistant for Duke's Pratt School of Engineering students. "
        "You focus on the 5 Pratt majors and help with degree requirements, course sequencing, "
        "prerequisites, study abroad planning, and overload rules.\n\n"
        "Use the provided handbook-like excerpts and example advising interactions as your primary sources of truth. "
        "If the excerpts do not clearly answer the question, be explicit about the uncertainty "
        "and recommend that the student confirm details in the official handbook or with their academic dean. "
        "Be concise, structured, and student-friendly."
    )

    # Map recent history into chat messages (for conversational memory)
    history_messages: List[Dict[str, Any]] = []
    for msg in (request.history or [])[-6:]:
        role = msg.role
        if role not in {"user", "assistant"}:
            continue
        history_messages.append({"role": role, "content": msg.content})

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": profile_summary},
        {
            "role": "system",
            "content": (
                "Here are relevant handbook/course excerpts that may help answer the student's question. "
                "Treat them as context, not verbatim policy:\n\n" + handbook_block
            ),
        },
    ]

    if fewshot_block:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Here are example advising interactions (few-shot examples). "
                    "Use their style and structure as a pattern for your answer:\n\n"
                    + fewshot_block
                ),
            }
        )

    messages.extend(history_messages)

    messages.append(
        {
            "role": "user",
            "content": (
                f"Student intent category: {intent}.\n\n"
                f"Student question: {request.message}"
            ),
        }
    )

    reply = await llm.chat(messages, temperature=0.2)

    return ChatResponse(
        reply=reply.strip(),
        retrieved_chunks=retrieved_chunks,
        metadata={
            "intent": intent,
            "prompt_messages": messages,
        },
    )
