from app.intelligence.schema import FinancialQuery


METRIC_ALIASES = {
    "revenue growth": "revenue_growth",
    "revenue_growth": "revenue_growth",
    "growth in revenue": "revenue_growth",
    "top line growth": "revenue_growth",

    "free cash flow": "free_cash_flow",
    "free_cash_flow": "free_cash_flow",
    "fcf": "free_cash_flow",

    "operating margin": "operating_margin",
    "operating_margin": "operating_margin",

    "net margin": "net_margin",
    "net_margin": "net_margin",

    "revenue": "revenue",
    "ebitda": "ebitda",
    "eps": "eps",
}


def normalize_metric(metric: str) -> str:
    key = metric.strip().lower()
    return METRIC_ALIASES.get(key, key)


def validate_query(query: FinancialQuery) -> FinancialQuery:

    query.metrics = [
        normalize_metric(metric)
        for metric in query.metrics
    ]

    if query.intent == "comparison":

        if len(query.companies) < 2:
            raise ValueError(
                "A company comparison requires at least two companies."
            )

        query.comparison = True

    elif query.intent == "trend_analysis":

        if len(query.periods) >= 2:
            query.comparison = True
        else:
            query.comparison = False

    else:
        query.comparison = False

    return query