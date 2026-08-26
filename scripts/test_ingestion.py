from app.ingestion.pipeline import ingest_document
from app.ingestion.metadata import extract_metadata
from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore


PDF_PATH = "data/Infosys_FY25.pdf"
COLLECTION_NAME = "financial_documents"


def main():

    print("1. Extracting metadata...")

    metadata = extract_metadata(PDF_PATH)

    print(f"Company: {metadata['company']}")
    print(f"Period: {metadata['period']}")
    print(f"Document ID: {metadata['document_id']}")


    print("\n2. Ingesting document...")

    chunks = ingest_document(PDF_PATH)

    print(f"Chunks: {len(chunks)}")


    print("\n3. Loading BGE-M3...")

    embedder = BGE_M3_Embedder()


    print("\n4. Generating embeddings...")

    embeddings = embedder.encode(chunks)

    print(f"Dense vectors: {len(embeddings['dense_vecs'])}")
    print(f"Sparse vectors: {len(embeddings['lexical_weights'])}")


    print("\n5. Connecting to Qdrant...")

    store = QdrantStore()


    print("\n6. Storing vectors...")

    count = store.upsert_points(
        collection_name=COLLECTION_NAME,
        chunks=chunks,
        embeddings=embeddings,
        document_id=metadata["document_id"],
        company=metadata["company"],
    )

    print(f"Stored: {count}")


    print("\n7. Verifying Qdrant...")

    info = store.get_client().get_collection(COLLECTION_NAME)

    print(f"Points in Qdrant: {info.points_count}")


if __name__ == "__main__":
    main()