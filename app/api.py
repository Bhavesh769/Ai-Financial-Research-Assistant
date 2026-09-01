from pathlib import Path
import shutil
import tempfile
import re

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.parser import parse_document
from app.ingestion.chunker import chunk_document
from app.ingestion.metadata import extract_metadata

from app.intelligence.company_extractor import extract_company_entity

from app.embeddings.bge_m3 import BGE_M3_Embedder
from app.vector_store.qdrant import QdrantStore

from app.graph.graph import build_graph


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="AI Financial Research Assistant",
    description="RAG-based financial research assistant",
    version="1.0.0",
)


# ============================================================
# COLLECTIONS
# ============================================================

FINANCIAL_COLLECTION = "financial_documents"
COMPANY_ALIAS_COLLECTION = "company_aliases"


# ============================================================
# GLOBAL OBJECTS
# ============================================================

embedder = None
store = None
graph = None
current_document = None


# ============================================================
# REQUEST MODEL
# ============================================================

class QueryRequest(BaseModel):
    query: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "AI Financial Research Assistant API",
        "docs": "/docs",
    }


# ============================================================
# UPLOAD
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    global embedder
    global store
    global current_document

    print("\n" + "=" * 60, flush=True)
    print("STARTING DOCUMENT UPLOAD", flush=True)
    print("=" * 60, flush=True)

    # ========================================================
    # 1. Validate file
    # ========================================================

    print(
        f"Received file: {file.filename}",
        flush=True,
    )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # ========================================================
    # 2. Save uploaded PDF
    # ========================================================

    temp_dir = (
        Path(tempfile.gettempdir())
        / "ai_financial_assistant"
    )

    temp_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = temp_dir / file.filename

    print(
        "Saving uploaded PDF...",
        flush=True,
    )

    try:

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save PDF: {e}",
        )

    print(
        f"File saved: {file_path}",
        flush=True,
    )

    # ========================================================
    # 3. Parse PDF
    # ========================================================

    print(
        "Parsing PDF with Docling...",
        flush=True,
    )

    try:

        document = parse_document(
            str(file_path)
        )

    except Exception as e:

        print(
            f"PDF parsing failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse PDF: {e}",
        )

    print(
        "PDF parsing completed.",
        flush=True,
    )

    # ========================================================
    # 4. Extract basic metadata
    # ========================================================

    print(
        "Extracting document metadata...",
        flush=True,
    )

    try:

        metadata = extract_metadata(
            document
        )

    except Exception as e:

        print(
            f"Metadata extraction failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract metadata: {e}",
        )

    print(
        f"Period: {metadata['period']}",
        flush=True,
    )

    # ========================================================
    # 5. Validate fiscal period
    # ========================================================

    if metadata["period"] == "UNKNOWN":

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not identify the fiscal "
                "period from the document content."
            ),
        )

    # ========================================================
    # 6. Extract company + aliases using LLM
    # ========================================================

    print(
        "Identifying company using LLM...",
        flush=True,
    )

    try:

        document_text = document.export_to_markdown()

        company_entity = extract_company_entity(
            document_text[:12000]
        )

    except Exception as e:

        print(
            f"Company extraction failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to identify company "
                f"using LLM: {e}"
            ),
        )

    canonical_company = (
        company_entity["canonical_name"]
        .strip()
    )

    aliases = company_entity["aliases"]

    confidence = company_entity["confidence"]

    print(
        f"Canonical company: {canonical_company}",
        flush=True,
    )

    print(
        f"Aliases: {aliases}",
        flush=True,
    )

    print(
        f"Confidence: {confidence}",
        flush=True,
    )

    # ========================================================
    # 7. Validate company extraction
    # ========================================================

    if (
        not canonical_company
        or canonical_company.upper() == "UNKNOWN"
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not confidently identify the "
                "company from the document content."
            ),
        )

    # Confidence threshold
    if confidence < 0.80:

        raise HTTPException(
            status_code=400,
            detail=(
                "Company identification confidence "
                f"is too low: {confidence:.2f}"
            ),
        )

    # ========================================================
    # 8. Generate canonical document ID
    # ========================================================

    company_slug = re.sub(
        r"[^a-z0-9]+",
        "_",
        canonical_company.lower(),
    ).strip("_")

    document_id = (
        f"{company_slug}_{metadata['period'].lower()}"
    )

    print(
        f"Document ID: {document_id}",
        flush=True,
    )

    # ========================================================
    # 9. Chunk document
    # ========================================================

    print(
        "Creating document chunks...",
        flush=True,
    )

    try:

        chunks = chunk_document(
            document
        )

    except Exception as e:

        print(
            f"Chunking failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to chunk document: {e}",
        )

    print(
        f"Chunks created: {len(chunks)}",
        flush=True,
    )

    # ========================================================
    # 10. Connect to Qdrant
    # ========================================================

    print(
        "Connecting to Qdrant...",
        flush=True,
    )

    try:

        if store is None:
            store = QdrantStore()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Qdrant: {e}",
        )

    print(
        "Qdrant connected.",
        flush=True,
    )

    # ========================================================
    # 11. Clear previous financial document collection
    # ========================================================

    print(
        "Clearing previous document data...",
        flush=True,
    )

    try:

        store.get_client().delete_collection(
            collection_name=FINANCIAL_COLLECTION
        )

        print(
            "Previous financial collection deleted.",
            flush=True,
        )

    except Exception:

        print(
            "No previous financial collection found.",
            flush=True,
        )

    # ========================================================
    # 12. Create fresh financial collection
    # ========================================================

    print(
        "Creating fresh financial collection...",
        flush=True,
    )

    try:

        store.create_collection(
            FINANCIAL_COLLECTION
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to create financial "
                f"collection: {e}"
            ),
        )

    print(
        "Financial collection ready.",
        flush=True,
    )

    # ========================================================
    # 13. Create persistent company alias collection
    # ========================================================

    print(
        "Preparing company alias collection...",
        flush=True,
    )

    try:

        existing_collections = (
            store.get_client()
            .get_collections()
            .collections
        )

        collection_names = {
            collection.name
            for collection in existing_collections
        }

        if COMPANY_ALIAS_COLLECTION not in collection_names:

            store.create_alias_collection(
                COMPANY_ALIAS_COLLECTION
            )

            print(
                "Company alias collection created.",
                flush=True,
            )

        else:

            print(
                "Company alias collection already exists.",
                flush=True,
            )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to prepare company alias "
                f"collection: {e}"
            ),
        )

    # ========================================================
    # 14. Load BGE-M3
    # ========================================================

    print(
        "Loading BGE-M3...",
        flush=True,
    )

    try:

        if embedder is None:
            embedder = BGE_M3_Embedder()

    except Exception as e:

        print(
            f"BGE-M3 loading failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to load BGE-M3: {e}",
        )

    print(
        "BGE-M3 loaded.",
        flush=True,
    )

    # ========================================================
    # 15. Generate document embeddings
    # ========================================================

    print(
        "Generating embeddings...",
        flush=True,
    )

    try:

        embeddings = embedder.encode(
            chunks
        )

    except Exception as e:

        print(
            f"Embedding generation failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to generate embeddings: {e}"
            ),
        )

    print(
        f"Dense vectors: "
        f"{len(embeddings['dense_vecs'])}",
        flush=True,
    )

    print(
        f"Sparse vectors: "
        f"{len(embeddings['lexical_weights'])}",
        flush=True,
    )

    # ========================================================
    # 16. Store financial document vectors
    # ========================================================

    print(
        "Storing financial vectors in Qdrant...",
        flush=True,
    )

    try:

        stored = store.upsert_points(
            collection_name=FINANCIAL_COLLECTION,
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            company=canonical_company,
        )

    except Exception as e:

        print(
            f"Qdrant financial storage failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to store financial vectors: {e}"
            ),
        )

    print(
        f"Financial vectors stored: {stored}",
        flush=True,
    )

    # ========================================================
    # 17. Store company aliases
    # ========================================================

    print(
        "Storing company aliases...",
        flush=True,
    )

    try:

        aliases_stored = (
            store.upsert_company_aliases(
                collection_name=COMPANY_ALIAS_COLLECTION,
                canonical_name=canonical_company,
                aliases=aliases,
                embedder=embedder,
            )
        )

    except Exception as e:

        print(
            f"Company alias storage failed: {e}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to store company aliases: {e}"
            ),
        )

    print(
        f"Company aliases stored: {aliases_stored}",
        flush=True,
    )

    # ========================================================
    # 18. Save current document
    # ========================================================

    current_document = {
        "company": canonical_company,
        "period": metadata["period"],
        "document_id": document_id,
        "aliases": aliases,
    }

    # ========================================================
    # 19. Complete
    # ========================================================

    print("\n" + "=" * 60, flush=True)
    print("DOCUMENT READY FOR QUESTIONS", flush=True)
    print("=" * 60, flush=True)

    return {
        "message": "Document indexed successfully.",
        "company": canonical_company,
        "period": metadata["period"],
        "document_id": document_id,
        "aliases": aliases,
        "company_confidence": confidence,
        "chunks": len(chunks),
        "vectors_stored": stored,
        "aliases_stored": aliases_stored,
    }


