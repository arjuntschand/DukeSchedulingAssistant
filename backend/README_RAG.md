# Pratt RAG Pipeline

This backend includes a real retrieval-augmented generation (RAG) stack over the CSV context documents in `ContextDocuments/`.

## Overview

- **Documents**: Each row in the context CSVs (e.g. `BME_classes.csv`, `CEE_classes.csv`) is converted into a structured `Document` (`backend/rag/schema.py`) with fields like `major`, `code`, `title`, and `text` (course descriptions, policies, requirements).
- **Embeddings**: We embed each document using `EmbeddingBackend` (`backend/rag/embeddings.py`).
  - If `OPENAI_API_KEY` and `OPENAI_EMBEDDING_MODEL` are configured, we use OpenAI embeddings via the existing `LLMClient`.
  - Otherwise, we fall back to a local sentence-transformers model (`all-MiniLM-L6-v2`) so the stack works offline.
- **Vector store**: Embeddings and metadata are stored in a persistent Chroma collection via `VectorStore` (`backend/rag/vector_store.py`), under `backend/.chroma/`.
- **Retriever**: The `Retriever` (`backend/rag/retriever.py`) performs metadata-aware similarity search, using the student's Pratt profile (major, year, semester, current/completed courses) and the model-classified intent to filter the index.
- **Chat pipeline**: `backend/rag_pipeline.py` orchestrates intent classification, retrieval, and answer generation. `backend/main.py` wires this into the `/api/chat` endpoint.

## Ingestion: building the vector index

Before using the RAG stack, ingest the CSV documents into the vector store.

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run ingestion (loads CSVs from ContextDocuments/, computes embeddings, writes Chroma index)
python -m rag.ingest
```

This will:

1. Read all `*.csv` files in `ContextDocuments/` (`load_context_documents` in `backend/rag/ingest.py`).
2. Convert each row into a `Document` with normalized `major` and `type`:
   - `type="course_description"` for class list CSVs.
   - `type="handbook_requirement"` / `"other"` for non-course CSVs (based on filename heuristics).
3. Compute embeddings using `EmbeddingBackend`.
4. Store `(id, text, metadata, embedding)` in a persistent Chroma collection under `backend/.chroma/`.

You only need to re-run ingestion when the CSVs change.

## Runtime behavior (with and without an LLM key)

### Without `OPENAI_API_KEY`

- The FastAPI app still initialises the RAG components at startup:
  - `EmbeddingBackend` (local model only).
  - `VectorStore` reading from `backend/.chroma/`.
  - `Retriever` combining both.
- `/api/chat`:
  - Uses `Retriever` to pull relevant chunks based on the student's question and Pratt profile.
  - Returns a deterministic placeholder `reply` string, plus `retrieved_chunks` and metadata (`using_model=False`).
  - This fully exercises ingestion, embeddings, and retrieval even without external services.

### With `OPENAI_API_KEY`

- `LLMClient` is configured with your OpenAI chat and embedding models.
- `/api/chat` pipeline:
  1. `classify_intent` (`rag_pipeline.py`) calls the chat model to pick an intent label (e.g. `major_requirements`, `prerequisites_sequencing`).
  2. `retrieve_context` calls `Retriever.retrieve`, which:
     - Builds a `where` filter on `major` (e.g. `ECE` or `ALL`).
     - Uses `intent` to bias towards `course_description` vs `handbook_requirement` documents.
     - Prepends a short profile snippet (major, year, semester, current/completed courses) to the query string before embedding.
  3. `generate_answer` constructs a RAG-style prompt with:
     - System prompt about Pratt advising.
     - Student profile summary.
     - Numbered context chunks from retrieval.
     - The student's question and intent.
  4. The model's answer is returned as `reply`, along with the raw `retrieved_chunks` and metadata (`intent`, `intent_confidence`, `using_model=True`).

## Design choices (for an oral exam)

- **Explicit document schema**: `backend/rag/schema.py` defines a `Document` dataclass with `major`, `type`, `code`, `title`, and arbitrary `metadata`. This makes it easy to:
  - Filter by major (`ECE`, `BME`, `ME`, `CEE_ENV`, `CS`, `ALL`).
  - Distinguish course descriptions vs handbook/policy text.
  - Track provenance (`source_file`, `row_index`).
- **Metadata-aware retrieval**: Instead of a pure text search, the retriever uses:
  - Major-based filters (`major in {student_major, "ALL"}`) so ECE students mainly see ECE documents.
  - Intent-based filters on `type` to bias towards courses vs policies.
- **Profile-conditioned queries**: The retriever prepends a compact summary of the student's profile (major, year, semester, current/completed courses) to the query text before embedding, so the similarity search is aware of their context.
- **Two-mode embeddings**: A single `EmbeddingBackend` abstracts over local vs OpenAI embeddings, so the system is robust:
  - Works offline for demos and grading.
  - Can be upgraded to higher-quality embeddings just by setting environment variables.
- **Graceful degradation**: Even without an LLM key, the system:
  - Builds and queries a real vector index.
   - Returns retrieved chunks so you can inspect what the RAG layer is doing.
   - Uses a placeholder answer string to keep UX consistent.

## How to run the full stack

1. **Start the backend** (after ingestion and `pip install -r requirements.txt`):

```bash
cd backend
source .venv/bin/activate
uvicorn backend.main:app --reload
```

2. **Start the frontend** (in another terminal):

```bash
cd ..  # project root
npm install
npm run dev
```

3. Open `http://localhost:5173` in your browser and ask Pratt-specific questions. The assistant will:
   - Use your Pratt profile from the sidebar.
   - Retrieve relevant course/handbook snippets from the vector store.
   - (Optionally) call an LLM to generate an answer grounded in those snippets.
