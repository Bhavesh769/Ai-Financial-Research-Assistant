from app.intelligence.classifier import classify_query
from app.intelligence.validator import validate_query
from app.intelligence.schema import FinancialQuery


def analyze_query(query: str) -> FinancialQuery:

    financial_query = classify_query(query)

    validated_query = validate_query(financial_query)

    return validated_query