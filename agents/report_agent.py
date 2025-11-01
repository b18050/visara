"""Report generation agent using OpenAI ChatGPT.

Generates network outage analysis reports using GPT.
"""

from typing import Any, List, Optional
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


class ReportAgent:
    def __init__(
        self,
        api_key: Optional[str],
        prompt_template: str,
        use_llm: bool = True,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        # Try to get API key from environment if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.prompt_template = prompt_template
        self.use_llm = use_llm
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize OpenAI client
        self._client = None
        if self.api_key and OpenAI is not None:
            try:
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
                self._client = None

    def _create_prompt(self, location: str, news_articles: List[dict], visualization_url: Optional[str], has_image: bool) -> str:
        """Create a prompt for GPT to generate a network outage report."""
        prompt = f"""You are a network outage analysis expert. Generate a professional 300-word report analyzing a network outage incident.

**LOCATION:** {location}
**TIME WINDOW:** Last 24 hours
"""
        
        if visualization_url:
            prompt += f"""**IODA DASHBOARD:** {visualization_url}
(Use this to reference real-time IODA data: BGP routing, active probing, internet telescope signals)

"""
        
        if has_image:
            prompt += """**VISUAL EVIDENCE:** User uploaded a network outage visualization/map showing connectivity disruptions, traffic patterns, or BGP anomalies. Analyze this image in your report.

"""
        
        if news_articles and len(news_articles) > 0:
            prompt += f"""**RECENT NEWS ARTICLES ({len(news_articles)} articles):**
"""
            for i, article in enumerate(news_articles[:5], 1):
                title = article.get("title", "Untitled")
                source = (article.get("source") or {}).get("name") or article.get("source") or "Unknown"
                description = article.get("description", "")[:150]
                prompt += f"{i}. \"{title}\" - {source}\n"
                if description:
                    prompt += f"   Summary: {description}\n"
            prompt += "\n"
        
        prompt += """**TASK:** Generate a comprehensive 300-word network outage analysis report.

**REQUIRED SECTIONS:**
1. **Executive Summary** - What happened in this location? Synthesize the image, news, and IODA data
2. **Root Cause Analysis** - List 3-4 most likely technical causes based on evidence
3. **Impact Assessment** - Who is affected? Infrastructure, businesses, citizens?
4. **Recommended Actions** - 4 specific technical steps for ISPs/engineers

**REQUIREMENTS:**
- Be specific to {location}
- Reference the uploaded image if provided
- Cite the news articles if provided
- Mention BGP routing, transit providers, or technical details from IODA
- Keep it exactly ~300 words
- Use professional technical language
- Format with clear markdown headers

Generate the report now:"""
        
        return prompt

    def generate_report(self, location: str, outage_data, news_articles, visualization_url: Optional[str] = None, image_base64: Optional[str] = None) -> str:
        """
        Generates a 300-word report using OpenAI ChatGPT.
        
        Args:
            location: Geographic location being analyzed
            outage_data: IODA outage metrics (can be None)
            news_articles: List of related news articles
            visualization_url: Link to IODA dashboard
            image_base64: User-uploaded image (PNG/JPEG)
        """
        # Check if OpenAI is available
        if not self._client:
            return self._generate_demo_report(location, news_articles, has_image=bool(image_base64))

        # Create prompt with all inputs
        prompt = self._create_prompt(
            location, 
            news_articles or [], 
            visualization_url,
            has_image=bool(image_base64)
        )

        # Use OpenAI ChatGPT
        try:
            content: Any = [{"type": "text", "text": prompt}]
            
            # Add image if provided (GPT-4 Vision models)
            if image_base64 and "gpt-4" in self.model:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                })
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert network engineer specializing in internet outage analysis and incident response."},
                    {"role": "user", "content": content},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content or "Report generation failed."
        except Exception as e:
            error_msg = str(e)
            print(f"OpenAI API error: {error_msg}")
            return f"⚠️ OpenAI API Error: {error_msg}\n\nPlease configure your OPENAI_API_KEY in configs/config.yaml or as an environment variable."
    
    def _generate_demo_report(self, location: str, news_articles: List[dict], has_image: bool) -> str:
        """Generate a simple demo report when OpenAI is not configured."""
        report = f"""📊 Network Outage Analysis Report
Location: {location}
{"🖼️  Image: Outage visualization provided" if has_image else ""}

⚠️ OpenAI API Configuration Required

This system uses GPT (ChatGPT) to generate professional 300-word network outage analysis reports.

To enable AI-powered reports:
1. Get an API key from https://platform.openai.com/api-keys
2. Add to configs/config.yaml: openai_api_key: "sk-your-key"
3. Or set environment variable: export OPENAI_API_KEY="sk-your-key"

Demo Mode Features:
✓ Real-time IODA data integration
✓ NewsAPI article aggregation  
✓ Image upload support (PNG/JPEG)
✓ GPT-4 powered analysis (when configured)

With GPT enabled, you'll receive:
• Executive summary of the outage
• Root cause analysis
• Impact assessment
• Recommended remediation steps
• Professional 300-word report

{"News articles provided: " + str(len(news_articles)) if news_articles else ""}
"""
        return report
