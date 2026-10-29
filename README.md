# QueryChat: Basic RAG Chain (Python + Ollama)

This project implements the requested RAG steps:

1. **Query:** the user enters a question in the desktop chat window.
2. **Retrieval:** TF-IDF similarity ranks PDF chunks and selects the top-k chunks.
3. **Context augmentation:** the selected chunks, source pages, and question are combined into a prompt.
4. **Generation:** the prompt is sent to a local Ollama language model.
5. **Answer:** the generated response is shown in the GUI.
6. **Evaluation:** enable “Compare RAG vs no retrieval” to see a RAG answer and a baseline answer side by side.

The project uses TF-IDF retrieval rather than a neural embedding model to keep installation simple. It is a valid basic retrieval pipeline, but it is not a production-grade semantic vector database.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- Ollama for Windows
- The Ollama model `llama3.2`
- A text-based PDF (scanned image-only PDFs need OCR first)

## Step 1: Install Ollama and download the model

Install Ollama from https://ollama.com/download

Open Command Prompt or the VS Code terminal and run:

```bash
ollama pull llama3.2
```

Test that the model works:

```bash
ollama run llama3.2
```

Type a simple question. To exit the model prompt, type `/bye`.

Ollama usually runs in the background on Windows. If the app cannot connect, try:

```bash
ollama serve
```

If it says the port is already in use, Ollama is probably already running; do not start a second server.

## Step 2: Extract the project

Extract `querychat_rag_project.zip` to a folder, for example:

`C:\\Users\\YourName\\Documents\\querychat_rag_project`

Open that folder in VS Code using **File → Open Folder**.

## Step 3: Create a virtual environment

In the VS Code terminal, make sure the terminal is inside the project folder, then run:

```bash
python -m venv .venv
```

Activate it in Windows Command Prompt:

```bat
.venv\\Scripts\\activate
```

For PowerShell:

```powershell
.\\.venv\\Scripts\\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or run the app with the interpreter at `.venv\\Scripts\\python.exe`.

## Step 4: Install Python packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Step 5: Run the application

From the project root (the folder containing `main.py`), run:

```bash
python main.py
```

Do not run `main.py` from `C:\\Windows\\System32`. In VS Code, open the project folder first and check that the terminal path ends with `querychat_rag_project`.

## Step 6: Test it

1. Click **Upload PDF** and select a text-based PDF.
2. Wait for the message confirming the number of pages and chunks.
3. Ask a question whose answer is in the PDF.
4. Ask a question that the PDF does not answer. The RAG prompt tells the model to say when the context is insufficient.
5. Tick **Compare RAG vs no retrieval** and ask a question to compare both answers.

Example questions:
- “Summarize the main points in this document.”
- “What are the important dates mentioned?”
- “List the key advantages described in the PDF.”
- “Does the document mention a budget? If not, say that it does not.”

## How to explain the evaluation

Use 5–10 questions and manually compare each response against the PDF. Record whether each answer is correct, partly correct, incorrect, or unsupported. RAG often improves grounding when the answer is present in the retrieved chunks, but it does not guarantee correctness. Retrieval can miss relevant chunks, and the language model can still make mistakes.

## Common errors

- **Cannot connect to Ollama:** make sure Ollama is installed and running. Check `http://localhost:11434` in a browser or run `ollama list`.
- **Model not found:** run `ollama pull llama3.2` and confirm the exact model name with `ollama list`.
- **No readable text found:** the PDF may be scanned. Use OCR to make it searchable, then upload it again.
- **ModuleNotFoundError:** activate the virtual environment and run `pip install -r requirements.txt` from the project root.
- **App opens but answer is slow:** local models can take time, especially on computers with limited RAM.

## Project structure

```text
querychat_rag_project/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── chatbot/
│   ├── __init__.py
│   └── orchestrator.py
├── gui/
│   ├── __init__.py
│   └── chat_window.py
└── rag/
    ├── __init__.py
    ├── ingest.py
    └── engine.py
```

## Important notes

- Uploaded PDF chunks remain in memory only while the app is open. Restarting the app clears the document.
- This version processes one PDF at a time; uploading another PDF replaces the searchable chunks.
- The “no retrieval” baseline uses general model knowledge, not the PDF.
- Do not upload private or sensitive documents unless you are comfortable processing them locally with the installed software.
