from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from core.config import settings
from core.database import init_db
from api.documents import router as documents_router
from api.chat import router as chat_router
from api.eval import router as eval_router
from api.auth import router as auth_router
from api.sessions import router as sessions_router

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(eval_router)
app.include_router(auth_router)
app.include_router(sessions_router)


@app.on_event("startup")
async def startup():
    await init_db()
    from rag.vectorstore import load_all_chunks
    from rag.bm25_index import load_chunks

    chunks = load_all_chunks()
    load_chunks(chunks)
    logger.info(f"BM25 index rebuilt: {len(chunks)} chunks loaded")


@app.get("/health")
async def health():
    return {"status": "ok"}
