from __future__ import annotations

from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingBackend:
        """Simple embedding backend using a local sentence-transformers model.

        We always use the `all-MiniLM-L6-v2` model so the RAG stack works fully
        offline and does not depend on any external embedding API.
        """

        def __init__(self) -> None:
                self._local_model: SentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")

        async def embed_documents(self, texts: List[str]) -> List[List[float]]:
            vectors = self._local_model.encode(texts, show_progress_bar=False)
            return [v.tolist() for v in vectors]  # type: ignore[return-value]

        async def embed_query(self, text: str) -> List[float]:
            return (await self.embed_documents([text]))[0]
