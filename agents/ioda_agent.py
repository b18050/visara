"""IODA (Internet Outage Detection and Analysis) API agent.

This agent is resilient to offline environments and API failures,
returning None/empty data when requests cannot be completed.
"""

from typing import Any, Dict, Optional
import base64
from datetime import datetime

try:
    import httpx
except Exception:  # pragma: no cover - import safety
    httpx = None  # type: ignore


class IODAAgent:
    def __init__(self, base_url: Optional[str]):
        self.base_url = base_url or "https://api.ioda.inetintel.cc.gatech.edu/v2"

    def fetch_outage_data(self, location: str, start_time: datetime, end_time: datetime) -> Optional[Dict[str, Any]]:
        """Fetch outage data from IODA for a given location and time range.

        Returns None if the request cannot be completed.
        """
        if httpx is None:
            return None

        endpoint = f"{self.base_url}/signals"
        params = {
            "location": location,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(endpoint, params=params)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            return None
        return None

    def get_visualization_url(self, location: str, start_time: datetime, end_time: datetime) -> str:
        """Construct a best-effort visualization URL for IODA UI."""
        return (
            f"{self.base_url}/visualization?location={location}"
            f"&start={start_time.isoformat()}&end={end_time.isoformat()}"
        )

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
