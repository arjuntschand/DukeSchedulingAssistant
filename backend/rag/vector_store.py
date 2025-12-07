from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from .schema import Document
from .embeddings import EmbeddingBackend


class VectorStore:
    """Thin wrapper around a persistent Chroma collection."""

    def __init__(self, persist_dir: Path, collection_name: str = "pratt_rag") -> None:
        self._persist_dir = persist_dir
        self._client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def add_documents(self, docs: List[Document], embeddings: List[List[float]]) -> None:
        ids = [d.id for d in docs]
        texts = [d.text for d in docs]
        metadatas = [d.to_metadata() for d in docs]

        self._collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    async def similarity_search(
        self,
        embedding_backend: EmbeddingBackend,
        query: str,
        k: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        # Embed the query using the same backend used at ingestion time
        q_embedding = await embedding_backend.embed_query(query)

        results = self._collection.query(
            query_embeddings=[q_embedding],
            n_results=k,
            where=where or {},
        )

        docs: List[Document] = []
        ids = results.get("ids", [[]])[0]
        texts = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for doc_id, text, metadata in zip(ids, texts, metadatas):
            metadata = metadata or {}
            docs.append(
                Document(
                    id=str(doc_id),
                    major=metadata.get("major"),
                    type=metadata.get("type", "unknown"),
                    code=metadata.get("code"),
                    title=metadata.get("title"),
                    text=text,
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in {"major", "type", "code", "title"}
                    },
                )
            )

        return docs
