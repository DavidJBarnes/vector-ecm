import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.database import engine
from app.routers import (
    chat_router,
    collections_router,
    documents_router,
    search_router,
)

logger = logging.getLogger("vector-ecm")


def run_migrations() -> None:
    import subprocess
    import sys

    backend_dir = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        logger.error("Migration failed:\n%s\n%s", result.stdout, result.stderr)
        raise RuntimeError(f"Migration failed: {result.stderr}")
    logger.info("Migrations applied successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(run_migrations)
    yield
    await engine.dispose()


app = FastAPI(
    title="Vector ECM",
    description="Enterprise content management with semantic search",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(collections_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
