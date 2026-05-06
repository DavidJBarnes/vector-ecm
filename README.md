# VectorCMS

Probabilistic document retrieval with semantic search.

[github.com/DavidJBarnes/vectorcms](https://github.com/DavidJBarnes/vectorcms)

## Architecture

```
vectorcms/
├── backend/          # FastAPI + PostgreSQL/pgvector
│   ├── app/
│   │   ├── models/   # SQLAlchemy ORM (collections, documents, chunks)
│   │   ├── schemas/  # Pydantic request/response models
│   │   ├── services/ # Embedding, chunking, search, LLM chat
│   │   └── routers/  # REST endpoints
│   └── migrations/   # Alembic migrations
└── frontend/         # React/Vite (coming soon)
```

## Quick Start

```bash
# 1. Start PostgreSQL with pgvector
docker compose up -d

# 2. Install Python dependencies
cd backend
pip install -e ".[dev]"

# 3. Set up environment
cp .env.example .env
# Edit .env with your DeepSeek API key if using remote embeddings/chat

# 4. Start the API (migrations run automatically on startup)
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs

## API Endpoints

### Collections
- `POST   /collections`              — Create collection
- `GET    /collections`              — List collections
- `GET    /collections/{id}`         — Get collection
- `PATCH  /collections/{id}`         — Update collection
- `DELETE /collections/{id}`         — Delete collection

### Documents
- `POST   /collections/{id}/documents`          — Create (auto-chunks + embeds)
- `GET    /collections/{id}/documents`          — List documents
- `GET    /collections/{id}/documents/{doc_id}` — Get with chunks
- `PATCH  /collections/{id}/documents/{doc_id}` — Update (re-embeds)
- `DELETE /collections/{id}/documents/{doc_id}` — Delete

### Search
- `POST /collections/{id}/search`        — Semantic search
- `POST /collections/{id}/search/hybrid` — Hybrid (vector + keyword)

### Chat (RAG)
- `POST /collections/{id}/chat`         — RAG chat with DeepSeek
- `POST /collections/{id}/chat/stream`  — Streaming RAG chat

## Configuration

Key env vars (see `.env.example` for full list):

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_PROVIDER` | `local` | `local` (sentence-transformers) or `deepseek` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Model name for local or API embeddings |
| `DEEPSEEK_API_KEY` | — | Required for DeepSeek chat + API embeddings |
| `LLM_PROVIDER` | `deepseek` | LLM for RAG chat |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |

## Design Decisions

- **pgvector** over dedicated vector DB: simpler deployment, one DB for everything, supports hybrid search natively via PostgreSQL FTS + vector
- **HNSW index** for vector search: better recall/performance than IVFFlat
- **Embedding on write**: documents are chunked and embedded synchronously on create/update. For high-throughput, swap to a background task queue later
- **DeepSeek API**: OpenAI-compatible, used for both optional embeddings and RAG chat. Local sentence-transformers are default for embeddings to keep costs low
- **Hybrid search**: weighted combination of vector cosine similarity and PostgreSQL `ts_rank` — tunable via `vector_weight`/`keyword_weight` params
