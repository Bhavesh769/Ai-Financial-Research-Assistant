from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore
from app.retrieval.hybrid import hybrid_search
from app.retrieval.company_resolver import resolve_company


def get_resolved_company(
    company_query,
    embedder,
    store,
):
    """
    Convert a user-facing company expression into
    the canonical company name stored in Qdrant.
    """

    resolved = resolve_company(
        company_query=company_query,
        embedder=embedder,
        store=store,
    )

    # If resolution fails, fall back to the original
    # expression rather than crashing the graph.
    return resolved or company_query


def metric_lookup_node(state):

    financial_query = state[
        "financial_query"
    ]

    company_query = (
        financial_query.companies[0]
    )

    metric = financial_query.metrics[0]
    period = financial_query.periods[0]

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    # ============================================================
    # Resolve company
    # ============================================================

    company = get_resolved_company(
        company_query,
        embedder,
        store,
    )

    print(
        f"Company query: {company_query}"
    )

    print(
        f"Resolved company: {company}"
    )

    search_query = (
        f"{company} {metric} {period}"
    )

    results = hybrid_search(
        query=search_query,
        embedder=embedder,
        store=store,
        collection_name="financial_documents",
        limit=5,
        company=company,
    )

    context_parts = []

    for result in results:

        context_parts.append(
            result["payload"]["text"]
        )

    state["context"] = (
        "\n\n".join(context_parts)
    )

    return state


def comparison_node(state):

    financial_query = state[
        "financial_query"
    ]

    metric = financial_query.metrics[0]
    period = financial_query.periods[0]

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    context_parts = []

    for company_query in (
        financial_query.companies
    ):

        company = get_resolved_company(
            company_query,
            embedder,
            store,
        )

        search_query = (
            f"{company} {metric} {period}"
        )

        print(
            f"Company query: {company_query}"
        )

        print(
            f"Resolved company: {company}"
        )

        results = hybrid_search(
            query=search_query,
            embedder=embedder,
            store=store,
            collection_name="financial_documents",
            limit=5,
            company=company,
        )

        context_parts.append(
            f"Evidence for {company}:"
        )

        if not results:

            context_parts.append(
                f"No relevant {company} "
                f"document found."
            )

            continue

        for result in results:

            context_parts.append(
                result["payload"]["text"]
            )

    state["context"] = (
        "\n\n".join(context_parts)
    )

    return state


def trend_analysis_node(state):

    financial_query = state[
        "financial_query"
    ]

    company_query = (
        financial_query.companies[0]
    )

    metric = financial_query.metrics[0]

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    company = get_resolved_company(
        company_query,
        embedder,
        store,
    )

    context_parts = []

    for period in (
        financial_query.periods
    ):

        search_query = (
            f"{company} {metric} {period}"
        )

        results = hybrid_search(
            query=search_query,
            embedder=embedder,
            store=store,
            collection_name="financial_documents",
            limit=5,
            company=company,
        )

        context_parts.append(
            f"Evidence for {company} - "
            f"{period}:"
        )

        if not results:

            context_parts.append(
                f"No relevant document found "
                f"for {company} {period}."
            )

            continue

        for result in results:

            context_parts.append(
                result["payload"]["text"]
            )

    state["context"] = (
        "\n\n".join(context_parts)
    )

    return state


def unknown_node(state):

    """
    Fallback retrieval for queries that don't
    match specialized financial workflows.
    """

    query = state["user_query"]

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    results = hybrid_search(
        query=query,
        embedder=embedder,
        store=store,
        collection_name="financial_documents",
        limit=5,
    )

    context_parts = []

    if not results:

        context_parts.append(
            "No relevant documents were found."
        )

    else:

        for result in results:

            context_parts.append(
                result["payload"]["text"]
            )

    state["context"] = (
        "\n\n".join(context_parts)
    )

    return state