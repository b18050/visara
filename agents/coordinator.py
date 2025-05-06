# agents/coordinator.py

from agents.ioda_agent import IODAAgent
from agents.news_agent import NewsAgent
from agents.report_agent import ReportAgent
from datetime import datetime, timedelta

class Coordinator:
    def __init__(self, config, prompt_template):
        self.ioda_agent = IODAAgent(config["ioda_base_url"])
        self.news_agent = NewsAgent(config["news_api_key"])
        self.report_agent = ReportAgent(config["openai_api_key"], prompt_template)

    def run(self, location, start_time, end_time):
        """
        Coordinates the workflow to generate the outage report.
        """
        outage_data = self.ioda_agent.fetch_outage_data(location, start_time, end_time)
        visualization_url = self.ioda_agent.get_visualization_url(location, start_time, end_time)
        news_articles = self.news_agent.fetch_news(location, start_time, end_time)
        report = self.report_agent.generate_report(outage_data, news_articles, visualization_url)
        return report
