from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=8192)


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict] = Field(default_factory=list)
    model: str
