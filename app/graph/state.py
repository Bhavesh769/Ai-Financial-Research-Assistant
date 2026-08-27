from typing import TypedDict, Optional

from app.intelligence.schema import FinancialQuery


class GraphState(TypedDict):
    user_query: str
    financial_query: Optional[FinancialQuery]
    context: str
    answer: str