# ============================================================
# PART 1 — IMPORTS AND ENVIRONMENT
# ============================================================

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import backend.config as config


# ============================================================
# PART 2 — CONNECT TO QDRANT
# ============================================================

def get_qdrant_client():
    """Connect to Qdrant Cloud using credentials from .env."""
    return QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY if config.QDRANT_API_KEY else None
    )


# ============================================================
# PART 3 — LOAD EMBEDDING MODEL
# ============================================================

_embedding_model = None

def get_embedding_model():
    """Load SentenceTransformer model once and reuse it."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}...")
        _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        print("Embedding model ready!")
    return _embedding_model


# ============================================================
# PART 4 — CREATE / RECREATE QDRANT COLLECTION
# ============================================================

def setup_collection(client, recreate=False):
    """Create collection in Qdrant if it doesn't already exist."""
    collection_name = config.COLLECTION_NAME

    if client.collection_exists(collection_name):
        if recreate:
            print(f"Deleting existing collection: {collection_name}")
            client.delete_collection(collection_name)
        else:
            return

    print(f"Creating collection: {collection_name}")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=config.EMBEDDING_SIZE,
            distance=Distance.COSINE
        )
    )
    print("Collection ready!")


# ============================================================
# PART 5 — UPLOAD CHUNKS TO QDRANT
# ============================================================

def upload_chunks(chunks, batch_size=64):
    """
    Generate embeddings for chunks and upload them to Qdrant.
    """
    if not chunks:
        return 0

    client = get_qdrant_client()
    model = get_embedding_model()

    # Recreate collection for fresh upload
    setup_collection(client, recreate=True)

    texts = [chunk["text"] for chunk in chunks]
    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)

    # Create Qdrant points
    points = []
    for i, chunk in enumerate(chunks):
        point = PointStruct(
            id=chunk["id"],
            vector=embeddings[i].tolist(),
            payload={
                "text": chunk["text"],
                "source": chunk["source"]
            }
        )
        points.append(point)

    # Upload in batches
    print(f"Uploading {len(points)} points to Qdrant collection '{config.COLLECTION_NAME}'...")
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=config.COLLECTION_NAME,
            points=batch
        )

    print(f"Successfully uploaded {len(points)} points to Qdrant!")
    return len(points)


# ============================================================
# PART 6 — SEARCH QDRANT
# ============================================================

def search(query, top_k=5):
    """
    Search Qdrant for document chunks most similar to the user question.
    """
    client = get_qdrant_client()

    if not client.collection_exists(config.COLLECTION_NAME):
        return []

    model = get_embedding_model()
    query_vector = model.encode(query).tolist()

    # Query Qdrant
    try:
        results = client.query_points(
            collection_name=config.COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True
        ).points
    except Exception:
        results = client.search(
            collection_name=config.COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k
        )

    # Format results
    hits = []
    for r in results:
        hits.append({
            "score": r.score,
            "text": r.payload.get("text", "") if r.payload else "",
            "source": r.payload.get("source", "") if r.payload else ""
        })

    return hits
