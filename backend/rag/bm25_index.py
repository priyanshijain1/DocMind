from rank_bm25 import BM25Okapi

_chunk_store: list[dict] = []
_bm25: BM25Okapi | None = None


def load_chunks(chunks: list[dict]):
    global _chunk_store, _bm25
    _chunk_store = chunks
    if _chunk_store:
        tokenized = [c["text"].lower().split() for c in _chunk_store]
        _bm25 = BM25Okapi(tokenized)
    else:
        _bm25 = None


def index_chunks(chunks: list[dict]):
    global _chunk_store, _bm25
    _chunk_store.extend(chunks)
    tokenized = [c["text"].lower().split() for c in _chunk_store]
    _bm25 = BM25Okapi(tokenized)


def search_bm25(query: str, user_id: str, top_k: int = 10) -> list[dict]:
    if not _bm25 or not _chunk_store:
        return []

    user_chunks = [(i, c) for i, c in enumerate(_chunk_store) if c.get("user_id") == user_id]
    if not user_chunks:
        return []

    tokenized_query = query.lower().split()
    tokenized_corpus = [c["text"].lower().split() for _, c in user_chunks]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        {
            "text": user_chunks[i][1]["text"],
            "page": user_chunks[i][1]["page"],
            "doc_id": user_chunks[i][1]["doc_id"],
            "score": float(score),
        }
        for i, score in ranked
    ]
