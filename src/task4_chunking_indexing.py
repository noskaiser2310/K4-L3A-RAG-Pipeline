"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng Recursive Text Splitter (chunk_size=500, overlap=50).
    3. Embed chunks bằng Google Gemini Embedding (gemini-embedding-001, 3072 dims) hoặc SentenceTransformer fallback.
    4. Upsert vào ChromaDB với cosine distance (hoặc local vectorstore tương thích 100% API).
"""

import json
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIM = 3072
COLLECTION_NAME = "rag_documents"

_MODEL_INSTANCE = None


class LocalVectorCollection:
    """Tương thích 100% giao diện ChromaDB Collection với cosine distance."""
    def __init__(self, storage_dir: Path, name: str):
        self.storage_dir = storage_dir
        self.name = name
        self.storage_file = storage_dir / f"{name}.json"
        self.data: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.storage_file.exists():
            try:
                self.data = json.loads(self.storage_file.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}

    def _save(self):
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def upsert(self, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]):
        for item_id, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
            self.data[item_id] = {
                "id": item_id,
                "document": doc,
                "embedding": emb,
                "metadata": meta,
            }
        self._save()

    def query(self, query_embeddings: list[list[float]], n_results: int = 10, include: list[str] = None) -> dict:
        if not query_embeddings or not self.data:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

        import numpy as np

        q_vec = np.array(query_embeddings[0], dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        scored_items = []
        for item in self.data.values():
            vec = np.array(item["embedding"], dtype=np.float32)
            v_norm = np.linalg.norm(vec)
            if v_norm > 0:
                vec = vec / v_norm
            cos_sim = float(np.dot(q_vec, vec))
            cos_dist = max(0.0, 1.0 - cos_sim)
            scored_items.append((cos_dist, item))

        scored_items.sort(key=lambda pair: pair[0])
        top_items = scored_items[:n_results]

        ids = [item["id"] for _, item in top_items]
        docs = [item["document"] for _, item in top_items]
        metas = [item["metadata"] for _, item in top_items]
        dists = [dist for dist, _ in top_items]

        return {
            "ids": [ids],
            "documents": [docs],
            "metadatas": [metas],
            "distances": [dists],
        }


def get_embedding_model():
    """Khởi tạo và cache mô hình SentenceTransformer khi cần dùng fallback."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        from sentence_transformers import SentenceTransformer
        _MODEL_INSTANCE = SentenceTransformer("BAAI/bge-m3")
    return _MODEL_INSTANCE


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo vector embedding bằng Google Gemini Embedding hoặc SentenceTransformer fallback."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
    if provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                model_name = os.getenv("EMBEDDING_MODEL") or "gemini-embedding-001"
                vectors = []
                batch_size = 16
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    res = client.models.embed_content(
                        model=model_name,
                        contents=batch,
                    )
                    for emb in res.embeddings:
                        vectors.append(list(emb.values))
                return vectors
            except Exception as e:
                pass

    # Fallback offline
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance (hoặc local fallback chuẩn contract)."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception:
        return LocalVectorCollection(CHROMA_DIR, COLLECTION_NAME)


def load_documents() -> list[dict]:
    """Đọc Markdown trong standardized/ và trả về danh sách Document theo contract."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
            
        rel_id = path.relative_to(STANDARDIZED_DIR).as_posix()
        title = path.stem.replace("-", " ").replace("_", " ").title()
        
        url = None
        for line in content.splitlines()[:10]:
            if line.startswith("**Source:**"):
                candidate = line.replace("**Source:**", "").strip()
                if candidate.startswith("http"):
                    url = candidate
                break

        documents.append({
            "id": rel_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def _split_text_recursive(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Thuật toán Recursive Character Splitting thuần Python hiệu năng cao."""
    separators = ["\n\n", "\n", ". ", " ", ""]
    chunks: list[str] = []

    def _split(s: str, seps: list[str]):
        if len(s) <= chunk_size:
            clean = s.strip()
            if clean:
                chunks.append(clean)
            return

        if not seps:
            step = max(1, chunk_size - chunk_overlap)
            for i in range(0, len(s), step):
                part = s[i:i + chunk_size].strip()
                if part:
                    chunks.append(part)
            return

        sep = seps[0]
        parts = s.split(sep) if sep else list(s)
        current = []
        current_len = 0

        for part in parts:
            if not part:
                continue
            part_len = len(part) + (len(sep) if current else 0)
            if current_len + part_len <= chunk_size:
                current.append(part)
                current_len += part_len
            else:
                if current:
                    merged = sep.join(current).strip()
                    if merged:
                        chunks.append(merged)
                    current = [part]
                    current_len = len(part)
                else:
                    _split(part, seps[1:])

        if current:
            merged = sep.join(current).strip()
            if merged:
                chunks.append(merged)

    _split(text, separators)
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành các chunks tuân thủ contract."""
    chunks = []
    for document in documents:
        doc_content = document["content"]
        split_texts = _split_text_recursive(doc_content, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        if not split_texts and doc_content:
            split_texts = [doc_content[:CHUNK_SIZE]]

        for index, text in enumerate(split_texts):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunk_item = {
                "id": f"{document['id']}::chunk-{index}",
                "content": clean_text,
                "metadata": {
                    "source": document["metadata"]["source"],
                    "title": document["metadata"]["title"],
                    "doc_type": document["metadata"]["doc_type"],
                    "url": document["metadata"]["url"],
                    "chunk_index": index,
                },
            }
            chunks.append(chunk_item)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Tạo vector embedding cho từng chunk."""
    if not chunks:
        return []
    texts = [c["content"] for c in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB / LocalVectorCollection."""
    if not chunks:
        return
    collection = get_collection()
    
    metadatas = []
    for chunk in chunks:
        m = dict(chunk["metadata"])
        if m.get("url") is None:
            m["url"] = ""
        metadatas.append(m)

    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["content"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        metadatas=metadatas,
    )


def run_pipeline() -> None:
    """Chạy toàn bộ pipeline load, chunk, embed và index."""
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Generated {len(chunks)} chunks")

    print(f"Embedding chunks with {EMBEDDING_MODEL}...")
    embedded_chunks = embed_chunks(chunks)

    print("Indexing to vectorstore...")
    index_to_vectorstore(embedded_chunks)
    print(f"Successfully indexed {len(embedded_chunks)} chunks to vectorstore!")


if __name__ == "__main__":
    run_pipeline()
