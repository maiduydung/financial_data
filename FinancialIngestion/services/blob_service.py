"""Azure Blob Storage helpers."""

import json
import logging
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_RAW

logger = logging.getLogger(__name__)


def get_blob_service() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def upload_raw_json(symbol: str, data: dict):
    """Upload raw company JSON to Azure Blob Storage."""
    if not AZURE_STORAGE_CONNECTION_STRING:
        logger.warning("⏭️ No Azure Storage connection string — skipping blob upload for %s", symbol)
        return

    client = get_blob_service()
    container = client.get_container_client(BLOB_CONTAINER_RAW)

    # Create container if it doesn't exist
    try:
        container.create_container()
    except Exception:
        pass  # Already exists

    blob_name = f"{symbol}/raw_data.json"
    container.upload_blob(
        name=blob_name,
        data=json.dumps(data, indent=2),
        overwrite=True,
    )
    logger.info("☁️ Uploaded raw data to blob: %s", blob_name)


def download_raw_json(symbol: str) -> dict | None:
    """Download raw company JSON from Blob Storage."""
    client = get_blob_service()
    container = client.get_container_client(BLOB_CONTAINER_RAW)
    blob_name = f"{symbol}/raw_data.json"
    try:
        blob = container.download_blob(blob_name)
        return json.loads(blob.readall())
    except Exception as e:
        logger.error("❌ Failed to download %s: %s", blob_name, e)
        return None
