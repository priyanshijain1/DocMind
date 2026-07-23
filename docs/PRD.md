# Product Requirements Document (PRD)
## DocMind — Retrieval-Augmented Generation (RAG) Chat over PDFs

**Version:** 1.1
**Status:** Approved — ready for Phase 1
**Author:** [Your Name]
**Last updated:** 2026-07-22

---

## 1. Executive Summary

DocMind is a web application that lets users upload PDF documents and have a
natural-language conversation with them. It uses Retrieval-Augmented Generation
(RAG): user questions are used to retrieve the most relevant passages from the
uploaded documents, and a Large Language Model (LLM) generates a grounded answer
with **citations** back to the source.

The project is built as a **portfolio/resume showcase** demonstrating production-grade
engineering practices: clean architecture, streaming responses, hybrid retrieval,
reranking, evaluation metrics, authentication, and containerized deployment.

---

## 2. Problem Statement

- **Users** struggle to extract answers from long PDFs (research papers, contracts,
  manuals, lecture notes). Manual Ctrl+F is slow and doesn't understand context.
- **Generic chatbots** (e.g. free ChatGPT) cannot see your private documents and
  often hallucinate.
- **Existing tools** (ChatPDF, NotebookLM) are great but closed-source — there's
  no easy way to learn how they actually work under the hood.

DocMind solves this by combining accurate retrieval with a grounded LLM, while
also being a transparent, build-it-yourself reference implementation.

---

## 3. Goals & Non-Goals

### Goals
1. Let a user upload one or more PDFs and ask questions about their content.
2. Return **grounded** answers with clickable citations to source passages.
3. Stream answers token-by-token for a responsive UX.
4. Use **advanced retrieval** (hybrid + reranking) for high answer quality.
5. Provide **objective evaluation metrics** (RAGAS) so quality is measurable.
6. Support multiple users with isolated document libraries and chat history.
7. Ship a **deployed, containerized** application viewable by recruiters.

### Non-Goals (explicitly out of scope)
- OCR for scanned/image-only PDFs (text-based PDFs only in v1).
- Multi-modal RAG (images, tables, audio) — possible future work.
- Fine-tuning models — we use off-the-shelf LLMs.
- Mobile-native apps (web responsive only).
- Real-time collaborative editing.

---

## 4. Target Users / Personas

| Persona | Need |
|---|---|
| **Students** | Q&A over lecture notes, textbooks, research papers |
| **Recruiters / hiring managers** | Evaluating the author's engineering skills (primary "user" for resume purposes) |
| **Knowledge workers** | Summarize/extract answers from contracts, reports, manuals |
| **Developers learning RAG** | Reference implementation to study |

---

## 5. User Stories

**MVP**
- *As a user*, I can upload a PDF so that I can ask questions about it.
- *As a user*, I can ask a question in a chat box and receive a streamed answer.
- *As a user*, I can see which part of the PDF the answer came from (citation).
- *As a user*, I receive a clear message when no relevant context is found.

**V1 (Quality)**
- *As a user*, answers are accurate even when keywords don't match (hybrid search).
- *As a user*, I can see a confidence/quality indicator per answer.

**V2 (Production)**
- *As a user*, I can sign up, log in, and access only my own documents/chats.
- *As a user*, I can revisit previous conversations from history.
- *As an admin*, I can run an evaluation script that reports faithfulness/relevance.

---

## 6. Functional Requirements

### 6.1 MVP (Phase 1)
| ID | Requirement | Priority |
|---|---|---|
| F1 | Upload PDF (drag & drop, ≤ 25 MB) | Must |
| F2 | Extract text, chunk into ~500-token passages with overlap | Must |
| F3 | Generate embeddings and store in vector DB | Must |
| F4 | Semantic search: top-k relevant chunks per question | Must |
| F5 | LLM generates answer using retrieved context (prompt template) | Must |
| F6 | Stream answer to UI token-by-token | Must |
| F7 | Show source citations (page + snippet) | Must |
| F8 | Show "no relevant context" fallback when score is below threshold | Must |

