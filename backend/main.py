from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import get_settings
from .models import ChatRequest, ChatResponse, SourceChunk
from .openrouter_client import OpenRouterClient
from .rag_pipeline import (
    classify_intent,
    generate_answer,
    retrieve_context,
    retrieve_fewshot_examples,
)
from .rag.embeddings import EmbeddingBackend
from .rag.vector_store import VectorStore
from .rag.retriever import Retriever

app = FastAPI(title="Duke Pratt Degree & Course Planning Chatbot API")


# Global RAG components initialised at startup. These are lightweight wrappers
# around a persistent Chroma index built by backend/rag/ingest.py.
_embedding_backend = EmbeddingBackend()
_vector_store = VectorStore(
    persist_dir=Path(__file__).resolve().parent / ".chroma",
)
_retriever = Retriever(store=_vector_store, embedding_backend=_embedding_backend)

# Serve raw context documents (CSVs, PDFs) so the frontend can
# open a "View source" link for retrieved chunks.
CONTEXT_DOCS_DIR = Path(__file__).resolve().parent.parent / "ContextDocuments"
app.mount(
    "/context-docs",
    StaticFiles(directory=CONTEXT_DOCS_DIR),
    name="context-docs",
)

# CORS so the Vite dev server (and later production frontend) can call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_llm_client() -> OpenRouterClient:
    """Construct an OpenRouter client using environment-based settings."""

    # OpenRouterClient itself pulls from get_settings(), and will raise a
    # clear error if the key is truly missing. The chat endpoint performs a
    # separate guard using get_settings() as well.
    return OpenRouterClient()


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint consumed by the React frontend.

    Pipeline:
      1. Classify intent from the latest user message.
      2. Retrieve a small set of handbook-like chunks.
      3. Call the LLM with a RAG-style prompt.
    """

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message must not be empty.")

    # If no OpenRouter key is configured, return a deterministic placeholder
    # response so the frontend can still exercise the full request/response
    # flow without any external dependencies.
    current_settings = get_settings()
    if not current_settings.openrouter_api_key:
        docs = await retrieve_context(
            retriever=_retriever,
            question=request.message,
            pratt_profile=request.prattProfile,
            intent="other",
            k=3,
        )
        retrieved_chunks = [d.text for d in docs]
        sources: list[SourceChunk] = []
        for d in docs:
            meta = d.metadata or {}
            sources.append(
                SourceChunk(
                    text=d.text,
                    source_file=meta.get("source_file"),
                    page=meta.get("page"),
                    chunk_index=meta.get("chunk_index"),
                    type=meta.get("type"),
                )
            )
        return ChatResponse(
            reply=(
                "This is a placeholder backend response. No OpenRouter API key is "
                "configured yet, so I am not calling a real model. "
                "Once credentials are added, I will use Pratt handbook "
                "context and a GPT-style model to answer more precisely."
            ),
            retrieved_chunks=retrieved_chunks,
            sources=sources,
            metadata={"intent": "other", "intent_confidence": 0.0, "using_model": False},
        )

    llm = _get_llm_client()

    try:
        intent_result = await classify_intent(llm, request.message)
        docs = await retrieve_context(
            retriever=_retriever,
            question=request.message,
            pratt_profile=request.prattProfile,
            intent=intent_result.intent,
            k=5,
        )
        retrieved_chunks = [d.text for d in docs]
        sources: list[SourceChunk] = []
        for d in docs:
            meta = d.metadata or {}
            sources.append(
                SourceChunk(
                    text=d.text,
                    source_file=meta.get("source_file"),
                    page=meta.get("page"),
                    chunk_index=meta.get("chunk_index"),
                    type=meta.get("type"),
                )
            )

        fewshot_docs = await retrieve_fewshot_examples(
            retriever=_retriever,
            question=request.message,
            pratt_profile=request.prattProfile,
            k=2,
        )
        # Expose few-shot example texts alongside main context so the
        # frontend can optionally display them for debugging/demo.
        fewshot_chunks = [d.text for d in fewshot_docs]
        response = await generate_answer(
            llm,
            request,
            retrieved_chunks,
            intent=intent_result.intent,
            fewshot_chunks=fewshot_chunks,
        )
        response.sources = sources
        if fewshot_chunks:
            # Hard-cap what we expose so the frontend dropdown only
            # shows the top 2 few-shot examples actually used.
            response.metadata.setdefault("fewshot_chunks", fewshot_chunks[:2])
        # Attach more metadata if needed
        response.metadata.setdefault("intent_confidence", intent_result.confidence)
        response.metadata.setdefault("using_model", True)
        return response
    except Exception as exc:  # pragma: no cover - generic safety net
        raise HTTPException(status_code=500, detail=f"Chat pipeline failed: {exc}")
