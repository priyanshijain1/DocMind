import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.database import get_db
from core.models import User, ChatSession, Message
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
    if req.session_id:
        result = await db.execute(select(ChatSession).where(ChatSession.id == req.session_id))
        session = result.scalar_one_or_none()
    else:
        session = ChatSession(user_id=user.id, title=req.question[:80])
        db.add(session)
        await db.commit()
        await db.refresh(session)

    user_msg = Message(session_id=session.id, role="user", content=req.question)
    db.add(user_msg)
    await db.commit()

    sources = hybrid_search(req.question, user_id=user.id, top_k=settings.retrieval_top_k)

    if not sources:
        answer = "I couldn't find this in the uploaded documents."
        assistant_msg = Message(session_id=session.id, role="assistant", content=answer, sources="[]")
        db.add(assistant_msg)
        await db.commit()
        return {"answer": answer, "sources": [], "session_id": session.id}

    llm = get_llm()
    messages = build_messages(req.question, sources)
    full_answer = ""

    async def stream():
        nonlocal full_answer
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_answer += chunk.content
                yield f"data: {json.dumps({'token': chunk.content})}\n\n"

        sources_json = json.dumps(sources)
        assistant_msg = Message(session_id=session.id, role="assistant", content=full_answer, sources=sources_json)
        db.add(assistant_msg)
        await db.commit()

        yield f"data: {json.dumps({'sources': sources, 'session_id': session.id})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
