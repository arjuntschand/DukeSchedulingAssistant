from __future__ import annotations

from typing import List, Optional

from sentence_transformers import SentenceTransformer

from ..config import get_settings
from ..llm_client import LLMClient


class EmbeddingBackend:
    """Abstraction over local and OpenAI embeddings.

    - If OPENAI_API_KEY and OPENAI_EMBEDDING_MODEL are set, uses OpenAI
      embeddings via LLMClient.
    - Otherwise, falls back to a local sentence-transformers model
      (all-MiniLM-L6-v2) so the RAG stack works fully offline.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._openai_embedding_model: Optional[str] = settings.openai_embedding_model
        self._openai_api_key: Optional[str] = settings.openai_api_key

        self._openai_client: Optional[LLMClient] = None
        if self._openai_api_key and self._openai_embedding_model:
            self._openai_client = LLMClient(
                api_key=self._openai_api_key,
                chat_model=settings.openai_chat_model,
                embedding_model=self._openai_embedding_model,
            )

        # Local model is always available as a fallback
        self._local_model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self._openai_client and self._openai_embedding_model:
            # Use OpenAI embeddings when configured
            return await self._openai_client.embed(texts)

        # Local embedding fallback
        vectors = self._local_model.encode(texts, show_progress_bar=False)
        return [v.tolist() for v in vectors]  # type: ignore[return-value]

    async def embed_query(self, text: str) -> List[float]:
        return (await self.embed_documents([text]))[0]
