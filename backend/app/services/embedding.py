from functools import lru_cache

from sqlalchemy import text

from app.config import get_settings


class EmbeddingService:
    """Generates embeddings using either a local model or DeepSeek API."""

    def __init__(self):
        settings = get_settings()
        self.provider = settings.embedding_provider
        self.model_name = settings.embedding_model
        self.dimensions = settings.embedding_dimensions
        self._local_model = None

    def _get_local_model(self):
        if self._local_model is None:
            from sentence_transformers import SentenceTransformer

            self._local_model = SentenceTransformer(self.model_name)
        return self._local_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "deepseek":
            return await self._embed_deepseek(texts)
        return self._embed_local(texts)

    def _embed_local(self, texts: list[str]) -> list[list[float]]:
        model = self._get_local_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def _embed_deepseek(self, texts: list[str]) -> list[list[float]]:
        import asyncio

        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        model = settings.deepseek_embedding_model or "deepseek-embedding"

        response = await client.embeddings.create(model=model, input=texts)
        return [d.embedding for d in response.data]

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await self.embed([text])
        return embeddings[0]

    def get_dimensions(self) -> int:
        return self.dimensions

    def to_pgvector(self, embedding: list[float]) -> str:
        return f"[{','.join(str(v) for v in embedding)}]"


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
