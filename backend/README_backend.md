# Duke Pratt Degree & Course Planning Chatbot Backend

FastAPI-based backend for the Duke Pratt advising chatbot. This service exposes
`POST /api/chat`, runs a real RAG pipeline over the handbook / course CSV /
few-shot example corpus, and calls an OpenRouter-hosted GPT model to generate
answers.

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
  "retrieved_chunks": ["handbook-like snippet 1", "snippet 2"],
  "sources": [
    {
      "text": "same text as in retrieved_chunks[0]",
      "source_file": "BMEHandbook2024-2025.pdf",
      "page": 17,
      "chunk_index": 3,
      "type": "handbook_requirement"
    }
  ],
  "metadata": {
    "intent": "major_requirements",
    "intent_confidence": 0.7,
    "fewshot_chunks": ["few-shot example text 1", "few-shot example text 2"],
    "using_model": true
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

Edit `.env` and set your OpenRouter key and model name:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=deepseek/deepseek-r1-distill-qwen-32b
```

## 2. Run the server

From inside `backend/` (with the virtualenv activated):

```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at:

- `http://localhost:8000/health` – health check
- `http://localhost:8000/api/chat` – main chat endpoint

## 3. Frontend integration

The existing frontend calls `fetch('/api/chat', ...)` from the Vite origin
(`http://localhost:5173`). In development, Vite is configured to proxy `/api`
to `http://localhost:8000`, so you do not need to hard-code the full backend
URL. CORS is configured to allow the dev origin.

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
   - Delegates to the real `Retriever` (`backend/rag/retriever.py`).
   - Queries a Chroma vector index built from:
     - Course CSVs (e.g. `BME_classes.csv`, `CEE_classes.csv`).
     - Handbook PDFs (e.g. `BMEHandbook2024-2025.pdf`).
   - Applies metadata filters based on the student's major and intent and
     returns the top `k` `Document`s.

4. **Few-shot example retrieval** (`rag_pipeline.retrieve_fewshot_examples`):
   - Retrieves whole worked examples from `FewShotLearningExamples.pdf`,
     ingested as `type="fewshot_example"`.
   - Returns only the top 2 examples (by similarity to the question).

5. **Answer generation** (`rag_pipeline.generate_answer`):
   - Builds a RAG-style prompt including:
     - A system message describing the Duke Pratt advising assistant.
     - A system message summarizing the `PrattProfile` fields.
     - A system message listing the retrieved handbook / course context.
     - A system message listing the selected few-shot examples (top 2).
     - The prior conversation history from the current chat.
     - A final user message with the intent label and the student's question.
   - Calls the OpenRouter client to get an answer from the GPT model.
   - Returns `ChatResponse` with:
     - `reply`: model answer.
     - `retrieved_chunks`: the snippets sent as context.
     - `metadata`: at least `intent` and `intent_confidence`.

## 5. RAG and Pratt handbooks

The legacy toy retriever has been replaced by a real vector-based RAG stack.
For details on ingestion, Chroma, and the metadata-aware retriever, see
`backend/README_RAG.md`.
