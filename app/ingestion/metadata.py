import re


def extract_metadata(document) -> dict:
    """
    Extract company and fiscal period from the parsed document content.
    Does not depend on the PDF filename.
    """

    text = document.export_to_markdown()

    # Use the first part of the document because company/year
    # information is normally present near the beginning.
    text_sample = text[:12000]

    # --------------------------------
    # Extract fiscal period
    # --------------------------------

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
        # Fallback: look for "year ended March 31, 2025"
        year_match = re.search(
            r"year ended.*?March\s+\d{1,2},?\s+(\d{4})",
            text_sample,
            re.IGNORECASE | re.DOTALL,
        )

        if year_match:
            period = f"FY{year_match.group(1)[-2:]}"
        else:
            period = "UNKNOWN"

    # --------------------------------
    # Extract company
    # --------------------------------

    company = None

    company_patterns = [
        r"\bTata\s+Consultancy\s+Services\b",
        r"\bInfosys\b",
        r"\bHDFC\s+Bank\b",
        r"\bReliance\s+Industries\b",
        r"\bWipro\b",
        r"\bHCLTech\b",
    ]

    for pattern in company_patterns:
        match = re.search(
            pattern,
            text_sample,
            re.IGNORECASE,
        )

        if match:
            company = match.group(0).strip()
            break

    if company is None:
        # Generic fallback:
        # Look for "About <Company>"
        about_match = re.search(
            r"\bAbout\s+([A-Z][A-Za-z&.\- ]{2,60})",
            text_sample,
        )

        if about_match:
            company = about_match.group(1).strip()

    if company is None:
        company = "UNKNOWN"

    # Normalize known company names
    normalized_companies = {
        "tata consultancy services": "TCS",
        "tcs": "TCS",
        "infosys": "Infosys",
        "hdfc bank": "HDFC Bank",
        "reliance industries": "Reliance Industries",
        "wipro": "Wipro",
        "hcltech": "HCLTech",
    }

    company = normalized_companies.get(
        company.lower(),
        company,
    )

    # --------------------------------
    # Generate document ID
    # --------------------------------

    document_id = (
        f"{company.lower().replace(' ', '_')}_{period.lower()}"
    )

    return {
        "company": company,
        "period": period,
        "document_id": document_id,
    }