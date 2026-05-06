from functools import lru_cache

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.search import ChunkResult
from app.services.embedding import get_embedding_service


class SearchService:
    async def semantic_search(
        self,
        session: AsyncSession,
        collection_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float | None = None,
    ) -> list[ChunkResult]:
        embedding_service = get_embedding_service()
        query_embedding = await embedding_service.embed_query(query)

        # Cosine similarity: 1 - cosine_distance = similarity
        similarity = 1.0 - Chunk.embedding.cosine_distance(query_embedding)

        stmt = (
            select(
                Chunk.id.label("chunk_id"),
                Chunk.document_id,
                Document.title.label("document_title"),
                Chunk.chunk_index,
                Chunk.content,
                Chunk.metadata_,
                similarity.label("score"),
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(
                Document.collection_id == collection_id,
                Chunk.embedding.isnot(None),
            )
        )

        if score_threshold is not None:
            stmt = stmt.where(similarity >= score_threshold)

        stmt = stmt.order_by(similarity.desc()).limit(top_k)

        result = await session.execute(stmt)
        rows = result.all()

        return [
            ChunkResult(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                document_title=row.document_title,
                chunk_index=row.chunk_index,
                content=row.content,
                score=round(row.score, 4),
                metadata=row.metadata_ or {},
            )
            for row in rows
        ]

    async def hybrid_search(
        self,
        session: AsyncSession,
        collection_id: str,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> list[ChunkResult]:
        settings = get_settings()
        embedding_service = get_embedding_service()
        query_embedding = await embedding_service.embed_query(query)

        vector_similarity = 1.0 - Chunk.embedding.cosine_distance(query_embedding)
        keyword_rank = func.ts_rank(
            func.to_tsvector("english", Chunk.content),
            func.plainto_tsquery("english", query),
        )

        combined_score = (
            vector_weight * vector_similarity + keyword_weight * func.coalesce(keyword_rank, 0.0)
        )

        stmt = (
            select(
                Chunk.id.label("chunk_id"),
                Chunk.document_id,
                Document.title.label("document_title"),
                Chunk.chunk_index,
                Chunk.content,
                Chunk.metadata_,
                combined_score.label("score"),
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(
                Document.collection_id == collection_id,
                Chunk.embedding.isnot(None),
            )
            .order_by(combined_score.desc())
            .limit(top_k)
        )

        result = await session.execute(stmt)
        rows = result.all()

        return [
            ChunkResult(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                document_title=row.document_title,
                chunk_index=row.chunk_index,
                content=row.content,
                score=round(row.score, 4),
                metadata=row.metadata_ or {},
            )
            for row in rows
        ]


@lru_cache
def get_search_service() -> SearchService:
    return SearchService()
