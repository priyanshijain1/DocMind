from rank_bm25 import BM25Okapi

_chunk_store: list[dict] = []
_bm25: BM25Okapi | None = None


def index_chunks(chunks: list[dict]):
    global _chunk_store, _bm25
    _chunk_store.extend(chunks)
    tokenized = [c["text"].lower().split() for c in _chunk_store]
    _bm25 = BM25Okapi(tokenized)


def search_bm25(query: str, top_k: int = 10) -> list[dict]:
    if not _bm25 or not _chunk_store:
        return []
    tokenized = query.lower().split()
    scores = _bm25.get_scores(tokenized)
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
    return [
        {
            "text": _chunk_store[i]["text"],
            "page": _chunk_store[i]["page"],
            "doc_id": _chunk_store[i]["doc_id"],
            "score": float(score),
        }
        for i, score in ranked
    ]
