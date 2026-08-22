from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore
from app.retrieval.hybrid import hybrid_search


def main():
    query = "What was TCS revenue growth in FY25?"

    print("Loading BGE-M3...")
    embedder = BGE_M3_Embedder()

    print("Connecting to Qdrant...")
    store = QdrantStore()

    print("\nRunning hybrid search...")
    results = hybrid_search(
        query=query,
        embedder=embedder,
        store=store,
        collection_name="financial_documents",
        limit=5,
    )

    print(f"\nRetrieved {len(results)} results:\n")

    for i, result in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print(f"ID: {result['id']}")
        print(f"RRF Score: {result['rrf_score']}")
        print(f"Document: {result['payload']['document_id']}")
        print(f"Chunk: {result['payload']['chunk_index']}")
        print(f"Text: {result['payload']['text'][:500]}")
        print()


if __name__ == "__main__":
    main()