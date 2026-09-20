"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    query_vectors = embed_texts([query])
    if not query_vectors:
        return []

    collection = get_collection()
    response = collection.query(
        query_embeddings=query_vectors,
        n_results=max(1, top_k),
        include=["documents", "metadatas", "distances"],
    )

    if not response or not response.get("ids") or not response["ids"][0]:
        return []

    results = []
    seen_ids = set()

    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        meta = dict(metadata) if metadata else {}
        if meta.get("url") == "":
            meta["url"] = None

        # Cosine distance to similarity: similarity = 1 - distance
        score = max(0.0, 1.0 - float(distance))
        results.append({
            "id": item_id,
            "content": content,
            "score": float(score),
            "metadata": meta,
            "retrieval_method": "dense",
        })

    # Sort descending by score
    sorted_results = sorted(results, key=lambda item: item["score"], reverse=True)
    return sorted_results[:top_k]


if __name__ == "__main__":
    for result in semantic_search("quy chế học vụ vinuni", top_k=3):
        print(result)
