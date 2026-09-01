import uuid
import os
from typing import Optional

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

    def __init__(
        self,
        url: Optional[str] = None,
    ):
        if url is None:
            url = os.getenv(
                "QDRANT_URL",
                "http://localhost:6333",
            )

        self.client = QdrantClient(
            url=url
        )

    # ============================================================
    # COLLECTION
    # ============================================================

    def create_collection(
        self,
        collection_name: str,
    ):
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

    # ============================================================
    # COMPANY ALIAS COLLECTION
    # ============================================================

    def create_alias_collection(
        self,
        collection_name: str = "company_aliases",
    ):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE,
            ),
        )

    # ============================================================
    # CLIENT
    # ============================================================

    def get_client(self):
        return self.client

    # ============================================================
    # FINANCIAL DOCUMENT VECTORS
    # ============================================================

    def upsert_points(
        self,
        collection_name: str,
        chunks: list[str],
        embeddings,
        document_id: str,
        company: str,
    ):
        points = []

        for i, chunk in enumerate(chunks):

            sparse_dict = embeddings[
                "lexical_weights"
            ][i]

            sparse_vector = SparseVector(
                indices=[
                    int(k)
                    for k in sparse_dict.keys()
                ],
                values=[
                    float(v)
                    for v in sparse_dict.values()
                ],
            )

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{document_id}_{i}",
                )
            )

            point = PointStruct(
                id=point_id,

                vector={
                    "dense": embeddings[
                        "dense_vecs"
                    ][i].tolist(),

                    "sparse": sparse_vector,
                },

                payload={
                    "text": chunk,
                    "document_id": document_id,
                    "company": company,
                    "chunk_index": i,
                },
            )

            points.append(point)

        self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

        return len(points)

    # ============================================================
    # COMPANY ALIASES
    # ============================================================

    def upsert_company_aliases(
        self,
        collection_name: str,
        canonical_name: str,
        aliases: list[str],
        embedder,
    ):
        """
        Store one vector for the canonical company name
        and one vector for every known alias.

        All vectors point back to the same canonical company.
        """

        points = []

        names = [
            canonical_name,
            *aliases,
        ]

        # Remove duplicates while preserving order.
        unique_names = []

        for name in names:

            name = str(name).strip()

            if not name:
                continue

            if name.lower() not in [
                existing.lower()
                for existing in unique_names
            ]:
                unique_names.append(name)

        for name in unique_names:

            embedding = embedder.encode(
                [name]
            )

            vector = embedding[
                "dense_vecs"
            ][0].tolist()

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"company_entity::{canonical_name}::{name}",
                )
            )

            point = PointStruct(
                id=point_id,

                vector=vector,

                payload={
                    "canonical_name": canonical_name,
                    "alias": name,
                    "entity_type": "company",
                },
            )

            points.append(point)

        if points:

            self.client.upsert(
                collection_name=collection_name,
                points=points,
            )

        return len(points)