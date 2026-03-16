import os
import json
import dotenv

# Load from local.settings.json first (Azure Functions convention)
try:
    with open(os.path.join(os.path.dirname(__file__), "local.settings.json")) as f:
        settings = json.load(f)
        local_settings = settings.get("Values", {})
except (FileNotFoundError, json.JSONDecodeError):
    local_settings = {}

dotenv.load_dotenv()


def get_config(key, default=None):
    return local_settings.get(key) or os.getenv(key) or default


# Financial Modeling Prep
FMP_API_KEY = get_config("FMP_API_KEY")
FMP_BASE_URL = "https://financialmodelingprep.com/stable"

# Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = get_config("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_RAW = get_config("BLOB_CONTAINER_RAW", "financial-raw")

# OpenAI (for embeddings)
OPENAI_API_KEY = get_config("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

# Chroma Cloud
CHROMA_API_KEY = get_config("CHROMA_API_KEY")
CHROMA_TENANT = get_config("CHROMA_TENANT")
CHROMA_DATABASE = get_config("CHROMA_DATABASE")
CHROMA_COLLECTION = get_config("CHROMA_COLLECTION", "financial_docs")

# Target companies
COMPANIES = ["AAPL", "MSFT", "NVDA"]
