"""Document and RAG cache SQLAlchemy models."""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[Optional[str]] = mapped_column(String(50))

    source: Mapped[Optional[str]] = mapped_column(String(255))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    author: Mapped[Optional[str]] = mapped_column(String(255))

    skill_areas: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    topics: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    published_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[Optional[int]] = mapped_column(Integer)
    chunk_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Note: Vector column added via raw SQL in migration (pgvector type not natively in SA)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


class RAGSearchCache(BaseModel):
    __tablename__ = "rag_search_cache"

    query_text: Mapped[str] = mapped_column(String(500), nullable=False)
    query_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    retrieved_chunk_ids: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    retrieval_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    cached_result: Mapped[Optional[dict]] = mapped_column(JSONB)

    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
