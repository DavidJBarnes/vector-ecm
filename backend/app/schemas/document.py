import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=1024)
    content: str = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=1024)
    content: str | None = Field(None, min_length=1)
    metadata: dict | None = None


class ChunkResponse(BaseModel):
    id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int | None
    metadata: dict

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: uuid.UUID
    collection_id: uuid.UUID
    title: str
    content: str
    metadata: dict
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class DocumentWithChunks(DocumentResponse):
    chunks: list[ChunkResponse] = Field(default_factory=list)
