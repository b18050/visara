# main.py

import yaml
from datetime import datetime, timedelta
from agents.coordinator import Coordinator

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def load_prompt(prompt_path):
    with open(prompt_path, 'r') as file:
        return file.read()

def main():
    config = load_config("configs/config.yaml")
    prompt_template = load_prompt("configs/prompts/report_prompt.txt")

    coordinator = Coordinator(config, prompt_template)

    # Example parameters
    location = "Sanaa, Yemen"
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=4)

    report = coordinator.run(location, start_time, end_time)

    # Save the report
    output_path = f"outputs/reports/report_{location.replace(', ', '_')}_{end_time.strftime('%Y%m%d%H%M%S')}.txt"
    with open(output_path, 'w') as file:
        file.write(report)

    print(f"Report saved to {output_path}")

if __name__ == "__main__":
    main()
