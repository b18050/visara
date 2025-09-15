"""News aggregation agent using NewsAPI-compatible endpoint.

Gracefully returns an empty list on failure or offline mode.
"""

from datetime import datetime
from typing import List, Dict

try:
    import httpx
except Exception:  # pragma: no cover - import safety
    httpx = None  # type: ignore


class NewsAgent:
    def __init__(self, api_key: "str | None"):
        # Keep runtime compatible with Python 3.9 by avoiding PEP 604 syntax at runtime
        self.api_key = api_key or ""

    def fetch_news(self, query: str, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Fetch news articles related to the query within the specified date range."""
        if not self.api_key or httpx is None:
            return []

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "sortBy": "relevancy",
            "apiKey": self.api_key,
            "language": "en",
            "pageSize": 10,
        }
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    return resp.json().get("articles", [])
        except Exception:
            return []
        return []
