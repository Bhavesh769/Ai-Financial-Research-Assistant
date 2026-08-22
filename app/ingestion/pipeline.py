from app.ingestion.parser import parse_document
from app.ingestion.chunker import chunk_document

def ingest_document(file_path: str):

    document = parse_document(file_path)

    chunks = chunk_document(document)

    return chunks