"""Initial schema: collections, documents, chunks with pgvector"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "collections",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("collection_id", sa.UUID(), sa.ForeignKey("collections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(1024), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata_", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("idx_documents_collection_id", "documents", ["collection_id"])
    op.execute(
        "CREATE INDEX idx_documents_fts ON documents USING GIN (to_tsvector('english', content))"
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", sa.UUID(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(384), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata_", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("idx_chunks_document_id", "chunks", ["document_id"])
    op.execute(
        "CREATE INDEX idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("idx_chunks_embedding")
    op.drop_index("idx_chunks_document_id")
    op.drop_table("chunks")
    op.drop_index("idx_documents_fts")
    op.drop_index("idx_documents_collection_id")
    op.drop_table("documents")
    op.drop_table("collections")
