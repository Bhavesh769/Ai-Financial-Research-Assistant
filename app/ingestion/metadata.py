from pathlib import Path
import re


def extract_metadata(file_path: str) -> dict:
    """
    Extract basic financial document metadata from the filename.
    """

    path = Path(file_path)

    filename = path.stem

    # Example:
    # TCS_FY25
    # Infosys_FY25
    # HDFC_FY24

    parts = filename.split("_")

    if len(parts) < 2:
        raise ValueError(
            f"Could not extract metadata from filename: {path.name}"
        )

    company = parts[0]
    period = parts[1].upper()

    document_id = filename.lower()

    return {
        "company": company,
        "period": period,
        "document_id": document_id,
    }