from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    api_key: str = ""
    base_url: str = "https://api.deepseek.com"
    chat_model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_k: int = 5
    system_prompt: str = ""


class SettingsUpdate(BaseModel):
    api_key: str | None = Field(None, min_length=1)
    base_url: str | None = Field(None, min_length=1)
    chat_model: str | None = Field(None, min_length=1)
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=16384)
    top_k: int | None = Field(None, ge=1, le=50)
    system_prompt: str | None = None
