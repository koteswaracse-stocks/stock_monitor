from __future__ import annotations

from typing import List

from app.config import settings


class RAGService:
    """RAG service using a FAISS vector index with keyword fallback.

    When an OpenAI API key is configured, it creates embeddings for each document and uses FAISS
    as the similarity backend. Without an API key, it gracefully falls back to keyword matching.
    """

    def __init__(self):
        self.documents = [
            {
                "title": "Market Momentum Guide",
                "content": "Momentum trades outperform when earnings quality is stable and volume confirms the move.",
            },
            {
                "title": "Sector Rotation Notes",
                "content": "Technology and semiconductors often lead during broad market upswings, while energy can act defensively in inflationary environments.",
            },
            {
                "title": "Risk Framework",
                "content": "A strong signal should be validated with volume support, relative strength, and valuation discipline.",
            },
            {
                "title": "AI Analyst Workflow",
                "content": "Combine technical momentum, sector leadership, and company-specific news to generate a practical trade opportunity summary.",
            },
        ]
        self.vector_index = None
        self.embedding_dim = 1536
        self._init_vector_store()

    def _init_vector_store(self) -> None:
        self.vector_index = None
        if not settings.openai_api_key:
            return

        try:
            import numpy as np
            import faiss
            from openai import OpenAI

            client = OpenAI(api_key=settings.openai_api_key)
            texts = [f"{doc['title']} {doc['content']}" for doc in self.documents]
            embeddings = client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )
            vectors = np.array([item.embedding for item in embeddings.data], dtype="float32")
            if vectors.size == 0:
                return
            index = faiss.IndexFlatL2(vectors.shape[1])
            index.add(vectors)
            self.vector_index = index
            self.embedding_dim = vectors.shape[1]
        except Exception:
            self.vector_index = None

    def search(self, query: str, k: int = 3) -> List[dict]:
        if not query or not query.strip():
            return []

        if self.vector_index is not None:
            try:
                return self._search_with_embeddings(query, k)
            except Exception:
                pass

        return self._search_with_keywords(query, k)

    def _search_with_embeddings(self, query: str, k: int = 3) -> List[dict]:
        try:
            import numpy as np
            from openai import OpenAI
        except Exception:
            return self._search_with_keywords(query, k)

        client = OpenAI(api_key=settings.openai_api_key)
        query_embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=[query],
        ).data[0].embedding

        query_vector = np.array([query_embedding], dtype="float32")
        distances, indices = self.vector_index.search(query_vector, min(k, len(self.documents)))

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            doc = self.documents[int(idx)]
            results.append({
                "title": doc["title"],
                "content": doc["content"],
                "score": round(max(0.0, 1.0 - float(distance) / 10.0), 2),
            })
        return results

    def _search_with_keywords(self, query: str, k: int = 3) -> List[dict]:
        query_lower = query.lower()
        results = []
        for doc in self.documents:
            score = 0.0
            for token in query_lower.split():
                if token in doc["title"].lower() or token in doc["content"].lower():
                    score += 1.0
            if score > 0:
                results.append({
                    "title": doc["title"],
                    "content": doc["content"],
                    "score": round(score / max(len(query_lower.split()), 1), 2),
                })
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:k]
