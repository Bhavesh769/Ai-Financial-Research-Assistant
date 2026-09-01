import json
import requests


import os

OLLAMA_URL = (
    os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434",
    ).rstrip("/")
    + "/api/generate"
)

MODEL_NAME = "llama3:latest"


def extract_company_entity(text: str) -> dict:
    """
    Extract the canonical company name and aliases from
    the beginning of a financial document.

    The company identity must come from the document content,
    not from the filename.
    """

    prompt = f"""
You are a financial document entity extraction system.

Identify the company that this document is primarily about.

Return ONLY valid JSON.

Required format:

{{
    "canonical_name": "Full official company name",
    "aliases": ["alias1", "alias2"],
    "confidence": 0.0
}}

Rules:

1. Identify the company from the document itself.
2. Prefer the full legal/canonical company name.
3. Do not use the PDF filename.
4. Extract abbreviations that explicitly refer to the company.
5. Extract stock symbols only when they clearly belong to the company.
6. Do not invent aliases.
7. Do not use unrelated companies mentioned in the document.
8. If the company cannot be identified confidently, use:
   "canonical_name": "UNKNOWN"
9. Confidence must be between 0 and 1.
10. Return JSON only. No explanation.

Document:

{text}

JSON:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    raw_response = response.json()["response"].strip()

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Company extractor returned invalid JSON: "
            f"{raw_response}"
        ) from exc

    canonical_name = str(
        result.get("canonical_name", "UNKNOWN")
    ).strip()

    aliases = result.get("aliases", [])

    if not isinstance(aliases, list):
        aliases = []

    aliases = [
        str(alias).strip()
        for alias in aliases
        if str(alias).strip()
    ]

    confidence = result.get("confidence", 0.0)

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    return {
        "canonical_name": canonical_name,
        "aliases": aliases,
        "confidence": confidence,
    }