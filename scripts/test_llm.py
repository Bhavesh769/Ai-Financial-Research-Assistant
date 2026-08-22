from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore
from app.retrieval.hybrid import hybrid_search
from app.llm.ollama import generate_answer


def main():
    query = "What was TCS revenue growth in FY25?"

    print("Loading BGE-M3...")
    embedder = BGE_M3_Embedder()

    print("Connecting to Qdrant...")
    store = QdrantStore()

    print("Retrieving relevant evidence...")
    results = hybrid_search(
        query=query,
        embedder=embedder,
        store=store,
        collection_name="financial_documents",
        limit=5,
    )

    
    context_parts = []

    for result in results:
        text = result["payload"]["text"]
        context_parts.append(text)

    context = "\n\n".join(context_parts)

    print("\nGenerating answer with Ollama...")

    answer = generate_answer(
        query=query,
        context=context,
    )

    print("\n========== ANSWER ==========")
    print(answer)


if __name__ == "__main__":
    main()