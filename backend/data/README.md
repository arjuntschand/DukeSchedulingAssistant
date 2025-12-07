# Pratt Handbook Data (Placeholder)

This directory is reserved for the real Pratt School of Engineering degree
handbooks and related advising documents.

In the future, an ingestion script (e.g. `ingest_handbooks.py`) will:

- Load the 5 Pratt major handbooks (PDF or HTML).
- Chunk them into smaller text passages.
- Create vector embeddings for each chunk.
- Store the resulting vectors and metadata in a local file-based index or a
  dedicated vector database.

For now, the backend uses a small, hardcoded toy corpus in
`backend/retrieval/simple_retriever.py` to simulate handbook excerpts.