### 6.2 V1 — Retrieval Quality (Phase 2)
| ID | Requirement | Priority |
|---|---|---|
| F9 | Hybrid retrieval: BM25 (keyword) + dense (vector), score-fused via RRF | Must |
| F10 | Cross-encoder reranker on top-k candidates → top-n final | Must |
| F11 | RAGAS evaluation pipeline (faithfulness, answer relevance, context precision/recall) | Must |
| F12 | `/eval` endpoint returns metrics over a labeled test set | Should |

### 6.3 V2 — Production (Phase 3)
| ID | Requirement | Priority |
|---|---|---|
| F13 | User registration + login (JWT, bcrypt passwords) | Must |
| F14 | Per-user document isolation in vector DB (namespace / metadata filter) | Must |
| F15 | Persist chat sessions + messages in SQLite/Postgres | Must |
| F16 | List / rename / delete chat sessions | Should |

### 6.4 V3 — Ship (Phase 4)
| ID | Requirement | Priority |
|---|---|---|
| F17 | Dockerfile + docker-compose for backend + frontend | Must |
| F18 | Deploy to free tier (Render / Railway / Fly.io) | Must |
| F19 | Polished README with architecture diagram, screenshots, run instructions | Must |
| F20 | CI: run lint + tests on push (GitHub Actions) | Should |

---

## 7. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | First token streamed in < 3s on a typical query; ingestion of a 50-page PDF in < 60s |
| **Latency (UI)** | Time-to-first-token visible to user within 1.5s of request |
| **Cost** | Total project cost ≤ $10 USD using API free tiers |
| **Security** | Passwords hashed (bcrypt); JWT in httpOnly cookie / Authorization header; no secrets in repo |
| **Privacy** | User documents stored locally per user; option to delete on logout |
| **Observability** | Structured logs (loguru) with request IDs for tracing; request timing; retrieval scores logged |
| **Maintainability** | Modular code (clear `core/`, `rag/`, `api/` separation), type hints, docstrings |
| **Testability** | Unit tests for chunking, retrieval, prompt building; ≥ 60% coverage on core logic |
| **Portability** | Runs identically locally and in Docker |
| **CORS** | FastAPI CORS middleware configured for frontend origin (`localhost:3000` in dev, Vercel URL in prod) |
| **Validation** | All API requests validated via Pydantic models; malformed input → 400 with clear error message |
| **Error Handling** | Graceful fallback on Groq API failure (user-facing message, no crash); malformed/encrypted PDFs → 400; rate limit hit → 429 with cooldown message |
| **Graceful Shutdown** | Backend handles SIGTERM; closes DB connections and vector store cleanly |

---

## 8. Technical Architecture

```
┌────────────────────┐    HTTP/SSE     ┌──────────────────────────────────┐
│  Next.js Frontend  │ ──────────────▶ │         FastAPI Backend          │
│  React + shadcn/ui │                 │  ┌───────────────────────────┐   │
│  (port 3000)       │ ◀── token ────  │  │   API Layer (routes)      │   │
│                    │    stream       │  │   - /upload /chat /auth   │   │
└────────────────────┘                 │  │   - SSE streaming          │   │
                                       │  │   - Pydantic validation    │   │
                                       │  └───────────┬───────────────┘   │
                                       │              │                    │
                                       │  ┌───────────▼───────────────┐   │
                                       │  │      RAG Pipeline          │   │
                                       │  │  ingest → embed → store    │   │
                                       │  │  retrieve → rerank → LLM   │   │
                                       │  └───┬──────┬───────┬─────────┘   │
                                       │      │      │       │              │
                                       │  ┌───▼──┐ ┌─▼────┐ ┌▼──────────┐  │
                                       │  │Qdrant│ │BM25  │ │Embeddings │  │
                                       │  │Vector│ │Index │ │+Reranker  │  │
                                       │  │(Rust)│ │      │ │(HF local) │  │
                                       │  └──────┘ └──────┘ └───────────┘  │
                                       │  ┌─────────────┐ ┌────────────┐   │
                                       │  │  Groq API   │ │  SQLite    │   │
                                       │  │ (llama-3.3  │ │ (users,    │   │
                                       │  │  -70b)      │ │  history)  │   │
                                       │  └─────────────┘ └────────────┘   │
                                       └──────────────────────────────────┘
```

