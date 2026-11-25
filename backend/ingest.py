# ============================================================
# PIYUSH AI — DOCUMENT INGESTION SCRIPT
# ============================================================

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend.config as config
from backend.document_loader import load_all_documents
from backend.vector_db import upload_chunks


def run_ingestion():
    print("=" * 60)
    print("PIYUSH AI — INGESTION PIPELINE")
    print("=" * 60)

    # 1. Load and chunk documents
    print(f"Reading documents from: {config.DATA_DIR}")
    chunks = load_all_documents(config.DATA_DIR)
    print(f"Total chunks extracted: {len(chunks)}")

    if not chunks:
        print("No documents found to ingest!")
        return 0

    # 2. Upload to Qdrant
    print("Generating embeddings and uploading to Qdrant...")
    uploaded_count = upload_chunks(chunks)

    print("=" * 60)
    print(f"INGESTION COMPLETE: {uploaded_count} points stored in Qdrant!")
    print("=" * 60)
    return uploaded_count


if __name__ == "__main__":
    run_ingestion()
