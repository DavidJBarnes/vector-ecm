from functools import lru_cache

from openai import AsyncOpenAI

from app.config import get_settings
from app.services.search import get_search_service


SYSTEM_PROMPT = """You are a helpful assistant answering questions about documents in a CMS.
Use the provided document chunks to answer the user's question.
If the chunks don't contain enough information, say so honestly.
Always cite which documents you're drawing from when possible.
Be concise and accurate."""


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.provider = settings.llm_provider
        self.model = settings.chat_model
        self.max_tokens = settings.chat_max_tokens
        self.temperature = settings.chat_temperature
        self._client = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            settings = get_settings()
            self._client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
        return self._client

    async def chat(
        self,
        session,
        collection_id: str,
        message: str,
        top_k: int = 5,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict:
        # Search for relevant chunks
        search_service = get_search_service()
        results = await search_service.semantic_search(
            session=session,
            collection_id=collection_id,
            query=message,
            top_k=top_k,
        )

        # Build context from retrieved chunks
        context_parts = []
        for r in results:
            context_parts.append(
                f"[Document: {r.document_title} (chunk {r.chunk_index})]\n{r.content}"
            )
        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

        # Build messages for the LLM
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context from documents:\n\n{context}\n\nQuestion: {message}",
            },
        ]

        client = self._get_client()
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )

        answer = response.choices[0].message.content or ""

        sources = [
            {
                "chunk_id": str(r.chunk_id),
                "document_id": str(r.document_id),
                "document_title": r.document_title,
                "chunk_index": r.chunk_index,
                "score": r.score,
            }
            for r in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "model": self.model,
        }

    async def chat_stream(
        self,
        session,
        collection_id: str,
        message: str,
        top_k: int = 5,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        search_service = get_search_service()
        results = await search_service.semantic_search(
            session=session,
            collection_id=collection_id,
            query=message,
            top_k=top_k,
        )

        context_parts = []
        for r in results:
            context_parts.append(
                f"[Document: {r.document_title} (chunk {r.chunk_index})]\n{r.content}"
            )
        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context from documents:\n\n{context}\n\nQuestion: {message}",
            },
        ]

        client = self._get_client()
        stream = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
        )

        # Yield sources first as a JSON event, then content chunks
        import json

        sources = [
            {
                "chunk_id": str(r.chunk_id),
                "document_id": str(r.document_id),
                "document_title": r.document_title,
                "chunk_index": r.chunk_index,
                "score": r.score,
            }
            for r in results
        ]

        yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'model': self.model})}\n\n"

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

        yield "data: [DONE]\n\n"


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()
