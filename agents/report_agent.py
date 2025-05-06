# agents/report_agent.py

import openai

class ReportAgent:
    def __init__(self, api_key, prompt_template):
        openai.api_key = api_key
        self.prompt_template = prompt_template

    def generate_report(self, outage_data, news_articles, visualization_url):
        """
        Generates a report using the LLM based on outage data, news articles, and visualization.
        """
        prompt = self.prompt_template.format(
            outage_data=outage_data,
            news_articles=news_articles,
            visualization_url=visualization_url
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a network outage analysis assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
