import uuid
from datetime import datetime, timezone

from pydantic import BaseModel


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentResponse(BaseModel):
    id: str
    filename: str
    num_pages: int
    num_chunks: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]
    session_id: str


class Source(BaseModel):
    doc_id: str
    page: int
    snippet: str
    score: float


class EvalRequest(BaseModel):
    test_data: list[dict]
