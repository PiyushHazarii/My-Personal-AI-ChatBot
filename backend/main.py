# ============================================================
# PART 1 — IMPORTS AND FASTAPI SETUP
# ============================================================

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add root folder to python path
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend.config as config
from backend.vector_db import get_qdrant_client, setup_collection, upload_chunks
from backend.document_loader import load_all_documents
from backend.rag import answer_question

# Create FastAPI app
app = FastAPI(
    title="Piyush AI",
    description="Personal AI Chatbot for Piyush Hazari using RAG & Qdrant"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PART 2 — STARTUP EVENT
# ============================================================

@app.on_event("startup")
def on_startup():
    """Ensure collection exists on server startup."""
    try:
        client = get_qdrant_client()
        setup_collection(client, recreate=False)
        print("Backend startup complete!")
    except Exception as e:
        print(f"Startup warning: {e}")


# ============================================================
# PART 3 — REQUEST & RESPONSE SCHEMAS
# ============================================================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


# ============================================================
# PART 4 — API ENDPOINTS
# ============================================================

@app.get("/health")
def health_check():
    """Check backend health and Qdrant status."""
    client = get_qdrant_client()
    points_count = 0
    qdrant_status = "disconnected"

    try:
        if client.collection_exists(config.COLLECTION_NAME):
            info = client.get_collection(config.COLLECTION_NAME)
            points_count = info.points_count or 0
            qdrant_status = "connected"
    except Exception as e:
        qdrant_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "service": "Piyush AI Backend",
        "qdrant_status": qdrant_status,
        "collection": config.COLLECTION_NAME,
        "indexed_points": points_count
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint with strict boundary enforcement.
    """
    user_message = request.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        answer = answer_question(user_message)
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
def trigger_ingest():
    """Endpoint to trigger document ingestion on demand."""
    try:
        chunks = load_all_documents(config.DATA_DIR)
        count = upload_chunks(chunks)
        return {
            "status": "success",
            "message": f"Successfully ingested {count} chunks into Qdrant!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# PART 5 — RUN SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
