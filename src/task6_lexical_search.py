"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 4. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []


def ensure_corpus() -> list[dict]:
    """Tự động nạp corpus chunks nếu CORPUS chưa được gán."""
    global CORPUS
    if not CORPUS:
        from .task4_chunking_indexing import load_documents, chunk_documents
        documents = load_documents()
        CORPUS = chunk_documents(documents)
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ danh sách corpus chunks."""
    tokenized = [item["content"].lower().split() for item in corpus]
    bm25 = BM25Okapi(tokenized)
    # Đảm bảo IDF luôn dương đối với các tập corpus nhỏ (tránh ln(1) = 0 trong Okapi)
    for word, val in bm25.idf.items():
        if val <= 0:
            bm25.idf[word] = 0.5
    return bm25


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    corpus = CORPUS if CORPUS else ensure_corpus()
    if not corpus:
        return []

    tokens = query.lower().split()
    if not tokens:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(tokens)

    ranked_pairs = sorted(
        enumerate(scores),
        key=lambda pair: float(pair[1]),
        reverse=True
    )

    results = []
    seen_ids = set()

    for idx, score in ranked_pairs:
        if score <= 0:
            continue
        item = corpus[idx]
        item_id = item["id"]
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        meta = dict(item["metadata"])
        if meta.get("url") == "":
            meta["url"] = None

        results.append({
            "id": item_id,
            "content": item["content"],
            "score": float(score),
            "metadata": meta,
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    for result in lexical_search("học bổng CGPA", top_k=3):
        print(result)
