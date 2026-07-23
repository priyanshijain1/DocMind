from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DocMind"
    debug: bool = False

    groq_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "sqlite+aiosqlite:///./docmind.db"
    jwt_secret: str = "change-me-in-production"

    embedding_model: str = "all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 20
    rerank_top_n: int = 3

    class Config:
        env_file = "../.env"


settings = Settings()
