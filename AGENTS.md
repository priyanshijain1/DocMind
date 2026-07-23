# AGENTS.md — DocMind Coding Practices

## Project Overview
DocMind is a RAG (Retrieval-Augmented Generation) chat application for PDF documents.
- **Backend**: Python 3.11, FastAPI, LangChain, Qdrant, SQLite
- **Frontend**: Next.js 14, React, shadcn/ui
- **LLM**: Groq (`llama-3.3-70b-versatile`)
- **Embeddings**: `sentence-transformers` (local)
- **Reranker**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (local)

---

## Core Engineering Philosophy

### Before Writing Any Code, Ask:
1. **Does this already exist?** — Reuse existing structures, utilities, patterns in the codebase
2. **Is this justifiable?** — Every decision must have a clear reason (cost, latency, maintainability)
3. **Does this add complexity?** — If yes, is the complexity proportional to the value?
4. **Will this confuse future me/interviewer?** — Code should be obvious, not clever

### Zero Tolerance
- **No ghost code**: Every line must serve a purpose; delete unused imports, variables, functions
- **No summary code**: Don't create abstractions just to "organize" — keep logic flat when possible
- **No premature optimization**: Build simple first, optimize only when measured bottleneck exists
- **No unnecessary abstractions**: Only create new classes/functions when reuse is certain (3+ times)

### Decision Framework
```
Is there an existing pattern in the codebase? → USE IT
Is there a standard library solution?          → USE IT
Is there a well-known library for this?        → EVALUATE (cost vs benefit)
Should I create a new abstraction?             → ONLY IF reused 3+ times
Should I add a comment?                        → ONLY IF logic is non-obvious
```

---

## Code Style & Formatting

### Python
- **Formatter**: `black` (line length 88)
- **Linter**: `ruff` (replaces flake8, isort, pylint)
- **Type hints**: Required on all function signatures and return types
- **Docstrings**: Google-style docstrings on public functions/classes
- **Imports**: Sorted by `ruff` (isort-compatible)
- Run before commit:
  ```bash
  ruff check . --fix
  black .
  ```

### TypeScript/React (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint (Next.js config)
- Run before commit:
  ```bash
  npm run lint
  ```

---

## Architecture Conventions

### Backend Structure
```
backend/
├── api/            # FastAPI routers (endpoints)
├── core/           # Config, security, database, dependencies
├── rag/            # RAG pipeline: ingest, retrieve, rerank, generate
├── models/         # SQLAlchemy + Pydantic models
├── services/       # Business logic layer
└── tests/          # pytest tests (mirrors src structure)
```

### Key Principles
1. **Separation of concerns**: API layer handles HTTP; services handle logic; core handles infra
2. **Dependency injection**: Use FastAPI's `Depends()` for DB sessions, auth, config
3. **Pydantic validation**: All request/response models use Pydantic v2
4. **Async by default**: Use `async def` for all endpoint handlers
5. **No secrets in code**: Use `.env` files; never commit API keys

---

## Testing Requirements

### Coverage Targets
- `core/` and `rag/` modules: ≥ 60% coverage
- All new features must include tests

### Test Structure
```
tests/
├── unit/           # Fast, isolated tests (no external deps)
├── integration/    # Tests with real DB/vector store
└── fixtures/       # Shared test data
```

### Test Commands
```bash
pytest                    # Run all tests
pytest --cov=backend      # With coverage
pytest -x                 # Stop on first failure
```

### Test Guidelines
- Use `pytest-asyncio` for async tests
- Mock external services (Groq API, Qdrant) in unit tests
- Use fixtures for test data; avoid hardcoded values
- Name tests: `test_<function>_<scenario>_<expected>`
- Test both success and error paths

---

## Git Workflow

### Branch Strategy
- `main` — production-ready code
- `feat/*` — feature branches
- `fix/*` — bug fix branches
- `chore/*` — maintenance tasks

### Commit Messages
Format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`
- Example: `feat(rag): add hybrid retrieval with BM25 + vector`

### PR Requirements
- All CI checks pass (ruff, black, pytest)
- At least one review before merge
- Squash merge to keep history clean

---

## Security Practices

1. **Never commit secrets**: API keys, passwords, JWT secrets go in `.env`
2. **Password hashing**: Use `bcrypt` via `passlib` for user passwords
3. **JWT**: Short-lived tokens (15 min); use `httpOnly` cookies in production
4. **Input validation**: Validate all inputs via Pydantic; reject malformed data
5. **SQL injection**: Use SQLAlchemy ORM; never raw SQL with user input
6. **File uploads**: Validate PDF type; enforce 25 MB max size
7. **CORS**: Configure explicitly for known origins only

---

## Performance Guidelines

1. **Streaming**: Use SSE for chat responses; never buffer entire response
2. **Async I/O**: Use `async/await` for DB, HTTP, file operations
3. **Chunking**: Target ~500 tokens per chunk; 50-100 token overlap
4. **Caching**: Cache embeddings for repeated chunks; cache model loading
5. **Rate limiting**: Implement client-side debounce; handle 429 errors gracefully

---

## Error Handling

1. **API errors**: Return proper HTTP status codes (400, 401, 403, 404, 429, 500)
2. **User-facing messages**: Clear, actionable error messages (no stack traces)
3. **Logging**: Use `loguru` with request IDs for tracing
4. **Graceful degradation**: If Groq fails, show fallback message; don't crash
5. **PDF validation**: Reject encrypted/scanned PDFs with clear message

---

## Documentation

- **Docstrings**: Required on all public functions/classes
- **API docs**: Auto-generated via FastAPI's Swagger UI (`/docs`)
- **README**: Keep updated with setup instructions, architecture, screenshots
- **Inline comments**: Only for complex logic; don't over-comment

---

## Environment Setup

### Required Environment Variables
```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=http://localhost:6333
DATABASE_URL=sqlite:///./docmind.db
JWT_SECRET=your_jwt_secret
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Key Reminders

- [ ] Run `ruff check . --fix && black .` before committing Python code
- [ ] Run `npm run lint` before committing frontend code
- [ ] Write tests for new features; aim for 60%+ coverage on core/rag
- [ ] Never commit `.env` files or secrets
- [ ] Use type hints on all function signatures
- [ ] Handle errors gracefully; never expose stack traces to users
- [ ] Test streaming responses end-to-end
- [ ] Validate PDF uploads before processing
