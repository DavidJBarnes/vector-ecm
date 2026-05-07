from functools import lru_cache

from openai import AsyncOpenAI

from app.config import get_settings
from app.services.search import get_search_service


DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant answering questions about documents in a CMS.
Use the provided document chunks to answer the user's question.
If the chunks don't contain enough information, say so honestly.
Always cite which documents you're drawing from when possible.
Be concise and accurate."""


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.model = settings.chat_model
        self.max_tokens = settings.chat_max_tokens
        self.temperature = settings.chat_temperature
        self.provider = settings.llm_provider

    def _build_client(self, api_key: str | None = None, base_url: str | None = None) -> AsyncOpenAI:
        settings = get_settings()
        return AsyncOpenAI(
            api_key=api_key or settings.deepseek_api_key,
            base_url=base_url or settings.deepseek_base_url,
        )

    async def chat(
        self,
        session,
        collection_id: str,
        message: str,
        top_k: int = 5,
        temperature: float | None = None,
        max_tokens: int | None = None,
        runtime: dict | None = None,
    ) -> dict:
        rt = runtime or {}

        settings = get_settings()
        model = rt.get("chat_model") or self.model
        system_text = rt.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
        api_key = rt.get("api_key") or settings.deepseek_api_key
        base_url = rt.get("base_url") or settings.deepseek_base_url
        effective_top_k = top_k or int(rt.get("top_k", settings.search_default_top_k))
        effective_temp = temperature if temperature is not None else float(rt.get("temperature", self.temperature))
        effective_max = max_tokens or int(rt.get("max_tokens", self.max_tokens))

        search_service = get_search_service()
        results = await search_service.semantic_search(
            session=session,
            collection_id=collection_id,
            query=message,
            top_k=effective_top_k,
        )

        context_parts = []
        for r in results:
            context_parts.append(
                f"[Document: {r.document_title} (chunk {r.chunk_index})]\n{r.content}"
            )
        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

        messages = [
            {"role": "system", "content": system_text},
            {
                "role": "user",
                "content": f"Context from documents:\n\n{context}\n\nQuestion: {message}",
            },
        ]

        client = self._build_client(api_key=api_key, base_url=base_url)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=effective_temp,
            max_tokens=effective_max,
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

        return {"answer": answer, "sources": sources, "model": model}

    async def chat_stream(
        self,
        session,
        collection_id: str,
        message: str,
        top_k: int = 5,
        temperature: float | None = None,
        max_tokens: int | None = None,
        runtime: dict | None = None,
    ):
        rt = runtime or {}

        settings = get_settings()
        model = rt.get("chat_model") or self.model
        system_text = rt.get("system_prompt") or DEFAULT_SYSTEM_PROMPT
        api_key = rt.get("api_key") or settings.deepseek_api_key
        base_url = rt.get("base_url") or settings.deepseek_base_url
        effective_top_k = top_k or int(rt.get("top_k", settings.search_default_top_k))
        effective_temp = temperature if temperature is not None else float(rt.get("temperature", self.temperature))
        effective_max = max_tokens or int(rt.get("max_tokens", self.max_tokens))

        search_service = get_search_service()
        results = await search_service.semantic_search(
            session=session,
            collection_id=collection_id,
            query=message,
            top_k=effective_top_k,
        )

        context_parts = []
        for r in results:
            context_parts.append(
                f"[Document: {r.document_title} (chunk {r.chunk_index})]\n{r.content}"
            )
        context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

        messages = [
            {"role": "system", "content": system_text},
            {
                "role": "user",
                "content": f"Context from documents:\n\n{context}\n\nQuestion: {message}",
            },
        ]

        client = self._build_client(api_key=api_key, base_url=base_url)
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=effective_temp,
            max_tokens=effective_max,
            stream=True,
        )

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

        yield f"data: {json.dumps({'type': 'sources', 'sources': sources, 'model': model})}\n\n"

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"

        yield "data: [DONE]\n\n"


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()
