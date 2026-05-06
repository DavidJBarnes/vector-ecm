from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.routers import (
    chat_router,
    collections_router,
    documents_router,
    search_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="VectorCMS",
    description="Probabilistic document retrieval with semantic search",
    version="0.1.0",
)

app.include_router(collections_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
