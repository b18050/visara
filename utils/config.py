# utils/config.py

import os
import yaml
from functools import lru_cache

@lru_cache(maxsize=1)
def get_openai_api_key():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "configs", "config.yaml")

    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            print(config)
            if config and "openai_api_key" in config:
                return config["openai_api_key"]

    raise RuntimeError("OpenAI API key not found in config.yaml.")

@lru_cache(maxsize=1)
def get_geminiai_api_key():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "configs", "config.yaml")

    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            print(config)
            if config and "gemini_api_key" in config:
                return config["gemini_api_key"]

    raise RuntimeError("Gemini API key not found in config.yaml.")
