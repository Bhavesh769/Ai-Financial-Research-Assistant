def calculate_rrf(
    dense_results,
    sparse_results,
    k: int = 60,
):
    """
    Combine dense and sparse rankings using
    Reciprocal Rank Fusion (RRF).

    RRF score:
        score = 1 / (k + rank)
    """

    scores = {}
    result_map = {}

   
    for rank, result in enumerate(dense_results, start=1):
        point_id = result.id

        scores[point_id] = scores.get(point_id, 0.0)
        scores[point_id] += 1 / (k + rank)

        result_map[point_id] = result

    
    for rank, result in enumerate(sparse_results, start=1):
        point_id = result.id

        scores[point_id] = scores.get(point_id, 0.0)
        scores[point_id] += 1 / (k + rank)

        result_map[point_id] = result

    
    ranked_results = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    final_results = []

    for point_id, score in ranked_results:
        result = result_map[point_id]

        final_results.append(
            {
                "id": point_id,
                "rrf_score": score,
                "payload": result.payload,
            }
        )

    return final_results