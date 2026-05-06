import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.collection import Collection
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    DocumentWithChunks,
)
from app.services.document import get_document_service

router = APIRouter(prefix="/collections/{collection_id}/documents", tags=["documents"])


async def verify_collection(db: AsyncSession, collection_id: uuid.UUID):
    from sqlalchemy import select

    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    collection_id: uuid.UUID,
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    await verify_collection(db, collection_id)
    service = get_document_service()
    document = await service.create_document(db, collection_id, data)
    return _doc_to_response(document)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    collection_id: uuid.UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    await verify_collection(db, collection_id)
    service = get_document_service()
    documents, total = await service.list_documents(db, collection_id, offset, limit)
    return [_doc_to_response(d) for d in documents]


@router.get("/{document_id}", response_model=DocumentWithChunks)
async def get_document(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await verify_collection(db, collection_id)
    service = get_document_service()
    document = await service.get_document(db, document_id)
    if document is None or document.collection_id != collection_id:
        raise HTTPException(status_code=404, detail="Document not found")
    return _doc_with_chunks_to_response(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    await verify_collection(db, collection_id)
    service = get_document_service()
    document = await service.get_document(db, document_id)
    if document is None or document.collection_id != collection_id:
        raise HTTPException(status_code=404, detail="Document not found")

    updated = await service.update_document(db, document_id, data)
    return _doc_to_response(updated)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    collection_id: uuid.UUID,
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    await verify_collection(db, collection_id)
    service = get_document_service()
    document = await service.get_document(db, document_id)
    if document is None or document.collection_id != collection_id:
        raise HTTPException(status_code=404, detail="Document not found")

    await service.delete_document(db, document_id)


from sqlalchemy.orm import object_session


def _doc_to_response(doc) -> DocumentResponse:
    chunk_count = _count_chunks(doc)
    return DocumentResponse(
        id=doc.id,
        collection_id=doc.collection_id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata_,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=chunk_count,
    )


def _doc_with_chunks_to_response(doc) -> DocumentWithChunks:
    from app.schemas.document import ChunkResponse

    chunk_count = _count_chunks(doc)
    return DocumentWithChunks(
        id=doc.id,
        collection_id=doc.collection_id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata_,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        chunk_count=chunk_count,
        chunks=[
            ChunkResponse(
                id=c.id,
                chunk_index=c.chunk_index,
                content=c.content,
                token_count=c.token_count,
                metadata=c.metadata_,
            )
            for c in (doc.chunks or [])
        ],
    )


def _count_chunks(doc) -> int:
    from sqlalchemy import inspect

    insp = inspect(doc)
    if "chunks" in insp.unloaded:
        return 0
    return len(doc.chunks) if doc.chunks else 0
