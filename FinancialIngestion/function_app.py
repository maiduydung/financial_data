"""Azure Function App for Financial Data Ingestion Pipeline.

Endpoints:
  - POST /api/ingest         → Ingest data for all configured companies
  - POST /api/ingest/{symbol} → Ingest data for a specific company
"""

import logging
import json
import asyncio
import azure.functions as func
from config import COMPANIES
from services.fmp_client import fetch_company_data
from services.blob_service import upload_raw_json
from services.processor import process_company_data
from services.embedding_service import store_documents

app = func.FunctionApp()
logger = logging.getLogger(__name__)


async def _ingest_company(symbol: str) -> dict:
    """Full pipeline for one company: fetch → blob → process → embed."""
    logger.info("🚀 Starting ingestion for %s", symbol)

    # 1. Fetch from FMP API
    raw_data = await fetch_company_data(symbol)
    if not raw_data.get("profile"):
        logger.error("❌ Failed to fetch profile data for %s", symbol)
        return {"symbol": symbol, "status": "error", "message": "Failed to fetch profile data"}

    # 2. Store raw JSON in Azure Blob Storage
    upload_raw_json(symbol, raw_data)

    # 3. Process into text documents with metadata
    documents = process_company_data(raw_data)

    # 4. Generate embeddings and store in Chroma Cloud
    store_documents(documents)

    logger.info("✅ Ingestion complete for %s — %d documents indexed", symbol, len(documents))
    return {"symbol": symbol, "status": "success", "documents_indexed": len(documents)}


@app.function_name("IngestAll")
@app.route(route="ingest", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def ingest_all(req: func.HttpRequest) -> func.HttpResponse:
    """Ingest financial data for all configured companies."""
    logger.info("📋 Ingesting data for companies: %s", COMPANIES)

    results = []
    for symbol in COMPANIES:
        result = await _ingest_company(symbol)
        results.append(result)

    return func.HttpResponse(
        body=json.dumps({"results": results}),
        mimetype="application/json",
        status_code=200,
    )


@app.function_name("IngestCompany")
@app.route(route="ingest/{symbol}", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
async def ingest_company(req: func.HttpRequest) -> func.HttpResponse:
    """Ingest financial data for a specific company."""
    symbol = req.route_params.get("symbol", "").upper()
    if not symbol:
        return func.HttpResponse("Symbol is required", status_code=400)

    logger.info("🔍 Ingesting data for %s", symbol)
    result = await _ingest_company(symbol)

    status_code = 200 if result["status"] == "success" else 500
    return func.HttpResponse(
        body=json.dumps(result),
        mimetype="application/json",
        status_code=status_code,
    )