### Request flow (chat)
1. Frontend POSTs `{question, session_id}` to `/api/chat` with JWT header.
2. Backend authenticates user, validates input via Pydantic.
3. Runs **hybrid retrieval** (vector + BM25, RRF-fused).
4. **Cross-encoder reranker** re-scores top-k → top-n passages.
5. If best score < threshold → return "no relevant context".
6. Else: build prompt with citations, call **Groq API** (`stream=True`).
7. Tokens are sent to client via **Server-Sent Events (SSE)**.
8. Final message + sources persisted to SQLite.
9. Request ID logged with timing and retrieval scores.

---

## 9. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.11 | Industry standard for ML/LLM work |
| LLM orchestration | LangChain | User requested; widely used in industry |
| LLM provider | **Groq** (`llama-3.3-70b-versatile`) | Free tier (30 req/min), ultra-low latency, strong reasoning |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) | Free, fast, high quality (local, no API cost) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Free, well-known, runs locally |
| Vector DB | **Qdrant** (Rust-based, local Docker or free cloud) | Production-grade, native multi-tenancy, pre-filter HNSW, 5/5 resume signal |
| Keyword search | `rank-bm25` | Lightweight, well-known algorithm |
| Backend | **FastAPI** + Uvicorn | Async, auto-docs (Swagger), Pydantic validation |
| Frontend | **Next.js 14** (App Router) + React + shadcn/ui | SSR capable, streaming support, Vercel deploy |
| Auth | `python-jose` (JWT) + `passlib[bcrypt]` | Standard, secure |
| Database | SQLite via SQLAlchemy | Zero-config; easy upgrade path to Postgres |
| Eval | **RAGAS** | Industry-standard RAG metrics |
| Testing | pytest + pytest-asyncio | Standard Python testing |
| Linting | ruff + black | Modern, fast |
| Container | Docker + docker-compose | Reproducible deploys |
| Deploy | Render (backend) + Vercel (frontend) | Both free tier, native support for respective frameworks |

---

## 10. Data Model

### SQLite tables

```
users
  id (PK, uuid)
  email (unique)
  password_hash
  created_at

documents
  id (PK, uuid)
  user_id (FK → users.id)
  filename
  num_pages
  num_chunks
  qdrant_namespace      -- isolates vectors per user/doc
  created_at

chat_sessions
  id (PK, uuid)
  user_id (FK)
  document_id (FK, nullable)
  title
  created_at

messages
  id (PK, uuid)
  session_id (FK → chat_sessions.id)
  role (user | assistant)
  content
  sources (JSON)        -- list of {doc_id, page, snippet, score}
  created_at
```

### Qdrant collection
- Single collection `docmind_chunks`.
- Each chunk's payload (metadata): `{user_id, doc_id, page, chunk_index, text}`.
- Queries always filtered by `user_id` metadata for tenant isolation.
- Pre-filter HNSW ensures performance stays strong with user filtering.

---

## 11. API Design (key endpoints)

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Returns JWT |
| GET  | `/api/auth/me` | Current user |
| POST | `/api/documents/upload` | Upload PDF, ingest |
| GET  | `/api/documents` | List user's docs |
| DELETE | `/api/documents/{id}` | Delete doc + its vectors |
| POST | `/api/chat` | **SSE stream** answer for a question |
| GET  | `/api/sessions` | List chat sessions |
| GET  | `/api/sessions/{id}/messages` | Chat history |
| POST | `/api/eval` | Run RAGAS eval (admin/debug) |
| GET  | `/health` | Liveness probe (checks DB, Qdrant, Groq) |

**CORS:** FastAPI middleware allows `http://localhost:3000` (dev) and `https://*.vercel.app` (prod).

---

## 12. Success Metrics

### Product quality
- **Faithfulness ≥ 0.85** (RAGAS) on a held-out Q&A test set.
- **Context precision ≥ 0.75** on the same set.
- **Time-to-first-token < 3 s** for 95th percentile query.
- **Zero cost**: Groq free tier + local embeddings + Qdrant (local) = $0 running cost.

### Engineering quality
- ≥ 60% test coverage on `core/` and `rag/` modules.
- All PR checks green (ruff, black, pytest).
- One-command local start: `docker compose up`.

### Resume / portfolio impact
- Live demo URL accessible to recruiters.
- README with: architecture diagram, screenshots, GIF of streaming, eval results table.
- Code on GitHub with clear commit history and PR-style workflow.

