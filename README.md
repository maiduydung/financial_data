# Financial Data Ingestion Pipeline

Azure Function App that ingests financial data from the Financial Modeling Prep API, stores raw data in Azure Blob Storage, and indexes processed documents in Chroma Cloud.

## Architecture

```mermaid
flowchart TD
    subgraph trigger["⚡ Azure Function App (Flex Consumption)"]
        A["POST /api/ingest\nPOST /api/ingest/{symbol}"]
    end

    subgraph fetch["📡 Data Fetching"]
        B[FMP API Client]
        B1[/profile?symbol=X/]
        B2[/income-statement?symbol=X/]
        B3[/ratios?symbol=X/]
        B4[/news/stock-latest?symbol=X/]
        B --> B1 & B2 & B3 & B4
    end

    subgraph store["☁️ Raw Storage"]
        C[Azure Blob Storage]
        C1["financial-raw/{SYMBOL}/raw_data.json"]
        C --> C1
    end

    subgraph process["📄 Processing"]
        D[Processor]
        D1[Convert to text documents]
        D2[Attach metadata\ncompany / source_type / date]
        D3[Chunk text ~500 chars]
        D --> D1 --> D2 --> D3
    end

    subgraph embed["🧠 Embedding & Indexing"]
        E[OpenAI Embeddings\ntext-embedding-3-small]
        F[Chroma Cloud\ncollection: financial_docs]
        E --> F
    end

    A --> B
    B --> C
    C --> D
    D --> E

    style trigger fill:#0078d4,color:#fff
    style store fill:#0078d4,color:#fff
    style embed fill:#6b21a8,color:#fff
```

## Setup

1. Copy `local.settings.json.example` to `local.settings.json` and fill in your keys
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run Locally

```bash
func start
```

## Trigger Ingestion

```bash
# Ingest all companies (AAPL, MSFT, NVDA)
curl -X POST http://localhost:7071/api/ingest

# Ingest a specific company
curl -X POST http://localhost:7071/api/ingest/AAPL
```

## Deploy to Azure (Flex Consumption)

```bash
az functionapp create \
  --resource-group <rg-name> \
  --name <app-name> \
  --storage-account <storage-name> \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --flexconsumption-location eastus \
  --subscription 7aec3ed0-7ec5-498e-9284-6f21c94def7d

func azure functionapp publish <app-name>
```
