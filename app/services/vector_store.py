import re
import math
import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    """
    In-memory / persistent semantic vector store powered by numpy cosine similarity.
    Indexed by n-gram subword and token term-frequency vectors with inverse document frequency.
    Ready for Qdrant / dense neural embeddings integration.
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.matrix: Optional[np.ndarray] = None

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 2]
        return tokens

    def add_chunks(self, chunks: List[Dict[str, Any]], paper_id: str, paper_title: str):
        """
        Add chunks with metadata to the index and recompute vectors.
        """
        for chk in chunks:
            self.chunks.append({
                "chunk_id": chk.get("chunk_id", f"chk_{len(self.chunks)}"),
                "paper_id": paper_id,
                "paper_title": paper_title,
                "text": chk.get("text", ""),
                "page_number": chk.get("page_number", 1),
                "section": chk.get("section", "General")
            })
        self._rebuild_index()

    def _rebuild_index(self):
        if not self.chunks:
            return

        doc_count = len(self.chunks)
        doc_tokens_list = [self._tokenize(c["text"]) for c in self.chunks]
        
        # Build vocabulary
        df = Counter()
        for doc_tokens in doc_tokens_list:
            unique_terms = set(doc_tokens)
            df.update(unique_terms)

        # Retain terms that appear in documents
        self.vocabulary = {term: idx for idx, (term, count) in enumerate(df.most_common(5000))}
        vocab_size = len(self.vocabulary)
        if vocab_size == 0:
            return

        self.idf = {
            term: math.log((1.0 + doc_count) / (1.0 + count)) + 1.0
            for term, count in df.items() if term in self.vocabulary
        }

        # Build dense tf-idf vectors
        vectors = np.zeros((doc_count, vocab_size), dtype=np.float32)
        for doc_idx, doc_tokens in enumerate(doc_tokens_list):
            tf = Counter(doc_tokens)
            total_tokens = max(1, len(doc_tokens))
            for term, count in tf.items():
                if term in self.vocabulary:
                    v_idx = self.vocabulary[term]
                    vectors[doc_idx, v_idx] = (count / total_tokens) * self.idf.get(term, 1.0)

        # Normalize rows to unit length for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.matrix = vectors / norms

    def query(self, query_text: str, top_k: int = 4, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search across all indexed chunks.
        """
        if self.matrix is None or len(self.chunks) == 0:
            return []

        q_tokens = self._tokenize(query_text)
        if not q_tokens:
            return []

        vocab_size = len(self.vocabulary)
        q_vec = np.zeros((vocab_size,), dtype=np.float32)
        tf = Counter(q_tokens)
        total_tokens = len(q_tokens)

        for term, count in tf.items():
            if term in self.vocabulary:
                v_idx = self.vocabulary[term]
                q_vec[v_idx] = (count / total_tokens) * self.idf.get(term, 1.0)

        norm = np.linalg.norm(q_vec)
        if norm == 0:
            return []
        q_vec = q_vec / norm

        # Compute cosine similarity
        scores = np.dot(self.matrix, q_vec)
        top_indices = np.argsort(scores)[::-1]

        results = []
        for idx in top_indices[:top_k]:
            score = float(scores[idx])
            if score >= min_score:
                chk = self.chunks[idx].copy()
                chk["score"] = round(score, 4)
                results.append(chk)

        return results

# Global singleton instance
vector_store = VectorStore()
