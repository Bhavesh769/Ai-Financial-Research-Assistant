from qdrant_client.models import Filter, FieldCondition, MatchValue


COMPANY_ALIAS_COLLECTION = "company_aliases"


def resolve_company(
    company_query: str,
    embedder,
    store,
):
    """
    Resolve a user's company expression such as:

        TCS
        Tata Consultancy Services
        Tata Consultancy

    into the canonical company name stored in Qdrant.

    Resolution strategy:

    1. Exact alias/canonical match
    2. Dense semantic search
    3. Return canonical company only when a candidate exists
    """

    company_query = company_query.strip()

    if not company_query:
        return None

    client = store.get_client()

    # ============================================================
    # 1. Exact match
    # ============================================================

    exact_filter = Filter(
        should=[
            FieldCondition(
                key="alias",
                match=MatchValue(
                    value=company_query
                ),
            ),
            FieldCondition(
                key="canonical_name",
                match=MatchValue(
                    value=company_query
                ),
            ),
        ]
    )

    exact_results = client.scroll(
        collection_name=COMPANY_ALIAS_COLLECTION,
        scroll_filter=exact_filter,
        limit=1,
        with_payload=True,
        with_vectors=False,
    )[0]

    if exact_results:

        payload = (
            exact_results[0].payload
            or {}
        )

        return payload.get(
            "canonical_name"
        )

    # ============================================================
    # 2. Semantic search
    # ============================================================

    embedding = embedder.encode(
        [company_query]
    )

    dense_vector = embedding[
        "dense_vecs"
    ][0]

    results = (
        client.query_points(
            collection_name=COMPANY_ALIAS_COLLECTION,
            query=dense_vector.tolist(),
            limit=3,
            with_payload=True,
        )
        .points
    )

    if not results:
        return None

    # ============================================================
    # 3. Return best canonical candidate
    # ============================================================

    best = results[0]

    payload = best.payload or {}

    canonical_name = payload.get(
        "canonical_name"
    )

    return canonical_name