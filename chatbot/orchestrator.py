import json
import time
import requests
import config
from rag.engine import RAGEngine


class ChatOrchestrator:
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        self.rag_engine = RAGEngine(top_k=config.TOP_K)
        self.chat_history = []
        self.current_document = None

    def update_status(self, status):
        if self.ui_callback:
            self.ui_callback(status)

    def add_document(self, metadata):
        self.current_document = metadata
        self.rag_engine.add_document(metadata)

    def clear_chat(self):
        self.chat_history = []

    def clear_document(self):
        self.current_document = None
        self.rag_engine.clear()

    def _ask_ollama(self, prompt):
        url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.3}
        }
        try:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "").strip()
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running and "
                f"model '{config.OLLAMA_MODEL}' is installed."
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
                f"Ollama returned an error with model '{config.OLLAMA_MODEL}': {detail}"
            ) from exc

    def _ask_ollama_stream(self, prompt):
        url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
        payload = {
            "model": config.OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
            "options": {"temperature": 0.3}
        }
        try:
            response = requests.post(url, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Ollama streaming error: {exc}") from exc

    def build_rag_prompt(self, question, retrieved):
        # Format conversation history
        history_str = ""
        if self.chat_history:
            recent_turns = self.chat_history[-3:]
            lines = []
            for turn in recent_turns:
                lines.append(f"User: {turn['question']}")
                # Short snippet of answer
                ans_snippet = turn.get('rag_answer') or turn.get('answer', '')
                lines.append(f"Assistant: {ans_snippet[:250]}...")
            history_str = "PREVIOUS CONVERSATION HISTORY:\n" + "\n".join(lines) + "\n\n"

        if retrieved:
            context_parts = []
            for item in retrieved:
                score_str = f"relevance {item['score']:.2f}" if 'score' in item else ""
                context_parts.append(
                    f"[Source: {item.get('source', 'Document')}, page {item.get('page', 1)} {score_str}]\n{item['text']}"
                )
            context = "\n\n".join(context_parts)[:config.MAX_CONTEXT_CHARS]

            return (
                "You are QueryChat, an intelligent and helpful document question-answering assistant.\n\n"
                f"{history_str}"
                f"DOCUMENT CONTEXT:\n{context}\n\n"
                "INSTRUCTIONS:\n"
                "1. Answer the user's question thoroughly, using the document context above.\n"
                "2. When stating facts directly from the document (dates, numbers, features, quotes), cite the source page.\n"
                "3. If the user asks for summaries, overviews, explanations, or analysis, synthesize the information clearly.\n"
                "4. If the user asks for educated guesses, technical estimates, recommendations, or inferences (e.g. potential tech stacks, standard architectures, next steps):\n"
                "   - First state clearly what is explicitly documented.\n"
                "   - Then provide a helpful, intelligent engineering deduction or estimate based on industry standards, clearly noting that it is an educated estimate.\n"
                "5. Only if the document is completely unrelated to the topic and no connection can be made, mention what the document actually covers.\n\n"
                f"QUESTION: {question}\n\nANSWER:"
            )

        return (
            "You are QueryChat, a helpful AI assistant.\n\n"
            f"{history_str}"
            f"QUESTION: {question}\n\nANSWER:"
        )

    def stream_message(self, question, compare=False):
        """Generator that yields progress events, retrieval info, and streaming tokens."""
        question = question.strip()
        if not question:
            yield {"type": "error", "message": "Please enter a question."}
            return

        has_docs = bool(self.rag_engine.chunks)
        yield {
            "type": "phase",
            "phase": "searching",
            "message": "Searching document context..." if has_docs else "Processing query..."
        }

        retrieved = self.rag_engine.retrieve(question) if has_docs else []
        top_score = retrieved[0].get("score", 0.0) if retrieved else 0.0

        yield {
            "type": "retrieved",
            "retrieved": retrieved,
            "count": len(retrieved),
            "top_score": top_score
        }

        yield {
            "type": "phase",
            "phase": "crafting",
            "message": "Synthesizing answer..."
        }

        rag_prompt = self.build_rag_prompt(question, retrieved)
        rag_answer_tokens = []
        for token in self._ask_ollama_stream(rag_prompt):
            rag_answer_tokens.append(token)
            yield {"type": "rag_token", "token": token}

        rag_full_answer = "".join(rag_answer_tokens).strip()

        baseline_full_answer = ""
        if compare:
            yield {
                "type": "phase",
                "phase": "baseline",
                "message": "Generating baseline answer (without document retrieval)..."
            }
            baseline_prompt = (
                "Answer the following question using your general knowledge only. "
                "Do not assume access to any uploaded document. If uncertain, say so.\n\n"
                f"QUESTION: {question}\nANSWER:"
            )
            baseline_tokens = []
            for token in self._ask_ollama_stream(baseline_prompt):
                baseline_tokens.append(token)
                yield {"type": "baseline_token", "token": token}
            baseline_full_answer = "".join(baseline_tokens).strip()

        self.chat_history.append({
            "question": question,
            "rag_answer": rag_full_answer,
            "baseline_answer": baseline_full_answer,
            "retrieved_count": len(retrieved)
        })

        yield {
            "type": "done",
            "rag_answer": rag_full_answer,
            "baseline_answer": baseline_full_answer,
            "retrieved": retrieved
        }

    def process_message(self, question, compare=False):
        """Non-streaming fallback method for CLI/test evaluations."""
        question = question.strip()
        if not question:
            return "Please type a question."

        self.update_status("Searching document..." if self.rag_engine.chunks else "Thinking...")
        retrieved = self.rag_engine.retrieve(question)
        rag_prompt = self.build_rag_prompt(question, retrieved)
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
                "Evaluation tip: compare each answer with the uploaded PDF."
            )
        else:
            result = rag_answer

        self.chat_history.append({"question": question, "answer": result, "rag_answer": result})
        self.update_status("Ready")
        return result
