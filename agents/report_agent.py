"""Report generation agent using OpenAI ChatGPT.

Defaults to a local, deterministic renderer so the app works
without an API key. When enabled with an API key, uses OpenAI's
ChatGPT to generate a richer analysis.
"""

from typing import Any, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class ReportAgent:
    def __init__(
        self,
        api_key: Optional[str],
        prompt_template: str,
        use_llm: bool = False,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tokens: int = 800,
    ):
        self.api_key = api_key
        self.prompt_template = prompt_template
        self.use_llm = use_llm
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize OpenAI client if enabled
        self._client = None
        if self.use_llm and self.api_key and OpenAI is not None:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                self._client = None
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
        Generates a report using either a local renderer or OpenAI ChatGPT.
        """
        prompt = self.prompt_template.format(
            outage_data=outage_data,
            news_articles=news_articles,
            visualization_url=visualization_url or "",
            image_context=("User provided an outage image (PNG)." if image_base64 else "No image provided.")
        )

        # Use local renderer if LLM is disabled or client not initialized
        if not self.use_llm or self._client is None:
            return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))

        # Use OpenAI ChatGPT
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
        except Exception as e:
            print(f"OpenAI API error: {e}. Falling back to local renderer.")
            return self._render_local(outage_data, news_articles, visualization_url, has_image=bool(image_base64))
