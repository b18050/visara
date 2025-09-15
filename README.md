🔍 Component Overview

    agents/: Modular agents for IODA (outage signals), news, and report generation.
    configs/: YAML config and prompt templates.
    data/: Raw/processed data (optional).
    outputs/: Generated reports and visuals.
    utils/: Small helpers (config/env access).
    main.py: Orchestrates the workflow end‑to‑end.

🚀 Getting Started

- Prerequisites: Python 3.10+

- Install dependencies:
  pip install -r requirements.txt

- Configure settings:
  - Edit `configs/config.yaml` to set `ioda_base_url` and optional API keys.
  - To enable LLM output, set `use_llm: true` and configure `openai_api_key` (or export `OPENAI_API_KEY`).
  - Offline-friendly: with `use_llm: false` or missing keys, the app renders a deterministic report.

- Run the application (local renderer):
  python main.py

Web App (React + FastAPI)

- Backend (FastAPI)
  - Install Python deps:
    pip install -r requirements.txt
  - Start API server (default http://localhost:8000):
    uvicorn server.app:app --reload

- Frontend (React + Vite)
  - cd web
  - npm install
  - npm run dev  # default http://localhost:5173

- Generate a report in the UI
  - Open the Vite dev URL in your browser
  - Enter a location and hours, toggle Use LLM if desired
  - Click Generate Report; the API returns JSON with the report text

Local LLM Options

- Ollama (OpenAI-compatible server)
  - Install: https://ollama.com
  - Pull a model, e.g.:
    ollama pull llama3.1:8b
  - Configure `configs/config.yaml`:
    use_llm: true
    llm_provider: "ollama"
    llm_base_url: "http://localhost:11434/v1"
    openai_model: "llama3.1:8b"
  - Then run:
    python main.py
  - Or use the web app with the same settings via the API/UI

- llama.cpp (in-process, GGUF)
  - Download a GGUF model (e.g., Llama 3.1 8B instruct GGUF).
  - Configure `configs/config.yaml`:
    use_llm: true
    llm_provider: "llama_cpp"
    local_model_path: "/path/to/model.gguf"
    temperature: 0.2
    max_tokens: 800
  - Then run:
    python main.py
  - Or use the web app with the same settings via the API/UI

Configuration

- configs/config.yaml
  - ioda_base_url: IODA API base URL.
  - news_api_key: NewsAPI key (optional; without it, news falls back to empty).
  - openai_api_key: Optional; or provide via env var `OPENAI_API_KEY`.
  - use_llm: Enables LLM generation. If false, the app uses an offline local renderer.
  - llm_provider: one of `none`, `openai`, `ollama`, `llama_cpp`.
  - llm_base_url: OpenAI-compatible server URL (e.g., Ollama `http://localhost:11434/v1`).
  - local_model_path: GGUF path when using llama.cpp in-process.
  - openai_model: Model name for the provider (OpenAI or Ollama).
  - temperature, max_tokens: Decoding controls.
  - default_location: Seed location for the demo run.
  - default_window_hours: Lookback window for outage data.

Notes

- Network calls are best‑effort. If the environment has no network access, the app still completes with a local report and empty news/outage sections.
- Sensitive keys should be provided via environment variables in production.

Training For Your Use Case

- Data: Collect prior outage reports, annotated timelines, and links that represent good outputs for your domain. Convert to instruction format (input → desired report) or few-shot exemplars.
- Approach: Start with a strong small model (e.g., Qwen2.5‑7B‑Instruct, Llama‑3.1‑8B‑Instruct, Mistral‑7B‑Instruct). Fine‑tune with LoRA/QLoRA to keep compute low.
- Tools: LLaMA‑Factory or Axolotl for SFT (instruction fine‑tuning); TRL for preference optimization (DPO/KTO) if you have quality rankings.
- Artifacts:
  - vLLM/Transformers safetensors for high throughput servers.
  - GGUF for llama.cpp/Ollama local inference.
- Serving: 
  - vLLM for high throughput OpenAI‑compatible REST.
  - Ollama for simple local serving with model pulls and OpenAI compatibility.
  - llama.cpp in‑process for minimal dependencies.
- Evaluation: Define a rubric for correctness, specificity, citation use, and consistency. Use small held‑out sets and spot human reviews.

🧠 References

- IODA (Internet Outage Detection and Analysis)
- NewsAPI

![Dashboard Demo](image.png)
