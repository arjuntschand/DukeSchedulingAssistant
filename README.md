# Duke Degree & Course Planning Chatbot

Retrieval-Augmented Generation (RAG) chatbot for Duke Pratt students. The
system retrieves relevant passages from official degree handbooks and course
lists, combines them with a few-shot examples document, and then uses a GPT
model (via OpenRouter) to generate grounded answers about requirements,
prerequisites, study abroad, and overload policies.

## High-level architecture

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
	- Chat-style UI with sidebar and main conversation area.
	- Sends `POST /api/chat` with `{ message, history, prattProfile }`.
	- Shows **retrieved RAG context** and **few-shot examples** behind
		collapsible toggles, with links back to the underlying PDFs / CSVs
		served by the backend.
- **Backend (RAG)**: FastAPI (`backend/`)
	- `POST /api/chat` endpoint.
	- **RAG over `ContextDocuments/`**:
		- Course CSVs (e.g. `BME_classes.csv`, `CEE_classes.csv`, `ME_classes.csv`).
		- Handbook PDFs (e.g. `BMEHandbook2024-2025.pdf`, `CEEHandbook2024-2025.pdf`).
		- Few-shot examples (`FewShotLearningExamples.pdf`), split into full
			“Base Information … Answer” worked examples.
	- Builds a Chroma vector index via `backend.rag.ingest` and queries it
		with a metadata-aware `Retriever` (`backend/rag/retriever.py`).
	- Calls an OpenRouter-hosted GPT model for:
		- Intent classification (5 intent labels).
		- Answer generation conditioned on the retrieved documents and
			selected few-shot examples.

For more backend details, see `backend/README_backend.md` and
`backend/README_RAG.md`.

## Getting started

### 1. Frontend

From the project root:

```bash
npm install
npm run dev
```

The dev server will start on `http://localhost:5173`.

### 2. Backend

From the `backend/` directory:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure env vars
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY and OPENROUTER_MODEL

# Build the vector index from ContextDocuments/
python -m backend.rag.ingest

# Run the API
uvicorn backend.main:app --reload --port 8000
```

By default, the Vite dev server proxies `/api` to `http://localhost:8000`,
so the frontend can just call `fetch('/api/chat', ...)`.

## What the system does

- **Intent classification**: Classifies each question into one of
	`major_requirements`, `prerequisites_sequencing`, `study_abroad_transfer`,
	`overload_registration`, or `other`.
- **Profile-aware retrieval**: Uses the Pratt profile (major, year, semester,
	current and completed courses) plus the intent label to retrieve the most
	relevant handbook and course snippets from the vector store.
- **Few-shot guidance**: Retrieves the top 2 most relevant worked examples
	from `FewShotLearningExamples.pdf` and includes them in the prompt to
	steer answer style and structure.
- **Grounded answers**: The model answer is conditioned on the retrieved
	context and includes enough detail for students to understand prerequisites,
	sequencing, overload rules, or study abroad planning.
- **Source transparency**: The assistant response includes:
	- `retrieved_chunks` (plain text).
	- `sources` (file name, page, chunk index, type), which the frontend uses
		to show “View source” links back to the underlying PDFs / CSVs.

## Useful entry points

- Frontend app: `src/App.tsx`
- Message UI: `src/components/MessageBubble.tsx`
- Backend FastAPI app: `backend/main.py`
- RAG pipeline orchestration: `backend/rag_pipeline.py`
- RAG ingestion: `backend/rag/ingest.py`
- RAG retriever: `backend/rag/retriever.py`

These are good files to skim if you are grading, extending, or debugging the
project.
