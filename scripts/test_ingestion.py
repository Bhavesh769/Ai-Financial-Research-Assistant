from app.ingestion.pipeline import ingest_document
from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore


PDF_PATH = "data/TCS_FY25.pdf"
COLLECTION_NAME = "financial_documents"


def main():
    print("1. Ingesting document...")
    chunks = ingest_document(PDF_PATH)
    print(f"Chunks: {len(chunks)}")

    print("\n2. Loading BGE-M3...")
    embedder = BGE_M3_Embedder()

    print("\n3. Generating embeddings...")
    embeddings = embedder.encode(chunks)

    print(f"Dense vectors: {len(embeddings['dense_vecs'])}")
    print(f"Sparse vectors: {len(embeddings['lexical_weights'])}")

    print("\n4. Connecting to Qdrant...")
    store = QdrantStore()

    print("\n5. Storing vectors...")
    count = store.upsert_points(
        collection_name=COLLECTION_NAME,
        chunks=chunks,
        embeddings=embeddings,
        document_id="tcs_fy25",
    )

    print(f"Stored: {count}")

    print("\n6. Verifying Qdrant...")
    info = store.get_client().get_collection(COLLECTION_NAME)

    print(f"Points in Qdrant: {info.points_count}")


if __name__ == "__main__":
    main()