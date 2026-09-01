import json
import requests

from app.intelligence.schema import FinancialQuery

import os

OLLAMA_URL = (
    os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434",
    ).rstrip("/")
    + "/api/generate"
)

MODEL_NAME = "llama3:latest"


def parse_json_response(response_text: str) -> dict:
    response_text = response_text.strip()

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in LLM response.")

    json_text = response_text[start:end + 1]

    return json.loads(json_text)


def classify_query(query: str) -> FinancialQuery:
    prompt = f"""
You are a financial query analyzer.

Analyze the user's question and extract the following:

1. intent
2. companies
3. metrics
4. periods
5. whether the question is a comparison

Allowed intents:
- metric_lookup
- comparison
- trend_analysis
- explanation
- segment_analysis
- unknown

Examples of financial metrics:
- revenue
- revenue_growth
- operating_margin
- net_margin
- EBITDA
- EPS
- free_cash_flow

Return ONLY valid JSON.

Required JSON format:

{{
    "intent": "metric_lookup",
    "companies": [],
    "metrics": [],
    "periods": [],
    "comparison": false,
    "raw_query": "{query}"
}}

User question:
{query}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    response_text = response.json()["response"].strip()
    print("\nRAW LLM RESPONSE:")
    print(response_text)

    data = parse_json_response(response_text)

    return FinancialQuery(**data)