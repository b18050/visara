# main.py

import os
from pathlib import Path
import yaml
from datetime import datetime, timedelta
from agents.coordinator import Coordinator

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_config(config_path):
    """Load config from YAML and override with environment variables."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Override with environment variables if they exist
    if os.getenv("OPENAI_API_KEY"):
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("NEWSAPI_KEY"):
        config["news_api_key"] = os.getenv("NEWSAPI_KEY")
    
    return config

def load_prompt(prompt_path):
    with open(prompt_path, 'r') as file:
        return file.read()

def main():
    config = load_config("configs/config.yaml")
    prompt_template = load_prompt("configs/prompts/report_prompt.txt")

    coordinator = Coordinator(config, prompt_template)

    # Example parameters (could be parameterized later)
    location = config.get("default_location", "Sanaa, Yemen")
    window_hours = int(config.get("default_window_hours", 4))
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=window_hours)

    report = coordinator.run(location, start_time, end_time)

    # Ensure output directory exists and save the report
    out_dir = Path("outputs/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"report_{location.replace(', ', '_')}_{end_time.strftime('%Y%m%d%H%M%S')}.txt"
    output_path = out_dir / filename
    with open(output_path, 'w') as file:
        file.write(report)

    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    main()
