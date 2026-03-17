"""Process raw financial data into text documents for embedding."""

import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500  # characters per chunk


def _make_profile_text(profile: dict) -> str:
    return (
        f"{profile.get('companyName', 'N/A')} ({profile.get('symbol', '')}) "
        f"is a {profile.get('sector', 'N/A')} company in the {profile.get('industry', 'N/A')} industry. "
        f"Market cap: ${profile.get('mktCap', 0):,.0f}. "
        f"Price: ${profile.get('price', 0):.2f}. "
        f"Beta: {profile.get('beta', 'N/A')}. "
        f"CEO: {profile.get('ceo', 'N/A')}. "
        f"Description: {profile.get('description', 'N/A')}"
    )


def _make_income_text(symbol: str, stmt: dict) -> str:
    year = stmt.get("fiscalYear", stmt.get("date", "N/A"))
    return (
        f"{symbol} Income Statement ({year}): "
        f"Revenue: ${stmt.get('revenue', 0):,.0f}. "
        f"Gross Profit: ${stmt.get('grossProfit', 0):,.0f}. "
        f"Operating Income: ${stmt.get('operatingIncome', 0):,.0f}. "
        f"Net Income: ${stmt.get('netIncome', 0):,.0f}. "
        f"EPS: {stmt.get('eps', 'N/A')}. "
        f"EBITDA: ${stmt.get('ebitda', 0):,.0f}."
    )


def _fmt(value, fmt=".2f"):
    """Safely format a numeric value, returning 'N/A' for missing/non-numeric."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):{fmt}}"
    except (ValueError, TypeError):
        return str(value)


def _make_ratios_text(symbol: str, ratio: dict) -> str:
    year = ratio.get("fiscalYear", ratio.get("date", "N/A"))
    return (
        f"{symbol} Financial Ratios ({year}): "
        f"Current Ratio: {_fmt(ratio.get('currentRatio'))}. "
        f"Debt/Equity: {_fmt(ratio.get('debtToEquityRatio'))}. "
        f"Gross Margin: {_fmt(ratio.get('grossProfitMargin'), '.2%')}. "
        f"Net Margin: {_fmt(ratio.get('netProfitMargin'), '.2%')}. "
        f"Operating Margin: {_fmt(ratio.get('operatingProfitMargin'), '.2%')}. "
        f"P/E: {_fmt(ratio.get('priceToEarningsRatio'))}."
    )


def _make_news_text(symbol: str, article: dict) -> str:
    return (
        f"{symbol} News: {article.get('title', 'N/A')}. "
        f"Published: {article.get('publishedDate', 'N/A')}. "
        f"Summary: {article.get('text', 'N/A')}"
    )


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks by character count."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks


def process_company_data(raw: dict) -> list[dict]:
    """Convert raw API data into chunked documents with metadata.

    Returns list of dicts: {"text": ..., "metadata": {"company": ..., "source_type": ..., "date": ...}}
    """
    symbol = raw["symbol"]
    documents = []

    # Profile
    if raw.get("profile"):
        text = _make_profile_text(raw["profile"])
        for chunk in chunk_text(text):
            documents.append({
                "text": chunk,
                "metadata": {"company": symbol, "source_type": "profile", "date": "current"},
            })

    # Income statements
    for stmt in raw.get("income_statements", []):
        text = _make_income_text(symbol, stmt)
        year = stmt.get("fiscalYear", stmt.get("date", "unknown"))
        for chunk in chunk_text(text):
            documents.append({
                "text": chunk,
                "metadata": {"company": symbol, "source_type": "income_statement", "date": str(year)},
            })

    # Ratios
    for ratio in raw.get("ratios", []):
        text = _make_ratios_text(symbol, ratio)
        year = ratio.get("fiscalYear", ratio.get("date", "unknown"))
        for chunk in chunk_text(text):
            documents.append({
                "text": chunk,
                "metadata": {"company": symbol, "source_type": "ratios", "date": str(year)},
            })

    # News
    for article in raw.get("news", []):
        text = _make_news_text(symbol, article)
        date = article.get("publishedDate", "unknown")
        for chunk in chunk_text(text):
            documents.append({
                "text": chunk,
                "metadata": {"company": symbol, "source_type": "news", "date": str(date)},
            })

    logger.info("📄 Processed %d documents for %s", len(documents), symbol)
    return documents
