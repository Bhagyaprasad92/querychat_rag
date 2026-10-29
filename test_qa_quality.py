import time
from chatbot.orchestrator import ChatOrchestrator
from rag.ingest import ingest_pdf

metadata = ingest_pdf('sample_document.pdf')
orc = ChatOrchestrator()
orc.add_document(metadata)

queries = [
    "summarize this document",
    "what is the tech stack this project used to develop?",
    "then give me a guess of the tech stack this project developed on?"
]

print("=" * 80)
print("TESTING RETRIEVAL & ANSWER QUALITY")
print("=" * 80)

for q in queries:
    print(f"\n>> QUESTION: {q}")
    retrieved = orc.rag_engine.retrieve(q)
    print(f"Retrieved Chunks: {len(retrieved)} (Scores: {[round(r['score'], 3) for r in retrieved]})")
    ans = orc.process_message(q)
    print(">> RESPONSE:")
    print(ans)
    print("-" * 80)

