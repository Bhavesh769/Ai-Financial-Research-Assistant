import re


def extract_metadata(document) -> dict:
    """
    Extract basic metadata from the parsed document.

    The fiscal period is extracted using deterministic rules.
    Company identification is intentionally handled by the
    separate LLM-based company entity extraction layer.
    """

    text = document.export_to_markdown()

    # Keep the beginning of the document available for
    # the company/entity extraction layer.
    text_sample = text[:12000]

    # ============================================================
    # 1. Extract fiscal period
    # ============================================================

    period = "UNKNOWN"

    # Examples:
    # FY25
    # FY 25
    # FY2025
    # FY 2025
    period_match = re.search(
        r"\bFY\s?(\d{2,4})\b",
        text_sample,
        re.IGNORECASE,
    )

    if period_match:

        year = period_match.group(1)

        if len(year) == 4:
            year = year[-2:]

        period = f"FY{year}"

    else:

        # Example:
        # "year ended March 31, 2025"
        year_match = re.search(
            r"year\s+ended.*?March\s+\d{1,2},?\s+(\d{4})",
            text_sample,
            re.IGNORECASE | re.DOTALL,
        )

        if year_match:
            period = f"FY{year_match.group(1)[-2:]}"

    # ============================================================
    # 2. Company is NOT extracted here
    # ============================================================

    # The company will be identified by the dedicated
    # LLM entity extraction layer.

    company = "UNKNOWN"

    # ============================================================
    # 3. Temporary document ID
    # ============================================================

    # The final document_id will be generated after the
    # canonical company name has been resolved.

    document_id = f"unknown_{period.lower()}"

    # ============================================================
    # 4. Return metadata
    # ============================================================

    return {
        "company": company,
        "period": period,
        "document_id": document_id,
        "text_sample": text_sample,
    }