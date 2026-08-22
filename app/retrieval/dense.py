from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore

def dense_search(
        query:str,
        embedder: BGE_M3_Embedder,
        store: QdrantStore,
        collection_name: str = "financial_document",
        limit: int = 5,
):
    query_embedding = embedder.encode([query])

    dense_vector = query_embedding["dense_vecs"][0].tolist()

    results = store.get_client().query_points(
        collection_name=collection_name,
        query=dense_vector,
        using="dense",
        limit=limit,
        with_payload=True,
    )

    return results.points