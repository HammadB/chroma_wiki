import faiss
import numpy as np
from typing import Optional
from embedder import Embedder


class Index:

    def __init__(self, index_file: Optional[str], embedding_length=1536):
        if (index_file):
            self._faiss_index: faiss.IndexFlatIP = faiss.read_index(index_file)
        else:
            self._faiss_index: faiss.IndexFlatIP = faiss.IndexFlatIP(embedding_length)

        # TODO: factory / DI support
        self.embedder = Embedder()

    def get_closest_indices(self, query, k=4) -> list[int]:
        xq = self.embedder.get_embedding(query)[0]
        D, I = self._faiss_index.search(np.array([xq]), k)
        return list(I[0])

    def add_to_index(self, entries: list[str]) -> bool:
        embeddings = self.embedder.get_embedding(entries)
        if embeddings and len(embeddings) > 0:
            self._faiss_index.add(np.array(embeddings))
            return True
        return False

    def save_to_path(self, path: str):
        faiss.write_index(self._faiss_index, path)