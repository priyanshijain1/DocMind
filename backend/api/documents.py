import os
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.models import Document, User
from core.security import get_current_user
from rag.chunking import extract_text, chunk_pages
from rag.vectorstore import ensure_collection, embed_chunks, upsert_chunks
from rag.bm25_index import index_chunks

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 25 MB")

    doc_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    with open(pdf_path, "wb") as f:
        f.write(content)

    pages = extract_text(pdf_path)
    if not pages:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    chunks = chunk_pages(pages, settings.chunk_size, settings.chunk_overlap)

    ensure_collection()
    embeddings = embed_chunks(chunks)
    upsert_chunks(doc_id, user.id, chunks, embeddings)

    chunks_with_doc = [{**c, "doc_id": doc_id} for c in chunks]
    index_chunks(chunks_with_doc)

    doc = Document(
        id=doc_id,
        user_id=user.id,
        filename=file.filename,
        num_pages=len(pages),
        num_chunks=len(chunks),
    )
    db.add(doc)
    await db.commit()

    return {
        "id": doc_id,
        "filename": file.filename,
        "num_pages": len(pages),
        "num_chunks": len(chunks),
    }
