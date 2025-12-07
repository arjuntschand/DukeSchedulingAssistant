from __future__ import annotations

from typing import List, Optional, Dict, Any

from ..models import PrattProfile
from .schema import Document, normalize_major
from .embeddings import EmbeddingBackend
from .vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore, embedding_backend: EmbeddingBackend) -> None:
        self._store = store
        self._embeddings = embedding_backend

    async def retrieve(
        self,
        question: str,
        pratt_profile: Optional[PrattProfile],
        intent: Optional[str],
        k: int = 6,
        type_filter: Optional[str] = None,
    ) -> List[Document]:
        """Retrieve context documents for a question.

        - Uses the student's PrattProfile (major/year/semester/courses) to
          build a natural-language profile summary that is prepended to the
          question before embedding. This steers similarity search toward
          course and handbook text relevant to that specific student.
        - Normalizes the profile major to our canonical codes (ECE/BME/ME/
          CEE_ENV/CS) before building a `where` filter over metadata. If the
          major-constrained query returns no results, it automatically retries
          with the major filter removed so we never end up with "no chunks"
          just because of a mismatched label.
        """

        where: Dict[str, Any] = {}

        # --- Major normalization and metadata filter ---
        canonical_major: Optional[str] = None
        if pratt_profile and pratt_profile.major:
            canonical_major = normalize_major(pratt_profile.major)

        # For special global document types like few-shot examples, we do not
        # want to constrain by major. For everything else, we bias to the
        # student's major plus general docs.
        major_filter: Optional[Dict[str, Any]] = None
        if canonical_major and type_filter != "fewshot_example":
            major_filter = {"major": {"$in": [canonical_major, "ALL"]}}

        # --- Intent- or caller-based type biasing ---
        type_clause: Optional[Dict[str, Any]] = None
        if type_filter:
            type_clause = {"type": type_filter}
        else:
            if intent == "study_abroad_transfer" or intent == "overload_registration":
                type_clause = {"type": {"$in": ["policy", "handbook_requirement", "other"]}}
            elif intent == "major_requirements" or intent == "prerequisites_sequencing":
                type_clause = {"type": {"$in": ["handbook_requirement", "course_description"]}}

        # Chroma expects a single logical operator at the top level. Combine
        # major and type filters using an explicit $and when both are present.
        if major_filter and type_clause:
            where.update({"$and": [major_filter, type_clause]})
        elif major_filter:
            where.update(major_filter)
        elif type_clause:
            where.update(type_clause)

        # --- Build profile-aware query text ---
        def build_profile_summary(profile: Optional[PrattProfile]) -> str:
            if not profile:
                return ""

            parts = []
            if profile.major:
                parts.append(f"Major: {profile.major}")
            if profile.classYear:
                parts.append(f"Class year: {profile.classYear}")
            if profile.semester:
                parts.append(f"Current/target semester: {profile.semester}")
            if profile.currentCourses:
                parts.append(f"Current courses: {', '.join(profile.currentCourses)}")
            if profile.completedCourses:
                parts.append(
                    f"Completed / prereq courses: {', '.join(profile.completedCourses)}"
                )

            return " | ".join(parts)

        profile_summary = build_profile_summary(pratt_profile)
        if profile_summary:
            query_text = profile_summary + "\n\nQuestion: " + question
        else:
            query_text = question

        # --- First pass: with filters (if any) ---
        docs = await self._store.similarity_search(
            embedding_backend=self._embeddings,
            query=query_text,
            k=k,
            where=where or None,
        )

        # If an over-strict major filter yields nothing, retry without major
        # so we always return some context chunks.
        if not docs and where.get("major") is not None:
            fallback_where = {k: v for k, v in where.items() if k != "major"}
            docs = await self._store.similarity_search(
                embedding_backend=self._embeddings,
                query=query_text,
                k=k,
                where=fallback_where or None,
            )

        return docs
