from pydantic import BaseModel, Field
from typing import Optional


class FinancialQuery(BaseModel):
    intent: str = Field(
        description="Type of financial question"
    )

    companies: list[str] = Field(
        default_factory=list
    )

    metrics: list[str] = Field(
        default_factory=list
    )

    periods: list[str] = Field(
        default_factory=list
    )

    comparison: bool = False

    raw_query: str = ""