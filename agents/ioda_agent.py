# agents/ioda_agent.py

import requests
from datetime import datetime, timedelta

class IODAAgent:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_outage_data(self, location, start_time, end_time):
        """
        Fetches outage data from IODA API for a given location and time range.
        """
        endpoint = f"{self.base_url}/signals"
        params = {
            "location": location,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_visualization_url(self, location, start_time, end_time):
        """
        Constructs the URL for the IODA visualization.
        """
        # This is a placeholder. Replace with the actual method to get the visualization URL.
        return f"{self.base_url}/visualization?location={location}&start={start_time.isoformat()}&end={end_time.isoformat()}"
