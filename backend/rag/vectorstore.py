from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

from core.config import settings

client = QdrantClient(url=settings.qdrant_url)
embedding_model = SentenceTransformer(settings.embedding_model)

COLLECTION = "docmind_chunks"


def ensure_collection():
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    texts = [c["text"] for c in chunks]
    return embedding_model.encode(texts).tolist()


def upsert_chunks(doc_id: str, user_id: str, chunks: list[dict], embeddings: list[list[float]]):
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "doc_id": doc_id,
                    "user_id": user_id,
                    "page": chunk["page"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "source": "vector",
                },
            )
        )
    client.upsert(collection_name=COLLECTION, points=points)


def search(query: str, user_id: str, top_k: int = 10) -> list[dict]:
    query_vector = embedding_model.encode([query]).tolist()[0]
    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
    )
    return [
        {
            "text": r.payload["text"],
            "page": r.payload["page"],
            "doc_id": r.payload["doc_id"],
            "score": r.score,
        }
        for r in results
    ]


def delete_doc_vectors(doc_id: str):
    client.delete(
        collection_name=COLLECTION,
        points_selector={"filter": {"must": [{"key": "doc_id", "match": {"value": doc_id}}]}},
    )
