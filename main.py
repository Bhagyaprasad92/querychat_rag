import threading
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
            ui_callback=self.gui.update_status
        )

    def handle_user_input(self, user_text, compare=False):
        try:
            response = self.orchestrator.process_message(user_text, compare=compare)
            self.gui.add_message("Assistant", response)
        except Exception as exc:
            self.gui.add_message("Assistant", f"An error occurred: {exc}")
            self.gui.update_status("Error")

    def handle_clear_chat(self):
        self.orchestrator.clear_chat()
        self.gui.add_message("Assistant", "Chat history cleared. The uploaded document is still available.")

    def handle_upload_pdf(self):
        file_path = self.gui.choose_pdf()
        if not file_path:
            return

        def run_ingest():
            try:
                self.gui.update_status("Reading and chunking PDF...")
                filename = file_path.replace("\\", "/").split("/")[-1]
                self.gui.add_message(
                    "Assistant",
                    f"Processing '{filename}'. Extracting text and creating searchable chunks..."
                )
                metadata = ingest_pdf(file_path)
                self.orchestrator.add_document(metadata)
                self.gui.add_message(
                    "Assistant",
                    f"Successfully loaded '{metadata['filename']}' "
                    f"({metadata['num_pages']} pages, {metadata['num_chunks']} chunks). "
                    "You can now ask questions about this PDF."
                )
                self.gui.update_status("Ready")
            except Exception as exc:
                self.gui.add_message("Assistant", f"PDF ingestion failed: {exc}")
                self.gui.update_status("PDF error")

        threading.Thread(target=run_ingest, daemon=True).start()

    def run(self):
        self.gui.mainloop()


if __name__ == "__main__":
    UniDeskApp().run()
