import time
import os
import sys

from rag.ingest import ingest_pdf
from chatbot.orchestrator import ChatOrchestrator

def main():
    pdf_path = os.path.abspath("sample_document.pdf")
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} does not exist.")
        sys.exit(1)

    print("=" * 80)
    print("QUERYCHAT RAG SYSTEM - COMPLETE END-TO-END EXECUTION & EVALUATION")
    print("=" * 80)
    print(f"\n[1] Ingesting PDF Document: {pdf_path}")
    start_time = time.time()
    metadata = ingest_pdf(pdf_path)
    ingest_time = time.time() - start_time

    print(f"  -> File: {metadata['filename']}")
    print(f"  -> Pages: {metadata['num_pages']}")
    print(f"  -> Chunks generated: {metadata['num_chunks']}")
    print(f"  -> Ingestion completed in: {ingest_time:.2f}s")

    print("\n--- Document Chunks Sample ---")
    for i, chunk in enumerate(metadata['chunks'][:3], 1):
        snippet = chunk['text'].replace('\n', ' ')[:120]
        print(f"  Chunk {i} (Page {chunk['page']}, #{chunk['chunk']}): \"{snippet}...\"")

    print("\n[2] Initializing Chat Orchestrator and TF-IDF Retrieval Engine...")
    orchestrator = ChatOrchestrator()
    orchestrator.add_document(metadata)
    print("  -> TF-IDF vector matrix fitted and document indexed.")

    test_queries = [
        {
            "query": "What are the key milestones and important dates mentioned?",
            "compare": False,
            "description": "Factual extraction of specific dates from the document"
        },
        {
            "query": "List the core technical advantages of Project Nova.",
            "compare": False,
            "description": "Synthesis of document features and benefits"
        },
        {
            "query": "What is the approved budget and how is it allocated?",
            "compare": False,
            "description": "Financial figures extraction"
        },
        {
            "query": "Does the document mention any quantum computing hardware? If not, clearly state that it does not.",
            "compare": False,
            "description": "Negative constraint check (asking about unmentioned topic)"
        },
        {
            "query": "Summarize what Project Nova is, its primary goal, and its advantages.",
            "compare": True,
            "description": "Comparison Mode: RAG vs Baseline (no retrieval)"
        }
    ]

    print("\n[3] Executing Test Queries Against Ollama Model...")
    for idx, t in enumerate(test_queries, 1):
        q = t["query"]
        comp = t["compare"]
        desc = t["description"]

        print("\n" + "=" * 80)
        print(f"TEST QUERY #{idx}: \"{q}\"")
        print(f"Objective: {desc}")
        print(f"Compare Mode: {'ENABLED (RAG vs Baseline)' if comp else 'DISABLED (RAG only)'}")
        print("-" * 80)

        # Show retrieved chunks first
        retrieved = orchestrator.rag_engine.retrieve(q)
        print(f"Retrieved Top Chunks ({len(retrieved)}):")
        for r_idx, r in enumerate(retrieved, 1):
            text_preview = r['text'].replace('\n', ' ')[:100]
            print(f"  [{r_idx}] Page {r['page']} | Score: {r['score']:.4f} | \"{text_preview}...\"")

        print("\nGenerating model response...")
        q_start = time.time()
        answer = orchestrator.process_message(q, compare=comp)
        duration = time.time() - q_start

        print(f"\n--- MODEL RESPONSE (Generated in {duration:.2f}s) ---")
        print(answer)
        print("-" * 80)

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
