from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import config


class RAGEngine:
    """A robust TF-IDF retrieval engine with smart fallback for conversational/summary queries."""

    def __init__(self, top_k=None):
        self.top_k = top_k or config.TOP_K
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def add_document(self, document_metadata):
        self.chunks = list(document_metadata.get("chunks", []))
        self.vectorizer = None
        self.matrix = None

        if self.chunks:
            texts = [item["text"] for item in self.chunks]
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=25000,
                sublinear_tf=True
            )
            try:
                self.matrix = self.vectorizer.fit_transform(texts)
            except Exception:
                self.matrix = None

    def clear(self):
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def retrieve(self, query):
        """Return the top-k chunks most similar to the query, with smart fallback."""
        if not self.chunks:
            return []

        # If document is small (<= top_k chunks), return all chunks so context is 100% complete
        if len(self.chunks) <= self.top_k:
            results = []
            for i, chunk in enumerate(self.chunks):
                item = dict(chunk)
                item["score"] = 1.0  # Full context available
                results.append(item)
            return results

        if self.vectorizer is None or self.matrix is None or not query.strip():
            # Return initial overview chunks
            return [dict(c, score=0.5) for c in self.chunks[:self.top_k]]

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        ranked_indices = scores.argsort()[::-1]

        results = []
        for index in ranked_indices:
            score = float(scores[index])
            if score > 0:
                item = dict(self.chunks[index])
                item["score"] = score
                results.append(item)
                if len(results) >= self.top_k:
                    break

        # Fallback for queries with 0 direct lexical matches (e.g. "summarize document", "overview")
        if not results:
            for c in self.chunks[:self.top_k]:
                item = dict(c)
                item["score"] = 0.5
                results.append(item)

        return results
