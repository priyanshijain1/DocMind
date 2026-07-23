import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db
from core.models import User
from core.security import get_current_user
from models.schemas import ChatRequest
from rag.retrieval import hybrid_search
from rag.llm import get_llm, build_messages

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sources = hybrid_search(req.question, user_id=user.id, top_k=settings.retrieval_top_k)

    if not sources:
        return {"answer": "I couldn't find this in the uploaded documents.", "sources": []}

    llm = get_llm()
    messages = build_messages(req.question, sources)

    async def stream():
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield f"data: {json.dumps({'token': chunk.content})}\n\n"
        yield f"data: {json.dumps({'sources': sources})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
