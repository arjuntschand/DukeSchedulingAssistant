from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ChatRole = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    id: str
    role: ChatRole
    content: str
    timestamp: str


class SourceChunk(BaseModel):
    text: str
    source_file: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None
    type: Optional[str] = None


class PrattProfile(BaseModel):
    major: Optional[str] = None
    classYear: Optional[str] = None
    semester: Optional[str] = None
    currentCourses: List[str] = Field(default_factory=list)
    completedCourses: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    prattProfile: Optional[PrattProfile] = None


class ChatResponse(BaseModel):
    reply: str
    retrieved_chunks: List[str] = Field(default_factory=list)
    sources: List[SourceChunk] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentResult(BaseModel):
    intent: str
    confidence: float
