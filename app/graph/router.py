def route_query(state):
    """
    Decide which retrieval node should handle the query.
    """

    financial_query = state["financial_query"]

    intent = financial_query.intent

    if intent == "metric_lookup":
        return "metric_lookup"

    if intent == "comparison":
        return "comparison"

    if intent == "trend_analysis":
        return "trend_analysis"

    return "unknown"