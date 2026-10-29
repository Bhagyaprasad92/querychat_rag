import tkinter as tk
from tkinter import filedialog, messagebox
import threading


class ChatWindow:
    def __init__(self, on_submit_callback, on_clear_callback, on_upload_callback):
        self.on_submit_callback = on_submit_callback
        self.on_clear_callback = on_clear_callback
        self.on_upload_callback = on_upload_callback

        self.root = tk.Tk()
        self.root.title("QueryChat - Basic RAG Chain")
        self.root.geometry("900x680")
        self.root.minsize(700, 520)
        self.root.configure(bg="#f3eee8")

        header = tk.Frame(self.root, bg="#33251e", padx=14, pady=12)
        header.pack(fill="x")
        tk.Label(
            header, text="QueryChat", font=("Segoe UI", 18, "bold"),
            bg="#33251e", fg="white"
        ).pack(side="left")
        tk.Label(
            header, text="PDF RAG Assistant", font=("Segoe UI", 10),
            bg="#33251e", fg="#e8d9ca"
        ).pack(side="left", padx=12, pady=(5, 0))

        controls = tk.Frame(self.root, bg="#f3eee8", padx=12, pady=8)
        controls.pack(fill="x")
        tk.Button(
            controls, text="Upload PDF", command=self.on_upload_callback,
            bg="#80624d", fg="white", relief="flat", padx=12, pady=6
        ).pack(side="left")
        tk.Button(
            controls, text="Clear Chat", command=self.on_clear_callback,
            bg="#ded1c5", fg="#33251e", relief="flat", padx=12, pady=6
        ).pack(side="left", padx=8)
        self.compare_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            controls, text="Compare RAG vs no retrieval",
            variable=self.compare_var, bg="#f3eee8", fg="#33251e",
            activebackground="#f3eee8"
        ).pack(side="left", padx=6)

        self.chat_area = tk.Text(
            self.root, wrap="word", state="disabled",
            font=("Segoe UI", 10), bg="white", fg="#33251e",
            padx=12, pady=12, relief="flat"
        )
        self.chat_area.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.chat_area.tag_configure("role", font=("Segoe UI", 10, "bold"), foreground="#79543e")
        self.chat_area.tag_configure("body", font=("Segoe UI", 10), spacing3=8)

        input_frame = tk.Frame(self.root, bg="#f3eee8", padx=12, pady=8)
        input_frame.pack(fill="x")
        self.entry = tk.Entry(
            input_frame, font=("Segoe UI", 11), relief="solid", bd=1
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", lambda event: self._submit())
        tk.Button(
            input_frame, text="Send", command=self._submit,
            bg="#4c392e", fg="white", relief="flat", padx=18, pady=8
        ).pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            self.root, textvariable=self.status_var, anchor="w",
            bg="#e6d9cd", fg="#33251e", padx=12, pady=5
        ).pack(fill="x", side="bottom")
        self.add_message(
            "Assistant",
            "Welcome to QueryChat! Upload a text-based PDF, wait for processing, "
            "then ask questions about it. You can also compare RAG with a baseline "
            "answer that does not use retrieved document context."
        )

    def mainloop(self):
        self.root.mainloop()

    def add_message(self, role, message):
        def write():
            self.chat_area.configure(state="normal")
            self.chat_area.insert("end", f"{role}\n", "role")
            self.chat_area.insert("end", f"{message}\n\n", "body")
            self.chat_area.see("end")
            self.chat_area.configure(state="disabled")
        self.root.after(0, write)

    def update_status(self, status):
        self.root.after(0, lambda: self.status_var.set(status))

    def _submit(self):
        question = self.entry.get().strip()
        if not question:
            return
        self.entry.delete(0, "end")
        self.add_message("You", question)
        self.status_var.set("Generating answer...")
        threading.Thread(
            target=self._run_question,
            args=(question, self.compare_var.get()),
            daemon=True
        ).start()

    def _run_question(self, question, compare):
        try:
            self.on_submit_callback(question, compare)
        except Exception as exc:
            self.add_message("Assistant", f"Error: {exc}")
            self.update_status("Error")

    def choose_pdf(self):
        return filedialog.askopenfilename(
            parent=self.root,
            title="Select PDF document",
            filetypes=[("PDF files", "*.pdf")]
        )

    def show_error(self, title, message):
        self.root.after(0, lambda: messagebox.showerror(title, message, parent=self.root))
