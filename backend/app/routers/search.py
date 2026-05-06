import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.search import (
    HybridSearchRequest,
    SearchRequest,
    SearchResponse,
)
from app.services.search import get_search_service

router = APIRouter(prefix="/collections/{collection_id}/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def semantic_search(
    collection_id: uuid.UUID,
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_search_service()
    results = await service.semantic_search(
        session=db,
        collection_id=str(collection_id),
        query=req.query,
        top_k=req.top_k,
        score_threshold=req.score_threshold,
    )
    return SearchResponse(query=req.query, results=results, total=len(results))


@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    collection_id: uuid.UUID,
    req: HybridSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    service = get_search_service()
    results = await service.hybrid_search(
        session=db,
        collection_id=str(collection_id),
        query=req.query,
        top_k=req.top_k,
        vector_weight=req.vector_weight,
        keyword_weight=req.keyword_weight,
    )
    return SearchResponse(query=req.query, results=results, total=len(results))
