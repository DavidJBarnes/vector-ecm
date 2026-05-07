import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.collection import Collection
from app.models.document import Document
from app.schemas.collection import (
    CollectionCreate,
    CollectionResponse,
    CollectionUpdate,
)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", response_model=CollectionResponse, status_code=201)
async def create_collection(data: CollectionCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Collection).where(Collection.name == data.name)
    )
    existing_col = existing.scalar_one_or_none()
    if existing_col:
        count_result = await db.execute(
            select(func.count(Document.id)).where(Document.collection_id == existing_col.id)
        )
        return _to_response(existing_col, count_result.scalar() or 0)

    collection = Collection(
        name=data.name,
        description=data.description,
        metadata_=data.metadata,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return _to_response(collection, 0)


@router.get("", response_model=list[CollectionResponse])
async def list_collections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Collection).order_by(Collection.created_at.desc())
    )
    collections = result.scalars().all()

    responses = []
    for c in collections:
        count_result = await db.execute(
            select(func.count(Document.id)).where(Document.collection_id == c.id)
        )
        count = count_result.scalar() or 0
        responses.append(_to_response(c, count))

    return responses


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    collection = await _get_collection(db, collection_id)
    count_result = await db.execute(
        select(func.count(Document.id)).where(Document.collection_id == collection_id)
    )
    count = count_result.scalar() or 0
    return _to_response(collection, count)


@router.patch("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: uuid.UUID,
    data: CollectionUpdate,
    db: AsyncSession = Depends(get_db),
):
    collection = await _get_collection(db, collection_id)

    if data.name is not None:
        collection.name = data.name
    if data.description is not None:
        collection.description = data.description
    if data.metadata is not None:
        collection.metadata_ = data.metadata

    await db.commit()
    await db.refresh(collection)

    count_result = await db.execute(
        select(func.count(Document.id)).where(Document.collection_id == collection_id)
    )
    count = count_result.scalar() or 0
    return _to_response(collection, count)


@router.delete("/{collection_id}", status_code=204)
async def delete_collection(
    collection_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    collection = await _get_collection(db, collection_id)
    await db.delete(collection)
    await db.commit()


async def _get_collection(
    db: AsyncSession, collection_id: uuid.UUID
) -> Collection:
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


def _to_response(collection: Collection, document_count: int) -> CollectionResponse:
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        metadata=collection.metadata_,
        created_at=collection.created_at,
        updated_at=collection.updated_at,
        document_count=document_count,
    )
