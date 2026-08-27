from app.intelligence.pipeline import analyze_query


def analyze_query_node(state):

    financial_query = analyze_query(
        state["user_query"]
    )

    state["financial_query"] = financial_query

    return state