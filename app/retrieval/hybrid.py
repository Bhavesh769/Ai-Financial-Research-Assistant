from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore

from app.retrieval.dense import dense_search
from app.retrieval.sparse import sparse_search
from app.retrieval.rrf import calculate_rrf


def hybrid_search(
    query: str,
    embedder: BGE_M3_Embedder,
    store: QdrantStore,
    collection_name: str = "financial_documents",
    limit: int = 5,
):

    dense_results = dense_search(
        query=query,
        embedder=embedder,
        store=store,
        collection_name=collection_name,
        limit=limit,
    )

    sparse_results = sparse_search(
        query=query,
        embedder=embedder,
        store=store,
        collection_name=collection_name,
        limit=limit,
    )

    final_results = calculate_rrf(
        dense_results=dense_results,
        sparse_results=sparse_results,
    )

    return final_results[:limit]