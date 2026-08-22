from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

def parse_document(file_path: str):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    result = converter.convert(str(path))

    return result.document

