from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

from pypdf import PdfReader

from .schema import Document, normalize_major
from .embeddings import EmbeddingBackend
from .vector_store import VectorStore


CONTEXT_DIR = Path(__file__).resolve().parent.parent.parent / "ContextDocuments"
PERSIST_DIR = Path(__file__).resolve().parent.parent / ".chroma"


def _guess_type_from_filename(filename: str) -> str:
    lower = filename.lower()
    if "class" in lower or "course" in lower:
        return "course_description"
    if "handbook" in lower or "requirement" in lower:
        return "handbook_requirement"
    return "other"


def _row_to_document(file_path: Path, row_index: int, row: dict) -> Document:
    filename = file_path.name
    doc_id = f"{filename}:{row_index}"

    subject = row.get("Subject code") or row.get("Subject") or row.get("Major")
    major = normalize_major(str(subject) if subject is not None else None) or "ALL"

    catalog = row.get("Catalog Number") or row.get("Number") or ""
    code = None
    if subject and catalog:
        code = f"{subject} {catalog}".strip()

    title = row.get("Course Title") or row.get("Title") or None

    description_parts: List[str] = []
    for key in [
        "Course Description",
        "Description",
        "Requirements",
        "Text",
    ]:
        value = row.get(key)
        if value:
            description_parts.append(str(value))

    text = "\n\n".join(description_parts).strip()
    if not text:
        # As a fallback, at least index the title
        text = title or ""

    doc_type = _guess_type_from_filename(filename)

    metadata = {
        "source_file": filename,
        "row_index": row_index,
    }

    return Document(
        id=doc_id,
        major=major,
        type=doc_type,
        code=code,
        title=title,
        text=text,
        metadata=metadata,
    )


def _guess_major_from_pdf_name(filename: str) -> str:
    lower = filename.lower()
    if "bme" in lower:
        return "BME"
    if "ece" in lower:
        return "ECE"
    if "me_" in lower or "_me" in lower or "mechanical" in lower:
        return "ME"
    if "cee" in lower or "civil" in lower or "environmental" in lower:
        return "CEE_ENV"
    return "ALL"


def _chunk_text(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    for i in range(0, len(words), max_words):
        chunk_words = words[i : i + max_words]
        if chunk_words:
            chunks.append(" ".join(chunk_words))
    return chunks


def _pdf_to_documents(pdf_path: Path) -> List[Document]:
    """Convert a PDF into Documents.

    - Normal handbooks are split into ~400-word chunks.
    - Few-shot PDFs (filename contains "fewshot" or "few_shot") are split
      into whole example paths instead of arbitrary chunks. Each example
      becomes a single Document so we can retrieve the top-k examples.
    """

    reader = PdfReader(str(pdf_path))
    full_text_parts: List[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        if page_text.strip():
            full_text_parts.append(page_text)

    full_text = "\n\n".join(full_text_parts).strip()
    if not full_text:
        return []

    filename = pdf_path.name
    lower_name = filename.lower()

    # Few-shot examples PDF is not tied to a single major; mark as ALL and
    # give it a special type so we can retrieve it separately.
    if "fewshot" in lower_name or "few_shot" in lower_name:
        major_code = "ALL"
        doc_type = "fewshot_example"

        # Heuristic: split into whole example paths. In the provided
        # FewShotLearningExamples.pdf each example starts with a
        # "Base Information" section, so we use that as the
        # boundary marker rather than generic "Example N" markers.
        import re

        # Insert explicit newlines around "Base Information" so splitting is easier.
        normalized = re.sub(r"(Base Information)", r"\n\1", full_text)
        # Split on lines that start with "Base Information".
        parts = re.split(r"(?=^Base Information)", normalized, flags=re.MULTILINE)
        examples: List[str] = []
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                examples.append(cleaned)

        docs: List[Document] = []
        for idx, example_text in enumerate(examples):
            doc_id = f"{filename}:example-{idx}"
            title = f"{filename} example {idx + 1}"
            metadata = {
                "source_file": filename,
                "example_index": idx,
            }
            docs.append(
                Document(
                    id=doc_id,
                    major=major_code,
                    type=doc_type,
                    code=None,
                    title=title,
                    text=example_text,
                    metadata=metadata,
                )
            )

        return docs

    # Default handbook behavior: chunk into ~400-word pieces.
    major_code = _guess_major_from_pdf_name(filename)
    doc_type = "handbook_requirement"

    chunks = _chunk_text(full_text, max_words=400)
    docs: List[Document] = []
    for idx, chunk in enumerate(chunks):
        doc_id = f"{filename}:chunk-{idx}"
        title = f"{filename} section {idx + 1}"
        metadata = {
            "source_file": filename,
            "chunk_index": idx,
        }
        docs.append(
            Document(
                id=doc_id,
                major=major_code,
                type=doc_type,
                code=None,
                title=title,
                text=chunk,
                metadata=metadata,
            )
        )

    return docs


def load_context_documents(context_dir: Path = CONTEXT_DIR) -> Tuple[List[Document], List[Document]]:
    course_docs: List[Document] = []
    handbook_docs: List[Document] = []

    # Course / CSV documents
    for csv_path in context_dir.glob("*.csv"):
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                doc = _row_to_document(csv_path, idx, row)
                if doc.text:
                    course_docs.append(doc)

    # Handbook PDF documents
    for pdf_path in context_dir.glob("*.pdf"):
        handbook_docs.extend(_pdf_to_documents(pdf_path))

    return course_docs, handbook_docs


async def ingest() -> None:
    context_dir = CONTEXT_DIR
    persist_dir = PERSIST_DIR
    persist_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading context documents from {context_dir}...")
    course_docs, handbook_docs = load_context_documents(context_dir)
    docs = course_docs + handbook_docs
    print(f"Loaded {len(course_docs)} course documents from CSVs.")
    print(f"Loaded {len(handbook_docs)} handbook documents from PDFs.")

    embedding_backend = EmbeddingBackend()
    print("Computing embeddings (this may take a moment)...")
    embeddings = await embedding_backend.embed_documents([d.text for d in docs])

    store = VectorStore(persist_dir=persist_dir)
    print("Writing to vector store...")
    await store.add_documents(docs, embeddings)
    print(f"Ingestion complete. Persistent index stored in {persist_dir}.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(ingest())
