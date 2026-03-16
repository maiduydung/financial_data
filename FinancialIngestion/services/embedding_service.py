"""Generate embeddings and store in Chroma Cloud."""

import logging
import uuid
import chromadb
from openai import OpenAI
from config import (
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHROMA_API_KEY,
    CHROMA_TENANT,
    CHROMA_DATABASE,
    CHROMA_COLLECTION,
)

logger = logging.getLogger(__name__)


def _get_chroma_client():
    return chromadb.CloudClient(
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
        api_key=CHROMA_API_KEY,
    )


def _get_openai_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using OpenAI."""
    client = _get_openai_client()
    response = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    return [item.embedding for item in response.data]


def store_documents(documents: list[dict]):
    """Store processed documents with embeddings in Chroma Cloud.

    Each document: {"text": str, "metadata": dict}
    """
    if not documents:
        return

    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    ids = [str(uuid.uuid4()) for _ in documents]

    # Generate embeddings in batches of 100
    all_embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i : i + 100]
        embeddings = generate_embeddings(batch)
        all_embeddings.extend(embeddings)

    # Store in Chroma Cloud
    chroma = _get_chroma_client()
    collection = chroma.get_or_create_collection(name=CHROMA_COLLECTION)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    logger.info("🧠 Stored %d documents in Chroma collection '%s'", len(documents), CHROMA_COLLECTION)
