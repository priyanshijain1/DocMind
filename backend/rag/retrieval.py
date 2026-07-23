from rag.vectorstore import search as search_vector
from rag.bm25_index import search_bm25
from rag.reranker import rerank


def reciprocal_rank_fusion(lists: list[list[dict]], k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    doc_map: dict[str, dict] = {}

    for ranked_list in lists:
        for rank, doc in enumerate(ranked_list):
            key = f"{doc['doc_id']}:{doc['page']}:{doc['chunk_index'] if 'chunk_index' in doc else doc['text'][:50]}"
            scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)
            doc_map[key] = doc

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [{**doc_map[key], "score": score} for key, score in ranked]


def hybrid_search(query: str, user_id: str, top_k: int = 10, top_n: int = 5) -> list[dict]:
    vector_results = search_vector(query, user_id, top_k=top_k)
    bm25_results = search_bm25(query, user_id=user_id, top_k=top_k)

    if not vector_results and not bm25_results:
        return []

    if not vector_results:
        candidates = bm25_results[:top_k]
    elif not bm25_results:
        candidates = vector_results[:top_k]
    else:
        candidates = reciprocal_rank_fusion([vector_results, bm25_results])[:top_k]

    results = rerank(query, candidates, top_n=top_n)
    for r in results:
        r["score"] = round(r.pop("rerank_score", r.get("score", 0)), 4)
    return results
