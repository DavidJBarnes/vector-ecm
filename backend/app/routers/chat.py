import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.collection import Collection
from app.models.setting import Setting
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import get_llm_service

router = APIRouter(prefix="/collections/{collection_id}/chat", tags=["chat"])


async def _get_runtime_settings(db: AsyncSession) -> dict:
    result = await db.execute(select(Setting))
    return {r.key: r.value for r in result.scalars().all()}


@router.post("", response_model=ChatResponse)
async def chat(
    collection_id: uuid.UUID,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    collection = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    if collection.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    runtime = await _get_runtime_settings(db)
    llm = get_llm_service()
    result = await llm.chat(
        session=db,
        collection_id=str(collection_id),
        message=req.message,
        top_k=req.top_k,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        runtime=runtime,
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        model=result["model"],
    )


@router.post("/stream")
async def chat_stream(
    collection_id: uuid.UUID,
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    collection = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    if collection.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    runtime = await _get_runtime_settings(db)
    llm = get_llm_service()
    return StreamingResponse(
        llm.chat_stream(
            session=db,
            collection_id=str(collection_id),
            message=req.message,
            top_k=req.top_k,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            runtime=runtime,
        ),
        media_type="text/event-stream",
    )
