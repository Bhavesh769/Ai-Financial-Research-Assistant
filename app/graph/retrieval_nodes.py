from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore
from app.retrieval.hybrid import hybrid_search


def metric_lookup_node(state):

    financial_query = state["financial_query"]

    company = financial_query.companies[0]
    metric = financial_query.metrics[0]
    period = financial_query.periods[0]

    search_query = f"{company} {metric} {period}"

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

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

    state["context"] = "\n\n".join(context_parts)

    return state


def comparison_node(state):

    financial_query = state["financial_query"]

    metric = financial_query.metrics[0]
    period = financial_query.periods[0]

    context_parts = []

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    for company in financial_query.companies:

        search_query = f"{company} {metric} {period}"

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
                f"No relevant {company} document found."
            )
            continue

        for result in results:
            context_parts.append(
                result["payload"]["text"]
            )

    state["context"] = "\n\n".join(context_parts)

    return state


def trend_analysis_node(state):

    financial_query = state["financial_query"]

    company = financial_query.companies[0]
    metric = financial_query.metrics[0]

    context_parts = []

    embedder = BGE_M3_Embedder()
    store = QdrantStore()

    for period in financial_query.periods:

        search_query = f"{company} {metric} {period}"

        results = hybrid_search(
            query=search_query,
            embedder=embedder,
            store=store,
            collection_name="financial_documents",
            limit=5,
            company=company,
        )

        context_parts.append(
            f"Evidence for {company} - {period}:"
        )

        if not results:
            context_parts.append(
                f"No relevant document found for "
                f"{company} {period}."
            )
            continue

        for result in results:
            context_parts.append(
                result["payload"]["text"]
            )

    state["context"] = "\n\n".join(context_parts)

    return state


def unknown_node(state):
    """
    Fallback retrieval for queries that don't match
    our specialized financial workflows.
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

    state["context"] = "\n\n".join(context_parts)

    return state