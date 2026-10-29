from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RAGEngine:
    """A small TF-IDF retrieval engine. It requires no external embedding model."""

    def __init__(self, top_k=4):
        self.top_k = top_k
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def add_document(self, document_metadata):
        self.chunks = list(document_metadata["chunks"])
        self.vectorizer = None
        self.matrix = None

        if self.chunks:
            texts = [item["text"] for item in self.chunks]
            self.vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=20000
            )
            self.matrix = self.vectorizer.fit_transform(texts)

    def clear(self):
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def retrieve(self, query):
        """Return the top-k chunks most similar to the query."""
        if not self.chunks or self.vectorizer is None or not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        ranked_indices = scores.argsort()[::-1][:self.top_k]

        results = []
        for index in ranked_indices:
            score = float(scores[index])
            if score <= 0:
                continue
            item = dict(self.chunks[index])
            item["score"] = score
            results.append(item)
        return results
