import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    collection = relationship("Collection", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_documents_collection_id", "collection_id"),
        Index(
            "idx_documents_fts",
            func.to_tsvector("english", "content"),
            postgresql_using="gin",
        ),
    )
