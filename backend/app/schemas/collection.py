import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class CollectionUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    metadata: dict | None = None


class CollectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    model_config = {"from_attributes": True}
