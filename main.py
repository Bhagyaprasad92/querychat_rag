import threading
import time
import tkinter as tk
from tkinter import filedialog

import config
from gui.chat_window import ChatWindow
from chatbot.orchestrator import ChatOrchestrator
from rag.ingest import ingest_pdf


class UniDeskApp:
    def __init__(self):
        self.gui = ChatWindow(
            on_submit_callback=self.handle_user_input,
            on_clear_callback=self.handle_clear_chat,
            on_upload_callback=self.handle_upload_pdf
        )
        self.orchestrator = ChatOrchestrator(
            ui_callback=lambda status: self.gui.update_status(status)
        )

    def handle_user_input(self, user_text, compare=False):
        start_time = time.time()
        try:
            badge_info = ""
            rag_started = False
            baseline_started = False

            for event in self.orchestrator.stream_message(user_text, compare=compare):
                event_type = event.get("type")

                if event_type == "phase":
                    phase = event.get("phase")
                    msg = event.get("message", "")
                    self.gui.update_thinking_phase(msg)
                    self.gui.update_status(msg, is_active=True)

                elif event_type == "retrieved":
                    count = event.get("count", 0)
                    top_score = event.get("top_score", 0.0)
                    if count > 0:
                        badge_info = f"📚 {count} Chunks Context • Relevance: {top_score:.3f}"
                    else:
                        badge_info = "⚡ General Knowledge"

                elif event_type == "rag_token":
                    if not rag_started:
                        rag_started = True
                        role_name = "QueryChat AI (RAG Grounded)" if compare else "QueryChat AI"
                        self.gui.root.after(
                            0,
                            lambda r=role_name, b=badge_info: self.gui.start_streaming_answer(role=r, badge_info=b)
                        )
                    token = event.get("token", "")
                    self.gui.root.after(0, lambda t=token: self.gui.stream_token(t))

                elif event_type == "baseline_token":
                    if not baseline_started:
                        baseline_started = True
                        self.gui.root.after(0, self.gui.finish_streaming_answer)
                        self.gui.root.after(0, self.gui.start_baseline_answer)
                    token = event.get("token", "")
                    self.gui.root.after(0, lambda t=token: self.gui.stream_baseline_token(t))

                elif event_type == "done":
                    if baseline_started:
                        self.gui.root.after(0, self.gui.finish_baseline_answer)
                    elif rag_started:
                        self.gui.root.after(0, self.gui.finish_streaming_answer)
                    else:
                        self.gui.root.after(0, self.gui.stop_thinking_animation)

                elif event_type == "error":
                    self.gui.root.after(0, self.gui.stop_thinking_animation)
                    err_msg = event.get("message", "An unknown error occurred.")
                    self.gui.root.after(0, lambda m=err_msg: self.gui._append_system_card("Notice", m))

            elapsed = time.time() - start_time
            self.gui.update_timing(f"Latency: {elapsed:.2f}s")
            self.gui.update_status("Ready", is_active=False)

        except Exception as exc:
            self.gui.root.after(0, self.gui.stop_thinking_animation)
            self.gui.root.after(0, lambda e=str(exc): self.gui._append_system_card("Inference Error", e))
            self.gui.update_status("Error", is_active=False)

    def handle_clear_chat(self):
        self.orchestrator.clear_chat()
        self.gui.clear_chat_view()
        self.gui.update_status("Chat history reset", is_active=False)

    def handle_upload_pdf(self):
        file_path = self.gui.choose_pdf()
        if not file_path:
            return

        def run_ingest():
            try:
                self.gui.update_status("Reading & indexing PDF...", is_active=True)
                filename = file_path.replace("\\", "/").split("/")[-1]
                self.gui.root.after(
                    0,
                    lambda fn=filename: self.gui._append_system_card(
                        "Document Ingestion",
                        f"Extracting text & computing TF-IDF vectors for '{fn}'..."
                    )
                )

                metadata = ingest_pdf(file_path)
                self.orchestrator.add_document(metadata)

                self.gui.root.after(
                    0,
                    lambda m=metadata: self.gui.set_document_info(
                        m["filename"], m["num_pages"], m["num_chunks"]
                    )
                )
                self.gui.root.after(
                    0,
                    lambda m=metadata: self.gui._append_system_card(
                        "Document Ready",
                        f"Indexed '{m['filename']}' ({m['num_pages']} pages, {m['num_chunks']} searchable chunks).\n"
                        "You can now ask questions or click a quick prompt chip above!"
                    )
                )
                self.gui.update_status("Ready", is_active=False)
            except Exception as exc:
                self.gui.root.after(
                    0,
                    lambda e=str(exc): self.gui._append_system_card("Ingestion Error", e)
                )
                self.gui.update_status("PDF error", is_active=False)

        threading.Thread(target=run_ingest, daemon=True).start()

    def run(self):
        self.gui.mainloop()


if __name__ == "__main__":
    UniDeskApp().run()
