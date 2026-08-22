from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    PointStruct,
    SparseVector,
)


class QdrantStore:

    def __init__(self, url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=url)

    def create_collection(self, collection_name: str):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=1024,
                    distance=Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams()
                )
            },
        )

    def get_client(self):
        return self.client

    def upsert_points(
        self,
        collection_name: str,
        chunks: list[str],
        embeddings,
        document_id: str,
    ):
        points = []

        for i, chunk in enumerate(chunks):

            sparse_dict = embeddings["lexical_weights"][i]

            sparse_vector = SparseVector(
                indices=[int(k) for k in sparse_dict.keys()],
                values=[float(v) for v in sparse_dict.values()],
            )

            point = PointStruct(
                id=i,

                vector={
                    "dense": embeddings["dense_vecs"][i].tolist(),
                    "sparse": sparse_vector,
                },

                payload={
                    "text": chunk,
                    "document_id": document_id,
                    "chunk_index": i,
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

        return len(points)