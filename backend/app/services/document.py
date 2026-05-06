import uuid
from functools import lru_cache

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.chunking import get_chunking_service
from app.services.embedding import get_embedding_service


class DocumentService:
    async def create_document(
        self, session: AsyncSession, collection_id: uuid.UUID, data: DocumentCreate
    ) -> Document:
        document = Document(
            collection_id=collection_id,
            title=data.title,
            content=data.content,
            metadata_=data.metadata,
        )
        session.add(document)
        await session.flush()

        await self._rechunk_document(session, document)
        await session.commit()
        await session.refresh(document)
        return document

    async def get_document(
        self, session: AsyncSession, document_id: uuid.UUID
    ) -> Document | None:
        result = await session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        session: AsyncSession,
        collection_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Document], int]:
        count_query = select(func.count(Document.id)).where(
            Document.collection_id == collection_id
        )
        total = (await session.execute(count_query)).scalar() or 0

        query = (
            select(Document)
            .where(Document.collection_id == collection_id)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(query)
        documents = list(result.scalars().all())

        return documents, total

    async def update_document(
        self,
        session: AsyncSession,
        document_id: uuid.UUID,
        data: DocumentUpdate,
    ) -> Document | None:
        document = await self.get_document(session, document_id)
        if document is None:
            return None

        if data.title is not None:
            document.title = data.title
        if data.content is not None:
            document.content = data.content
        if data.metadata is not None:
            document.metadata_ = data.metadata

        # Re-chunk if content changed
        if data.content is not None:
            await self._rechunk_document(session, document)

        await session.commit()
        await session.refresh(document)
        return document

    async def delete_document(
        self, session: AsyncSession, document_id: uuid.UUID
    ) -> bool:
        result = await session.execute(
            delete(Document).where(Document.id == document_id)
        )
        await session.commit()
        return result.rowcount > 0

    async def _rechunk_document(
        self, session: AsyncSession, document: Document
    ) -> None:
        # Delete existing chunks
        await session.execute(
            delete(Chunk).where(Chunk.document_id == document.id)
        )

        chunking = get_chunking_service()
        embedding = get_embedding_service()

        chunks = chunking.chunk(document.content)
        if not chunks:
            return

        texts = [c.text for c in chunks]
        embeddings = await embedding.embed(texts)

        for chunk, emb in zip(chunks, embeddings):
            db_chunk = Chunk(
                document_id=document.id,
                chunk_index=chunk.index,
                content=chunk.text,
                embedding=emb,
                token_count=chunk.token_count,
                metadata_=document.metadata_,
            )
            session.add(db_chunk)


@lru_cache
def get_document_service() -> DocumentService:
    return DocumentService()
