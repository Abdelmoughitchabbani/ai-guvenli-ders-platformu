import hashlib
import re
import unicodedata
from pathlib import Path

import chromadb

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_client = None


def _collection():
    global _client
    if _client is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(DATA_DIR / "chroma"))
    return _client.get_or_create_collection("course_materials", metadata={"hnsw:space": "cosine"})


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c)).lower().replace("ı", "i")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "ders"


def _chunk_text(text: str, size: int = 800, overlap: int = 150):
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            cut = text.rfind(" ", start + size // 2, end)
            if cut != -1:
                end = cut
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def save_document_to_vector_db(course_name: str, file_name: str, text: str) -> int:
    col = _collection()
    slug = _slug(course_name)

    # Aynı dosya yeniden yüklenirse eski parçaları sil
    col.delete(where={"$and": [{"course": slug}, {"source": file_name}]})

    chunks = _chunk_text(text)
    if not chunks:
        return 0

    file_hash = hashlib.sha1(file_name.encode("utf-8")).hexdigest()[:8]
    for i in range(0, len(chunks), 100):
        batch = chunks[i:i + 100]
        col.add(
            ids=[f"{slug}-{file_hash}-{i + j}" for j in range(len(batch))],
            documents=batch,
            metadatas=[
                {"course": slug, "course_name": course_name, "source": file_name, "chunk": i + j}
                for j in range(len(batch))
            ],
        )
    return len(chunks)


def query_relevant_context(course_name: str, topic: str, n_results: int = 4, max_chars: int = 6000) -> str:
    col = _collection()
    slug = _slug(course_name)
    try:
        count = len(col.get(where={"course": slug}, include=[])["ids"])
        if count == 0:
            return ""
        res = col.query(query_texts=[topic], n_results=min(n_results, count), where={"course": slug})
    except Exception:
        return ""

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    parts, total = [], 0
    for doc, meta in zip(docs, metas):
        piece = f"[Kaynak: {meta.get('source', '?')}]\n{doc}"
        if total + len(piece) > max_chars:
            break
        parts.append(piece)
        total += len(piece)
    return "\n---\n".join(parts)


def list_courses():
    try:
        metas = _collection().get(include=["metadatas"])["metadatas"] or []
    except Exception:
        return []
    return sorted({m.get("course_name") for m in metas if m.get("course_name")})