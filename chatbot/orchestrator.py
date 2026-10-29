import requests
import config
from rag.engine import RAGEngine


class ChatOrchestrator:
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.rag_engine = RAGEngine(top_k=config.TOP_K)
        self.chat_history = []

    def update_status(self, status):
        if self.ui_callback:
            self.ui_callback(status)

    def add_document(self, metadata):
        self.rag_engine.add_document(metadata)

    def clear_chat(self):
        self.chat_history = []

    def clear_document(self):
        self.rag_engine.clear()

    def _ask_ollama(self, prompt):
        url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.2}
        }
        try:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Open a terminal and run "
                "'ollama serve' (if it is not already running), then check "
                f"that model '{config.OLLAMA_MODEL}' is installed."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("Ollama took too long to respond. Try again.") from exc
        except requests.exceptions.HTTPError as exc:
            detail = ""
            try:
                detail = response.text
            except Exception:
                pass
            raise RuntimeError(
                f"Ollama returned an error. Check model '{config.OLLAMA_MODEL}'. {detail}"
            ) from exc

    def process_message(self, question, compare=False):
        question = question.strip()
        if not question:
            return "Please type a question."

        self.update_status("Searching document..." if self.rag_engine.chunks else "Thinking...")
        retrieved = self.rag_engine.retrieve(question)

        if retrieved:
            context_parts = []
            for item in retrieved:
                context_parts.append(
                    f"[Source: {item['source']}, page {item['page']}, "
                    f"relevance {item['score']:.3f}]\n{item['text']}"
                )
            context = "\n\n".join(context_parts)[:config.MAX_CONTEXT_CHARS]
            rag_prompt = (
                "You are QueryChat, a helpful document question-answering assistant. "
                "Answer the question using the context below. If the answer is not "
                "supported by the context, clearly say that the document does not "
                "provide enough information. Do not invent facts. Mention source "
                "page numbers when useful.\n\n"
                f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
            )
        else:
            rag_prompt = (
                "You are a helpful assistant. Answer the user's question clearly. "
                "If you are unsure, say so.\n\n"
                f"QUESTION: {question}\nANSWER:"
            )

        rag_answer = self._ask_ollama(rag_prompt)

        if compare:
            baseline_prompt = (
                "Answer the following question using your general knowledge only. "
                "Do not assume access to any uploaded document. If uncertain, say so.\n\n"
                f"QUESTION: {question}\nANSWER:"
            )
            baseline_answer = self._ask_ollama(baseline_prompt)
            result = (
                "RAG ANSWER (retrieval + context)\n"
                f"{rag_answer}\n\n"
                "BASELINE ANSWER (without retrieval)\n"
                f"{baseline_answer}\n\n"
                "Evaluation tip: compare each answer with the uploaded PDF. "
                "Check correctness, missing facts, unsupported claims, and whether "
                "the RAG answer uses the document."
            )
        else:
            result = rag_answer

        self.chat_history.append({"question": question, "answer": result})
        self.update_status("Ready")
        return result
