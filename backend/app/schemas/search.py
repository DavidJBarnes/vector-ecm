import uuid

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=100)
    score_threshold: float | None = Field(default=None, ge=0.0, le=1.0)


class HybridSearchRequest(SearchRequest):
    vector_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.3, ge=0.0, le=1.0)


class ChunkResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    chunk_index: int
    content: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    query: str
    results: list[ChunkResult]
    total: int
