from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Tuple

from agents.coordinator import Coordinator
from main import load_config, load_prompt


class ReportRequest(BaseModel):
    location: Optional[str] = None
    hours: Optional[int] = None
    use_llm: Optional[bool] = None
    model: Optional[str] = None


def build_coordinator(overrides: Optional[dict] = None) -> Tuple[Coordinator, dict]:
    cfg = load_config("configs/config.yaml")
    if overrides:
        cfg = {**cfg, **{k: v for k, v in overrides.items() if v is not None}}
    prompt_template = load_prompt("configs/prompts/report_prompt.txt")
    return Coordinator(cfg, prompt_template), cfg


app = FastAPI(title="Network Outage Reporter API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev-friendly; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/config")
def get_config():
    cfg = load_config("configs/config.yaml")
    return {
        "default_location": cfg.get("default_location", "Sanaa, Yemen"),
        "default_window_hours": int(cfg.get("default_window_hours", 4)),
        "llm_provider": cfg.get("llm_provider", "none"),
        "use_llm": bool(cfg.get("use_llm", False)),
        "model": cfg.get("openai_model", ""),
    }


@app.post("/report")
def create_report(req: ReportRequest):
    try:
        overrides = {}
        if req.use_llm is not None:
            overrides["use_llm"] = req.use_llm
        if req.model:
            overrides["openai_model"] = req.model

        coordinator, cfg = build_coordinator(overrides)

        location = req.location or cfg.get("default_location", "Sanaa, Yemen")
        hours = int(req.hours or cfg.get("default_window_hours", 4))
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        report = coordinator.run(location, start_time, end_time)
        return {
            "location": location,
            "hours": hours,
            "generated_at": end_time.isoformat(),
            "report": report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
