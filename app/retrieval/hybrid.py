from qdrant_client.models import Filter, FieldCondition, MatchValue


def hybrid_search(
    query,
    embedder,
    store,
    collection_name,
    limit=5,
    company=None,
):
    """
    Perform dense + sparse search and combine results using RRF.

    If company is provided, only chunks belonging to that
    company are searched.
    """

    # --------------------------------------------------
    # 1. Generate query embeddings
    # --------------------------------------------------

    embeddings = embedder.encode([query])

    dense_vector = embeddings["dense_vecs"][0]

    sparse_dict = embeddings["lexical_weights"][0]

    sparse_indices = [
        int(k) for k in sparse_dict.keys()
    ]

    sparse_values = [
        float(v) for v in sparse_dict.values()
    ]

    # --------------------------------------------------
    # 2. Create company filter if requested
    # --------------------------------------------------

    query_filter = None

    if company:
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="company",
                    match=MatchValue(value=company),
                )
            ]
        )

    # --------------------------------------------------
    # 3. Dense search
    # --------------------------------------------------

    dense_results = store.get_client().query_points(
        collection_name=collection_name,
        query=dense_vector.tolist(),
        using="dense",
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    ).points

    # --------------------------------------------------
    # 4. Sparse search
    # --------------------------------------------------

    from qdrant_client.models import SparseVector

    sparse_vector = SparseVector(
        indices=sparse_indices,
        values=sparse_values,
    )

    sparse_results = store.get_client().query_points(
        collection_name=collection_name,
        query=sparse_vector,
        using="sparse",
        query_filter=query_filter,
        limit=limit,
        with_payload=True,
    ).points

    # --------------------------------------------------
    # 5. Calculate RRF
    # --------------------------------------------------

    rrf_scores = {}

    k = 60

    for rank, result in enumerate(dense_results):
        point_id = str(result.id)

        if point_id not in rrf_scores:
            rrf_scores[point_id] = {
                "score": 0.0,
                "result": result,
            }

        rrf_scores[point_id]["score"] += 1 / (k + rank + 1)

    for rank, result in enumerate(sparse_results):
        point_id = str(result.id)

        if point_id not in rrf_scores:
            rrf_scores[point_id] = {
                "score": 0.0,
                "result": result,
            }

        rrf_scores[point_id]["score"] += 1 / (k + rank + 1)

    # --------------------------------------------------
    # 6. Sort by RRF score
    # --------------------------------------------------

    ranked_results = sorted(
        rrf_scores.values(),
        key=lambda x: x["score"],
        reverse=True,
    )

    # --------------------------------------------------
    # 7. Return final results
    # --------------------------------------------------

    final_results = []

    for item in ranked_results[:limit]:

        result = item["result"]

        final_results.append(
            {
                "id": result.id,
                "rrf_score": item["score"],
                "payload": result.payload,
            }
        )

    return final_results