---

## 13. Milestones & Timeline

| Milestone | Scope | Est. effort |
|---|---|---|
| **M0 — PRD approved** | This document signed off; all decisions resolved | Done today |
| **M1 — MVP** | F1–F8: upload, ingest, vector search (Qdrant), streaming chat, citations, Groq integration | 2–3 sessions |
| **M2 — Quality** | F9–F12: hybrid + rerank + RAGAS eval | 1–2 sessions |
| **M3 — Production** | F13–F16: auth + history + multi-user | 1–2 sessions |
| **M4 — Ship** | F17–F20: Docker + deploy (Render+Vercel) + README + CI | 1 session |

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| API costs run high | Low | Med | Groq free tier (30 req/min); embeddings are local (free); cache them |
| Groq rate limit (30 req/min) | Med | Med | Client-side debounce, request queue, show cooldown message on 429 |
| Groq API outage | Low | Med | Graceful fallback message; retry with exponential backoff |
| Slow streaming on Windows | Low | Med | Test early; use SSE not WebSocket |
| Hallucinated answers | Med | High | Strict prompt, low-score fallback, RAGAS eval gate |
| Qdrant free tier auto-suspends after 1 week inactivity | Low | Low | Use local Docker in dev; free tier is backup for demo only |
| Free-tier deploy limits | Med | Low | Keep app stateless; SQLite → Postgres if needed |
| Scanned PDFs (no text) | Med | Med | Detect & reject upfront with clear message |
| Resume reviewer doesn't run it | High | Med | Provide hosted demo URL + screenshots + GIF in README |

---

## 15. Resolved Decisions

> All open questions resolved as of 2026-07-22.

| Question | Decision | Rationale |
|---|---|---|
| LLM provider | **Groq** (`llama-3.3-70b-versatile`) | Free, ultra-fast, strong reasoning. 128K context window. |
| Project name | **DocMind** | Clean, professional, easy to remember. |
| Frontend | **Next.js 14** + React + shadcn/ui | More impressive for Backend/SWE resume; Vercel deploy is free. |
| Resume target | **Backend / SWE** | Emphasize API design, testing, Docker, clean architecture. |
| Deployment | **Render** (backend) + **Vercel** (frontend) | Both free tier, native framework support. |

---

## 16. Appendix

### A. RAG concepts (1-line each, for reviewers)
- **Embedding** — converts text → vector of numbers capturing meaning.
- **Qdrant** — Rust-based vector database with native multi-tenancy and pre-filter HNSW search.
- **Vector DB** — stores vectors; finds nearest neighbors fast.
- **Chunking** — splits long docs into passages so retrieval is precise.
- **Semantic search** — matches by meaning, not keywords.
- **BM25** — classic keyword search based on term frequency; complements semantic search.
- **Hybrid search** — combines BM25 + semantic for best of both worlds.
- **RRF (Reciprocal Rank Fusion)** — merges two ranked lists into one score.
- **Reranker** — a more expensive model re-scores the top candidates for precision.
- **Cross-encoder** — reranker architecture that reads query+passage jointly (more accurate, slower).
- **RAGAS** — automatic metrics for RAG quality (faithfulness, context relevance, etc.).
- **SSE** — Server-Sent Events; how we stream tokens to the browser.
- **Groq** — LPU inference provider offering free-tier access to Llama 3.3 70B.
- **Next.js** — React framework with SSR, streaming, and API routes; deployed on Vercel.

### B. Example prompt template (draft)
```
You are DocMind, an AI assistant that answers questions strictly
based on the provided context. Always cite your sources using [1], [2], etc.
If the answer is not found in the context, say:
"I couldn't find this in the uploaded documents." — do not guess.

---
Context (retrieved passages):
[1] (page 4, doc: report.pdf) "The quarterly revenue increased by 12%..."
[2] (page 7, doc: report.pdf) "Customer churn rate dropped to 3.2%..."
---

Question: What was the revenue growth this quarter?

Answer:
```

- Model: `llama-3.3-70b-versatile` via Groq (128K context window).
- Max context budget: ~10K tokens (leaves room for question + answer).
- Chunk size target: ~500 tokens ≈ 300–400 words per chunk.
