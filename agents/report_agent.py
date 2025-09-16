"""Report generation agent with optional LLM backend.

Defaults to a local, deterministic renderer so the app works
without network access or API keys. When enabled, uses OpenAI's
chat completions-compatible client to generate a richer analysis.
"""

from typing import Any, List, Optional

try:
    # Optional dependency; only used if LLM is enabled.
    from openai import OpenAI
except Exception:  # pragma: no cover - import safety
    OpenAI = None  # type: ignore


class ReportAgent:
    def __init__(
        self,
        api_key: Optional[str],
        prompt_template: str,
        use_llm: bool = False,
        model: str = "gpt-4o-mini",
        provider: str = "none",  # options: none|openai|ollama|llama_cpp
        base_url: Optional[str] = None,
        local_model_path: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ):
        self.api_key = api_key
        self.prompt_template = prompt_template
        self.provider = (provider or "none").lower()
        self.use_llm = bool(use_llm and self.provider != "none")
        self.model = model
        self.base_url = base_url
        self.local_model_path = local_model_path
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize clients lazily/offline-safe
        self._client = None
        self._llama_cpp = None
        if self.use_llm:
            if self.provider in ("openai", "ollama") and OpenAI is not None:
                try:
                    kwargs = {}
                    if self.base_url:
                        kwargs["base_url"] = self.base_url
                    if self.api_key:
                        kwargs["api_key"] = self.api_key
                    else:
                        # Some local servers (e.g., Ollama) don't require keys
                        kwargs["api_key"] = ""
                    self._client = OpenAI(**kwargs)  # type: ignore
                except Exception:
                    self._client = None
                    self.use_llm = False
            elif self.provider == "llama_cpp":
                try:
                    from llama_cpp import Llama  # type: ignore

                    if not self.local_model_path:
                        raise RuntimeError("local_model_path is required for llama_cpp provider")
                    # Minimal, sensible defaults – callers can tune via config
                    self._llama_cpp = Llama(
                        model_path=self.local_model_path,
                        n_ctx=4096,
                        logits_all=False,
                    )
                except Exception:
                    self._llama_cpp = None
                    self.use_llm = False

    def _render_local(self, outage_data: Any, news_articles: List[dict], visualization_url: Optional[str], has_image: bool = False) -> str:
        """Render a concise, structured report locally without an LLM."""
        lines = []
        lines.append("Network Outage Report")
        lines.append("======================")
        if visualization_url:
            lines.append(f"Visualization: {visualization_url}")
        lines.append("")
        if has_image:
            lines.append("Image: An outage map/image was provided by the user.")
            lines.append("")

        lines.append("Outage Data:")
        if outage_data:
            # Keep compact; avoid huge dumps
            summary = str(outage_data)
            if len(summary) > 800:
                summary = summary[:800] + "..."
            lines.append(summary)
        else:
            lines.append("No outage data available (offline or API error).")
        lines.append("")

        lines.append("Relevant News:")
        if news_articles:
            for i, art in enumerate(news_articles[:5], start=1):
                title = art.get("title") or "Untitled"
                src = (art.get("source") or {}).get("name") or art.get("source") or "Unknown"
                url = art.get("url") or ""
                lines.append(f"{i}. {title} — {src} {url}")
        else:
            lines.append("No related articles found (offline or API error).")
        lines.append("")

        lines.append("Analysis:")
        lines.append(
            "Based on available signals and reports, an outage likely occurred in the target region. "
            "Possible causes include localized infrastructure failure, upstream transit disruptions, or intentional network restrictions. "
            "Cross-reference traffic anomalies with provider maintenance notices and incident trackers to confirm root cause."
        )
        return "\n".join(lines)

    def generate_report(self, outage_data, news_articles, visualization_url: Optional[str] = None, image_base64: Optional[str] = None) -> str:
        """
        Generates a report using either a local renderer or an LLM.
        """
        prompt = self.prompt_template.format(
            outage_data=outage_data,
            news_articles=news_articles,
            visualization_url=visualization_url or "",
            image_context=("User provided an outage image (PNG)." if image_base64 else "No image provided.")
        )

        if not self.use_llm:
            return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))

        # Provider: llama_cpp (in-process, no server)
        if self.provider == "llama_cpp" and self._llama_cpp is not None:
            try:
                result = self._llama_cpp.create_chat_completion(
                    messages=[
                        {"role": "system", "content": "You are a network outage analysis assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return result["choices"][0]["message"]["content"]
            except Exception:
                return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))

        # Provider: openai/ollama via OpenAI-compatible server
        if self._client is not None:
            try:
                content: Any = [{"type": "text", "text": prompt}]
                if image_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                    })
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a network outage analysis assistant."},
                        {"role": "user", "content": content},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content  # type: ignore[attr-defined]
            except Exception:
                return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))

        # Fallback
        return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))
