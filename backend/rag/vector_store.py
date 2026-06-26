"""
Lightweight vector store using numpy for cosine similarity and JSON for persistence.
No native extensions required — works on any Python environment.
"""

import json
import os
import numpy as np


class VectorStore:
    """
    A simple persistent vector store backed by a JSON file.
    Supports upsert and cosine-similarity search.
    """

    def __init__(self, db_path: str):
        """
        Args:
            db_path: Path to the JSON file that persists the store.
        """
        self.db_path = db_path
        self._data: list[dict] = []  # list of {"id", "document", "embedding", "metadata"}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = []

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def upsert(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
    ):
        """Insert or update records. Existing IDs are overwritten."""
        if metadatas is None:
            metadatas = [{} for _ in ids]

        existing_ids = {item["id"]: idx for idx, item in enumerate(self._data)}

        for doc_id, doc, emb, meta in zip(ids, documents, embeddings, metadatas):
            record = {"id": doc_id, "document": doc, "embedding": emb, "metadata": meta}
            if doc_id in existing_ids:
                self._data[existing_ids[doc_id]] = record
            else:
                self._data.append(record)

        self._save()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def count(self) -> int:
        return len(self._data)

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 3,
    ) -> list[dict]:
        """
        Return the top-n_results most similar documents (cosine similarity).

        Returns a list of dicts: {"id", "document", "metadata", "score"}
        """
        if not self._data:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []

        scores = []
        for item in self._data:
            v = np.array(item["embedding"], dtype=np.float32)
            v_norm = np.linalg.norm(v)
            if v_norm == 0:
                scores.append(0.0)
            else:
                scores.append(float(np.dot(q, v) / (q_norm * v_norm)))

        top_indices = np.argsort(scores)[::-1][:n_results]
        results = []
        for i in top_indices:
            results.append(
                {
                    "id": self._data[i]["id"],
                    "document": self._data[i]["document"],
                    "metadata": self._data[i]["metadata"],
                    "score": scores[i],
                }
            )
        return results
