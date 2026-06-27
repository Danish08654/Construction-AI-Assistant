import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag.pipeline import get_rag

load_dotenv()

app = FastAPI(
    title="Construction RAG Assistant",
    description="Vertical RAG for construction — building codes, permits, materials, costs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load RAG at startup
print("Loading Construction RAG pipeline...")
rag = get_rag()
print("Ready.")


class QueryRequest(BaseModel):
    question: str
    k:        int = 5


class QueryResponse(BaseModel):
    question:    str
    answer:      str
    sources:     list
    categories:  list
    chunks_used: int


@app.get("/")
def root():
    return {
        "service":    "Construction RAG Assistant",
        "version":    "1.0.0",
        "model":      "LLaMA 3.3 70B via Groq",
        "embeddings": "all-MiniLM-L6-v2",
        "domains": [
            "Building Codes (IBC)",
            "Permits & Inspections",
            "Structural Engineering",
            "Materials & Specifications",
            "Electrical (NEC)",
            "Plumbing (UPC/IPC)",
            "HVAC & Mechanical",
            "Accessibility (ADA)",
            "Cost Estimation"
        ]
    }


@app.get("/health")
def health():
    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    return {
        "groq_key":   "SET" if groq_ok else "MISSING",
        "rag_ready":  rag._initialized,
        "index_path": rag.index_path,
        "status":     "healthy" if groq_ok and rag._initialized else "not ready"
    }


@app.post("/query", response_model=QueryResponse)
def query_construction(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    if len(req.question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long")

    try:
        result = rag.query(req.question)
        return QueryResponse(
            question   = req.question,
            answer     = result["answer"],
            sources    = result["sources"],
            categories = result["categories"],
            chunks_used= result["chunks_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def similarity_search(q: str, k: int = 5):
    """Raw similarity search — see what chunks are retrieved."""
    try:
        results = rag.similarity_search(q, k=k)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-base")
def knowledge_base_info():
    import json
    try:
        with open("knowledge_base/metadata.json") as f:
            metadata = json.load(f)
        return {
            "documents": len(metadata),
            "categories": list({m["category"] for m in metadata}),
            "titles": [m["title"] for m in metadata],
            "total_chunks": sum(m.get("chunks", 0) for m in metadata)
        }
    except Exception as e:
        return {"error": str(e)}