from app.ingestion.parser import parse_document
from app.intelligence.company_extractor import extract_company_entity


FILE_PATH = "data/TCS_FY25.pdf"


document = parse_document(FILE_PATH)

text = document.export_to_markdown()

result = extract_company_entity(text[:12000])

print("\n" + "=" * 60)
print("COMPANY EXTRACTION RESULT")
print("=" * 60)

print("Canonical:", result["canonical_name"])
print("Aliases:", result["aliases"])
print("Confidence:", result["confidence"])