# utils/config.py

import os
import yaml
from functools import lru_cache

try:
    from dotenv import load_dotenv  # optional
    load_dotenv()
except Exception:
    pass


def _load_config_dict() -> dict:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "configs", "config.yaml")
    if os.path.isfile(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


@lru_cache(maxsize=1)
def get_openai_api_key() -> str:
    # Prefer environment variable
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    # Fallback to config file
    config = _load_config_dict()
    key = config.get("openai_api_key")
    if key:
        return key
    raise RuntimeError("OpenAI API key not found in environment or config.yaml.")


@lru_cache(maxsize=1)
def get_geminiai_api_key() -> str:
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key
    config = _load_config_dict()
    key = config.get("gemini_api_key")
    if key:
        return key
    raise RuntimeError("Gemini API key not found in environment or config.yaml.")