# ============================================================
# QUERY
# ============================================================

@app.post("/query")
def query_document(
    request: QueryRequest
):

    global graph
    global current_document

    print()
    print("=" * 60)
    print("QUERY RECEIVED")
    print("=" * 60)

    print(
        f"Question: {request.query}"
    )

    # ========================================================
    # 1. Check document
    # ========================================================

    if current_document is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please upload a financial "
                "PDF before asking a question."
            ),
        )

    print(
        f"Document: "
        f"{current_document['company']} "
        f"{current_document['period']}"
    )

    # ========================================================
    # 2. Build LangGraph
    # ========================================================

    print("Building LangGraph...")

    try:

        if graph is None:
            graph = build_graph()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not build LangGraph: {e}",
        )

    print("LangGraph ready")

    # ========================================================
    # 3. Initial state
    # ========================================================

    initial_state = {
        "user_query": request.query,
        "financial_query": None,
        "context": "",
        "answer": "",
    }

    # ========================================================
    # 4. Run graph
    # ========================================================

    print("Running LangGraph...")

    try:

        result = graph.invoke(
            initial_state
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to process query: {e}"
            ),
        )

    print("LangGraph completed")

    # ========================================================
    # 5. Extract intent
    # ========================================================

    financial_query = result.get(
        "financial_query"
    )

    intent = None

    if financial_query:
        intent = financial_query.intent

    print(
        f"Intent: {intent}"
    )

    print("=" * 60)
    print("QUERY COMPLETED")
    print("=" * 60)

    return {
        "query": request.query,
        "company": current_document["company"],
        "period": current_document["period"],
        "intent": intent,
        "answer": result.get(
            "answer",
            "",
        ),
    }