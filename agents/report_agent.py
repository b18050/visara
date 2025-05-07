# agents/report_agent.py

from openai import OpenAI
from utils.config import get_openai_api_key, get_geminiai_api_key


# client = OpenAI(api_key=get_api_key())
client = OpenAI(
    api_key=get_geminiai_api_key(),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class ReportAgent:
    def __init__(self, api_key, prompt_template):
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
        # response = client.chat.completions.create(model="gpt-4.1",
        # messages=[
        #     {"role": "system", "content": "You are a network outage analysis assistant."},
        #     {"role": "user", "content": prompt}
        # ])
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": "You are a network outage analysis assistant."},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ]
        )
        return response.choices[0].message.content