# Duke Pratt Degree & Course Planning Chatbot Backend

FastAPI-based backend for the Duke Pratt advising chatbot. This service exposes
`POST /api/chat`, performs a simple RAG-like pipeline over a toy corpus, and
uses an OpenAI-compatible GPT model to generate answers.

The frontend (React + Vite) sends requests shaped like:

```json
{
  "message": "string",
  "history": [
    { "id": "string", "role": "user|assistant", "content": "string", "timestamp": "string" }
  ],
  "prattProfile": {
    "major": "string",
    "classYear": "string",
    "semester": "string",
    "currentCourses": ["ECE 110L", "MATH 218D"],
    "completedCourses": ["CHEM 101DL"]
  }
}
```

The backend responds with:

```json
{
  "reply": "GPT-generated answer text",
  "retrieved_chunks": ["handbook-like snippet 1", "snippet 2", "snippet 3"],
  "metadata": {
    "intent": "major_requirements",
    "intent_confidence": 0.7
  }
}
```

## 1. Setup

From the `backend/` directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI (or compatible) API key and model names:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## 2. Run the server

From inside `backend/` (with the virtualenv activated):

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:

- `http://localhost:8000/health` – health check
- `http://localhost:8000/api/chat` – main chat endpoint

## 3. Frontend integration

The existing frontend currently calls `fetch('/api/chat', ...)` from the Vite
origin (usually `http://localhost:5173`). There are two options to connect it
with this backend:

1. **Change the frontend fetch URL** to the full backend URL, e.g.:
   `fetch('http://localhost:8000/api/chat', ...)`.

2. **Or configure a Vite dev proxy** so that `/api/chat` is forwarded to the
   backend while in development.

Given your current setup, the minimal change is to update the frontend fetch
URL to `http://localhost:8000/api/chat`. No backend changes are required for
this; CORS is already configured to allow `http://localhost:5173`.

## 4. Request → Response pipeline

1. **`POST /api/chat`** receives a `ChatRequest` containing:
   - `message`: latest user question.
   - `history`: prior messages (for context; not yet deeply used).
   - `prattProfile`: structured info about major, class year, courses, etc.

2. **Intent classification** (`rag_pipeline.classify_intent`):
   - Calls the LLM with a small prompt to classify the question into one of:
     - `major_requirements`
     - `prerequisites_sequencing`
     - `study_abroad_transfer`
     - `overload_registration`
     - `other`

3. **Context retrieval** (`rag_pipeline.retrieve_context`):
   - Delegates to `retrieval.simple_retriever.retrieve`.
   - Uses a tiny in-memory corpus of handbook-like strings about Pratt majors,
     overload rules, and study abroad.
   - Uses a naive keyword overlap score to pick the top `k` chunks.

4. **Answer generation** (`rag_pipeline.generate_answer`):
   - Builds a RAG-style prompt including:
     - A system message describing the Duke Pratt advising assistant.
     - A system message summarizing the `PrattProfile` fields.
     - An assistant message listing the retrieved handbook-like excerpts.
     - A final user message with the intent label and the student's question.
   - Calls `LLMClient.chat(...)` to get an answer from the GPT model.
   - Returns `ChatResponse` with:
     - `reply`: model answer.
     - `retrieved_chunks`: the snippets sent as context.
     - `metadata`: at least `intent` and `intent_confidence`.

## 5. RAG and Pratt handbooks (future work)

Current retrieval is purely illustrative and uses a hardcoded list in
`backend/retrieval/simple_retriever.py`. To move to a real RAG over the five
Pratt degree handbooks, you would:

1. Place the handbook source files (PDF or text) under `backend/data/`.
2. Create an ingestion script (e.g. `ingest_handbooks.py`) that:
   - Loads and chunks each handbook into passages.
   - Calls `LLMClient.embed(...)` to create embeddings.
   - Stores embeddings and metadata in a local index or vector DB.
3. Replace `simple_retriever.retrieve` with a new retriever that:
   - Loads the index.
   - Computes an embedding for the incoming question.
   - Performs nearest-neighbor search to return the most relevant chunks.

All higher-level interfaces (`retrieve_context`, `generate_answer`, and the
`POST /api/chat` contract) can remain the same while you upgrade the retrieval
layer.
