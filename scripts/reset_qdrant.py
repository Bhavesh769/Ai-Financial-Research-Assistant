from app.vector_store.qdrant import QdrantStore


COLLECTION_NAME = "financial_documents"


def main():

    store = QdrantStore()

    client = store.get_client()

    if client.collection_exists(COLLECTION_NAME):
        print("Deleting existing collection...")
        client.delete_collection(COLLECTION_NAME)

    print("Creating fresh collection...")

    store.create_collection(COLLECTION_NAME)

    print("Qdrant reset complete.")


if __name__ == "__main__":
    main()