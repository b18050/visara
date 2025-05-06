# agents/news_agent.py

import requests

class NewsAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_news(self, query, from_date, to_date):
        """
        Fetches news articles related to the query within the specified date range.
        """
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "sortBy": "relevancy",
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("articles", [])
        else:
            return []
