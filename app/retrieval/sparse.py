from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore
from qdrant_client.models import SparseVector


def sparse_search(
    query: str,
    embedder: BGE_M3_Embedder,
    store: QdrantStore,
    collection_name: str = "financial_documents",
    limit: int = 5,
):
    

    query_embedding = embedder.encode([query])

    sparse_dict = query_embedding["lexical_weights"][0]

    sparse_vector = SparseVector(
        indices=[int(k) for k in sparse_dict.keys()],
        values=[float(v) for v in sparse_dict.values()],
    )

    results = store.get_client().query_points(
        collection_name=collection_name,
        query=sparse_vector,
        using="sparse",
        limit=limit,
        with_payload=True,
    )

    return results.points