"""Client for Financial Modeling Prep API (stable endpoints)."""

import logging
import aiohttp
from config import FMP_API_KEY, FMP_BASE_URL

logger = logging.getLogger(__name__)


async def _get(session: aiohttp.ClientSession, url: str) -> dict | list | None:
    async with session.get(url) as resp:
        if resp.status != 200:
            logger.warning("⚠️ FMP request failed: %s → %d (skipping)", url, resp.status)
            return None
        return await resp.json()


async def fetch_company_data(symbol: str) -> dict:
    """Fetch profile, income statement, ratios, and news for a company."""
    key = f"apikey={FMP_API_KEY}"
    async with aiohttp.ClientSession() as session:
        profile = await _get(session, f"{FMP_BASE_URL}/profile?symbol={symbol}&{key}")
        income = await _get(session, f"{FMP_BASE_URL}/income-statement?symbol={symbol}&limit=3&{key}")
        ratios = await _get(session, f"{FMP_BASE_URL}/ratios?symbol={symbol}&limit=3&{key}")
        news = await _get(session, f"{FMP_BASE_URL}/news/stock-latest?symbol={symbol}&limit=5&{key}")

    # Profile returns a list with one item in stable API
    profile_data = profile[0] if isinstance(profile, list) and profile else (profile if isinstance(profile, dict) else {})

    return {
        "symbol": symbol,
        "profile": profile_data,
        "income_statements": income or [],
        "ratios": ratios or [],
        "news": news or [],
    }
