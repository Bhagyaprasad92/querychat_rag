import datetime
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox


class ChatWindow:
    def __init__(self, on_submit_callback, on_clear_callback, on_upload_callback):
        self.on_submit_callback = on_submit_callback
        self.on_clear_callback = on_clear_callback
        self.on_upload_callback = on_upload_callback

        self.root = tk.Tk()
        self.root.title("QueryChat AI — Intelligent Document Assistant")
        self.root.geometry("1020x760")
        self.root.minsize(800, 600)
        self.root.configure(bg="#0b0f19")

        # Color Palette
        self.BG_DARK = "#0b0f19"
        self.PANEL_BG = "#111827"
        self.CARD_BG = "#1e293b"
        self.BORDER_COLOR = "#334155"
        self.ACCENT_PRIMARY = "#6366f1"
        self.ACCENT_HOVER = "#4f46e5"
        self.TEXT_PRIMARY = "#f8fafc"
        self.TEXT_MUTED = "#94a3b8"
        self.EMERALD = "#10b981"
        self.AMBER = "#f59e0b"
        self.CYAN = "#06b6d4"

        # State tracking
        self.is_thinking = False
        self.thinking_dot_idx = 0
        self.thinking_phase_text = "Processing question..."
        self.thinking_mark_start = None
        self.streaming_msg_id = None
        self.current_pdf_name = None

        # Build UI in exact packing order to guarantee the input bar is NEVER pushed off screen
        self._build_header()         # 1. Top
        self._build_suggested_bar()   # 2. Top (below header)
        self._build_status_bar()      # 3. Bottom (very bottom)
        self._build_input_bar()       # 4. Bottom (above status bar)
        self._build_chat_display()    # 5. Fills the entire remaining middle space

        self._show_welcome_message()
        self.root.after(100, lambda: self.entry.focus_set())

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.PANEL_BG, padx=18, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        header.pack(fill="x", side="top")

        brand_frame = tk.Frame(header, bg=self.PANEL_BG)
        brand_frame.pack(side="left")

        logo_lbl = tk.Label(
            brand_frame, text="✨ QueryChat", font=("Segoe UI", 16, "bold"),
            bg=self.PANEL_BG, fg="#ffffff"
        )
        logo_lbl.pack(side="left")

        badge = tk.Label(
            brand_frame, text="RAG v2.0", font=("Segoe UI", 8, "bold"),
            bg="#312e81", fg="#c7d2fe", padx=6, pady=2
        )
        badge.pack(side="left", padx=8)

        # Active Document Chip
        self.doc_chip_frame = tk.Frame(header, bg="#1e293b", padx=10, pady=5)
        self.doc_chip_frame.pack(side="left", padx=15)

        self.doc_chip_dot = tk.Label(
            self.doc_chip_frame, text="●", font=("Segoe UI", 10),
            bg="#1e293b", fg="#64748b"
        )
        self.doc_chip_dot.pack(side="left")

        self.doc_chip_label = tk.Label(
            self.doc_chip_frame, text="No PDF Loaded (Click 'Upload PDF')",
            font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#94a3b8"
        )
        self.doc_chip_label.pack(side="left", padx=(6, 0))

        # Actions on right
        actions_frame = tk.Frame(header, bg=self.PANEL_BG)
        actions_frame.pack(side="right")

        self.compare_var = tk.BooleanVar(value=False)
        self.compare_check = tk.Checkbutton(
            actions_frame, text="⚖️ Compare RAG vs Baseline",
            variable=self.compare_var, font=("Segoe UI", 9),
            bg=self.PANEL_BG, fg="#cbd5e1", selectcolor="#1e293b",
            activebackground=self.PANEL_BG, activeforeground="#ffffff"
        )
        self.compare_check.pack(side="left", padx=10)

        self.upload_btn = tk.Button(
            actions_frame, text="📄 Upload PDF",
            command=self.on_upload_callback,
            font=("Segoe UI", 9, "bold"), bg=self.ACCENT_PRIMARY, fg="white",
            activebackground=self.ACCENT_HOVER, activeforeground="white",
            relief="flat", padx=14, pady=6, cursor="hand2"
        )
        self.upload_btn.pack(side="left", padx=4)

        self.clear_btn = tk.Button(
            actions_frame, text="🗑️ Clear",
            command=self.on_clear_callback,
            font=("Segoe UI", 9), bg="#1e293b", fg="#cbd5e1",
            activebackground="#334155", activeforeground="white",
            relief="flat", padx=12, pady=6, cursor="hand2"
        )
        self.clear_btn.pack(side="left", padx=4)

    def _build_suggested_bar(self):
        self.suggested_frame = tk.Frame(self.root, bg=self.BG_DARK, padx=18, pady=6)
        self.suggested_frame.pack(fill="x", side="top")

        lbl = tk.Label(
            self.suggested_frame, text="Quick Prompts:",
            font=("Segoe UI", 8, "bold"), bg=self.BG_DARK, fg=self.TEXT_MUTED
        )
        lbl.pack(side="left", padx=(0, 8))

        prompts = [
            ("💡 Summarize Document", "Summarize the key objectives, milestones, and main takeaways from this document."),
            ("📅 Important Dates", "What are all the key milestones, deadlines, and dates mentioned in the PDF?"),
            ("💰 Budget Breakdown", "What is the total approved budget and how is each portion allocated?"),
            ("🚀 Core Advantages", "List the key technical advantages and unique features described in the document.")
        ]

        for title, query in prompts:
            chip = tk.Button(
                self.suggested_frame, text=title,
                command=lambda q=query: self._on_chip_click(q),
                font=("Segoe UI", 8), bg="#1e293b", fg="#cbd5e1",
                activebackground=self.ACCENT_PRIMARY, activeforeground="white",
                relief="flat", padx=8, pady=3, cursor="hand2", bd=0
            )
            chip.pack(side="left", padx=4)

    def _on_chip_click(self, query):
        self.entry.delete(0, "end")
        self.entry.insert(0, query)
        self._submit()

    def _build_status_bar(self):
        # Packed side="bottom" so it anchors to the lowest edge
        status_frame = tk.Frame(self.root, bg="#070a11", padx=16, pady=4, highlightbackground="#1e293b", highlightthickness=1)
        status_frame.pack(fill="x", side="bottom")

        self.status_lbl = tk.Label(
            status_frame, text="🟢 Ready", font=("Segoe UI", 8, "bold"),
            bg="#070a11", fg="#10b981"
        )
        self.status_lbl.pack(side="left")

        self.timing_lbl = tk.Label(
            status_frame, text="", font=("Segoe UI", 8),
            bg="#070a11", fg="#94a3b8"
        )
        self.timing_lbl.pack(side="left", padx=14)

        info_lbl = tk.Label(
            status_frame, text="Engine: TF-IDF RAG  |  Model: llama3.2 (Local)",
            font=("Segoe UI", 8), bg="#070a11", fg="#64748b"
        )
        info_lbl.pack(side="right")

    def _build_input_bar(self):
        # Packed side="bottom" immediately above status bar
        dock = tk.Frame(self.root, bg=self.PANEL_BG, padx=16, pady=10, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        dock.pack(fill="x", side="bottom")

        input_container = tk.Frame(dock, bg="#1e293b", padx=8, pady=6, highlightbackground="#4f46e5", highlightthickness=1)
        input_container.pack(fill="x", expand=True)

        self.entry = tk.Entry(
            input_container, font=("Segoe UI", 11), bg="#1e293b", fg="#ffffff",
            insertbackground="#ffffff", relief="flat", bd=0
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=6, ipady=4)
        self.entry.bind("<Return>", lambda event: self._submit())

        self.send_btn = tk.Button(
            input_container, text="➤ Send", command=self._submit,
            font=("Segoe UI", 10, "bold"), bg=self.ACCENT_PRIMARY, fg="white",
            activebackground=self.ACCENT_HOVER, activeforeground="white",
            relief="flat", padx=18, pady=6, cursor="hand2"
        )
        self.send_btn.pack(side="right", padx=(6, 0))

    def _build_chat_display(self):
        # Packed last so it expands into all remaining vertical space between top bars and bottom input
        container = tk.Frame(self.root, bg=self.BG_DARK, padx=16, pady=6)
        container.pack(fill="both", expand=True, side="top")

        scrollbar = tk.Scrollbar(container, bg=self.PANEL_BG, troughcolor=self.BG_DARK)
        scrollbar.pack(side="right", fill="y")

        self.chat_area = tk.Text(
            container, wrap="word", state="disabled",
            font=("Segoe UI", 10), bg=self.BG_DARK, fg=self.TEXT_PRIMARY,
            padx=14, pady=12, relief="flat", yscrollcommand=scrollbar.set,
            selectbackground=self.ACCENT_PRIMARY, selectforeground="white",
            spacing1=3, spacing2=2, spacing3=8
        )
        self.chat_area.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.chat_area.yview)

        # Style Tags
        self.chat_area.tag_configure("user_header", font=("Segoe UI", 9, "bold"), foreground="#a5b4fc", spacing3=2)
        self.chat_area.tag_configure("user_bubble", font=("Segoe UI", 10), foreground="#ffffff", background="#312e81", lmargin1=16, lmargin2=16, rmargin=80, spacing1=4, spacing3=6)

        self.chat_area.tag_configure("assistant_header", font=("Segoe UI", 9, "bold"), foreground="#38bdf8", spacing3=2)
        self.chat_area.tag_configure("assistant_bubble", font=("Segoe UI", 10), foreground="#f1f5f9", background="#1e293b", lmargin1=16, lmargin2=16, rmargin=20, spacing1=4, spacing3=6)

        self.chat_area.tag_configure("baseline_header", font=("Segoe UI", 9, "bold"), foreground="#fbbf24", spacing3=2)
        self.chat_area.tag_configure("baseline_bubble", font=("Segoe UI", 10), foreground="#fef3c7", background="#261b2e", lmargin1=16, lmargin2=16, rmargin=20, spacing1=4, spacing3=6)

        self.chat_area.tag_configure("thinking_box", font=("Segoe UI", 9, "italic"), foreground="#38bdf8", background="#132038", lmargin1=16, lmargin2=16, spacing1=4, spacing3=6)
        self.chat_area.tag_configure("system_card", font=("Segoe UI", 9), foreground="#cbd5e1", background="#111827", lmargin1=16, lmargin2=16, spacing1=4, spacing3=6)

    def _show_welcome_message(self):
        welcome_text = (
            "👋 Welcome to QueryChat RAG Assistant!\n\n"
            "• Click 'Upload PDF' in the top bar to select any document.\n"
            "• Ask any question below or click one of the 'Quick Prompts' above.\n"
            "• You can also ask for summaries, implications, or technical recommendations based on the document!\n"
            "• Toggle 'Compare RAG vs Baseline' to see side-by-side responses."
        )
        self._append_system_card("System Ready", welcome_text)

    def set_document_info(self, filename, pages, chunks):
        self.current_pdf_name = filename
        self.doc_chip_dot.config(fg=self.EMERALD)
        self.doc_chip_label.config(
            text=f"🟢 {filename}  •  {pages} page(s)  •  {chunks} chunks",
            fg=self.EMERALD
        )

    def _append_system_card(self, title, text):
        self.chat_area.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert("end", f"⚙️  {title} • {now}\n", "assistant_header")
        self.chat_area.insert("end", f" {text} \n\n", "system_card")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def add_user_message(self, text):
        self.chat_area.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert("end", f"👤 You • {now}\n", "user_header")
        self.chat_area.insert("end", f" {text} \n\n", "user_bubble")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def start_thinking_animation(self, initial_phase="Processing question..."):
        self.is_thinking = True
        self.thinking_dot_idx = 0
        self.thinking_phase_text = initial_phase

        self.chat_area.configure(state="normal")
        self.thinking_mark_start = self.chat_area.index("end-1c")
        self.chat_area.insert("end", f" ✨ QueryChat is thinking... {initial_phase} \n\n", "thinking_box")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

        self._tick_thinking()

    def update_thinking_phase(self, phase_text):
        self.thinking_phase_text = phase_text

    def _tick_thinking(self):
        if not self.is_thinking or not self.thinking_mark_start:
            return

        dots = ["● ○ ○", "○ ● ○", "○ ○ ●", "● ● ●"][self.thinking_dot_idx % 4]
        self.thinking_dot_idx += 1

        self.chat_area.configure(state="normal")
        end_idx = self.chat_area.index("end-1c")
        self.chat_area.delete(self.thinking_mark_start, end_idx)
        display_text = f" ✨ QueryChat AI  •  {self.thinking_phase_text}  {dots}\n\n"
        self.chat_area.insert(self.thinking_mark_start, display_text, "thinking_box")
        self.chat_area.configure(state="disabled")

        self.root.after(220, self._tick_thinking)

    def stop_thinking_animation(self):
        if self.is_thinking and self.thinking_mark_start:
            self.is_thinking = False
            self.chat_area.configure(state="normal")
            end_idx = self.chat_area.index("end-1c")
            self.chat_area.delete(self.thinking_mark_start, end_idx)
            self.chat_area.configure(state="disabled")
            self.thinking_mark_start = None

    def start_streaming_answer(self, role="QueryChat AI", badge_info=""):
        self.stop_thinking_animation()

        self.chat_area.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        header_text = f"✨ {role} • {now}"
        if badge_info:
            header_text += f"  [{badge_info}]"
        header_text += "\n"

        self.chat_area.insert("end", header_text, "assistant_header")
        self.streaming_msg_id = self.chat_area.index("end-1c")
        self.chat_area.insert("end", " ", "assistant_bubble")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def stream_token(self, token):
        if not self.streaming_msg_id:
            return
        self.chat_area.configure(state="normal")
        self.chat_area.insert(f"{self.chat_area.index('end-1c')} - 1c", token, "assistant_bubble")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def finish_streaming_answer(self):
        if self.streaming_msg_id:
            self.chat_area.configure(state="normal")
            self.chat_area.insert("end", "\n\n", "assistant_bubble")
            self.chat_area.see("end")
            self.chat_area.configure(state="disabled")
            self.streaming_msg_id = None

    def start_baseline_answer(self):
        self.chat_area.configure(state="normal")
        now = datetime.datetime.now().strftime("%H:%M")
        self.chat_area.insert(
            "end",
            f"⚖️ Baseline Response (General Knowledge / Without Retrieval) • {now}\n",
            "baseline_header"
        )
        self.streaming_msg_id = self.chat_area.index("end-1c")
        self.chat_area.insert("end", " ", "baseline_bubble")
        self.chat_area.see("end")
        self.chat_area.configure(state="disabled")

    def stream_baseline_token(self, token):
        self.stream_token(token)

    def finish_baseline_answer(self):
        self.finish_streaming_answer()

    def update_status(self, status, is_active=False):
        color = self.CYAN if is_active else self.EMERALD
        icon = "⚡" if is_active else "🟢"
        self.root.after(0, lambda: self.status_lbl.config(text=f"{icon} {status}", fg=color))

    def update_timing(self, text):
        self.root.after(0, lambda: self.timing_lbl.config(text=text))

    def _submit(self):
        question = self.entry.get().strip()
        if not question or self.is_thinking:
            return

        self.entry.delete(0, "end")
        self.add_user_message(question)
        self.update_status("Searching document...", is_active=True)
        self.start_thinking_animation("Searching document index...")

        threading.Thread(
            target=self._run_submit,
            args=(question, self.compare_var.get()),
            daemon=True
        ).start()

    def _run_submit(self, question, compare):
        try:
            self.on_submit_callback(question, compare)
        except Exception as exc:
            self.root.after(0, self.stop_thinking_animation)
            self.root.after(0, lambda: self._append_system_card("Error", str(exc)))
            self.update_status("Error", is_active=False)

    def choose_pdf(self):
        return filedialog.askopenfilename(
            parent=self.root,
            title="Select PDF document for RAG indexing",
            filetypes=[("PDF files", "*.pdf")]
        )

    def clear_chat_view(self):
        self.chat_area.configure(state="normal")
        self.chat_area.delete("1.0", "end")
        self.chat_area.configure(state="disabled")
        self._show_welcome_message()

    def mainloop(self):
        self.root.mainloop()
