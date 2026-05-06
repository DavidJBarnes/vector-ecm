import logging
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from app.database import engine
from app.routers import (
    chat_router,
    collections_router,
    documents_router,
    search_router,
)

logger = logging.getLogger("vectorcms")


def run_migrations() -> None:
    alembic_cfg = Config(Path(__file__).parent.parent / "alembic.ini")
    alembic_cfg.set_main_option(
        "script_location", str(Path(__file__).parent.parent / "migrations")
    )
    try:
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully")
    except Exception as e:
        logger.error("Migration failed: %s", e)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield
    await engine.dispose()


app = FastAPI(
    title="VectorCMS",
    description="Probabilistic document retrieval with semantic search",
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
