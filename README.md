# DocMind

Chat with your PDFs using Retrieval-Augmented Generation.

Upload documents, ask questions, get grounded answers with citations — powered by hybrid search, cross-encoder reranking, and Llama 3.3 70B via Groq.

## Architecture

```
┌──────────────────┐    HTTP/SSE    ┌──────────────────────────────────┐
│  Next.js 14      │ ─────────────▶ │         FastAPI Backend          │
│  React + Tailwind│ ◀── tokens ──  │  ┌───────────────────────────┐   │
│  (port 3000)     │    stream      │  │   /upload /chat /auth     │   │
└──────────────────┘                │  │   /sessions /eval         │   │
                                    │  └───────────┬───────────────┘   │
                                    │              │                    │
                                    │  ┌───────────▼───────────────┐   │
                                    │  │      RAG Pipeline          │   │
                                    │  │  BM25 + Vector → RRF      │   │
                                    │  │  → Cross-Encoder Rerank    │   │
                                    │  │  → Groq LLM (stream)      │   │
                                    │  └───┬──────┬───────┬─────────┘   │
                                    │      │      │       │              │
                                    │  ┌───▼──┐ ┌─▼────┐ ┌▼──────────┐  │
                                    │  │Qdrant│ │BM25  │ │Embeddings │  │
                                    │  │      │ │      │ │+Reranker  │  │
                                    │  └──────┘ └──────┘ └───────────┘  │
                                    │  ┌─────────────┐ ┌────────────┐   │
                                    │  │  Groq API   │ │  SQLite    │   │
                                    │  │  (Llama 3.3 │ │  (users,   │   │
                                    │  │   70B)      │ │  history)  │   │
                                    │  └─────────────┘ └────────────┘   │
                                    └──────────────────────────────────┘
```

## Features

- **PDF Upload** — drag & drop, text extraction, 500-token chunking
- **Hybrid Retrieval** — BM25 (keyword) + vector (semantic) fused via RRF
- **Cross-Encoder Reranking** — re-scores top-k for precision
- **Streaming Chat** — token-by-token via Server-Sent Events
- **Citations** — every answer links back to source pages
- **Auth** — JWT-based registration and login
- **Chat History** — sessions persisted in SQLite
- **Multi-User** — per-user document and chat isolation
- **RAGAS Eval** — automated faithfulness, relevance, precision metrics

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic v2 |
| LLM | Groq (`llama-3.3-70b-versatile`) — free tier, 128K context |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| Vector DB | Qdrant (Rust-based, native multi-tenancy) |
| Keyword Search | rank-bm25 |
| Frontend | Next.js 14, React, Tailwind CSS |
| Auth | python-jose (JWT), passlib (bcrypt) |
| Eval | RAGAS |
| Deploy | Docker Compose, Render + Vercel |

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for Qdrant)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone
git clone https://github.com/yourusername/docmind-rag.git
cd docmind-rag

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env  # add your GROQ_API_KEY
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker

```bash
# Start Qdrant
docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant:latest

# Or start everything
docker compose up
```

Open [http://localhost:3000](http://localhost:3000).

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user |
| POST | `/api/documents/upload` | Upload PDF |
| GET | `/api/documents` | List documents |
| DELETE | `/api/documents/{id}` | Delete document |
| POST | `/api/chat` | Stream chat (SSE) |
| GET | `/api/sessions` | List chat sessions |
| GET | `/api/sessions/{id}/messages` | Chat history |
| POST | `/api/eval` | Run RAGAS evaluation |
| GET | `/health` | Health check |

## Project Structure

```
docmind-rag/
├── backend/
│   ├── api/            # FastAPI routers
│   ├── core/           # Config, security, database, models
│   ├── rag/            # RAG pipeline
│   │   ├── chunking.py       # PDF extraction + chunking
│   │   ├── vectorstore.py    # Qdrant integration
│   │   ├── bm25_index.py     # BM25 keyword search
│   │   ├── retrieval.py      # Hybrid search + RRF
│   │   ├── reranker.py       # Cross-encoder reranking
│   │   ├── llm.py            # Groq integration
│   │   └── evaluation.py     # RAGAS metrics
│   ├── models/         # SQLAlchemy + Pydantic models
│   └── services/       # Business logic
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages
│       ├── components/     # React components
│       └── lib/            # API client
├── docs/
│   └── PRD.md          # Product Requirements Document
├── .github/workflows/  # CI pipeline
├── docker-compose.yml
└── AGENTS.md           # AI coding practices
```

## Evaluation

```bash
curl -X POST http://localhost:8000/api/eval \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "test_data": [
      {
        "question": "What is the revenue growth?",
        "ground_truth": "Revenue grew 12% this quarter."
      }
    ]
  }'
```

Returns: faithfulness, answer_relevancy, context_precision, context_recall.

## License

MIT
