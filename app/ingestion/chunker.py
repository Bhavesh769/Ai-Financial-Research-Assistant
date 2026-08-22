from docling.chunking import HybridChunker

chunker = HybridChunker()

def chunk_document(document):

    chunks = []
    for chunk in chunker.chunk(document):
        text = chunker.contextualize(chunk)

        if text.strip():
            chunks.append(text)

    return chunks