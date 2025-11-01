#!/usr/bin/env python3
"""MCP Server for Network Outage Analysis

This server exposes IODA and news data as MCP tools that can be used by
AI assistants like Claude. It provides structured access to internet outage
data and relevant news articles.

Requirements: Python 3.10+ (required by MCP library)

Usage:
    python3 mcp_server.py
"""

import sys

# Check Python version first
if sys.version_info < (3, 10):
    print("❌ Error: MCP requires Python 3.10 or higher")
    print(f"   Current version: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("\n💡 Solutions:")
    print("   1. Install Python 3.10+: https://www.python.org/downloads/")
    print("   2. Use pyenv: 'pyenv install 3.11 && pyenv local 3.11'")
    print("   3. Or run the main app without MCP: 'python3 main.py'")
    sys.exit(1)

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Optional
import yaml

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("❌ Error: MCP library not installed")
    print("\n💡 Install with: pip install 'mcp>=1.0.0'")
    print("   (Requires Python 3.10+)")
    sys.exit(1)

from agents.ioda_agent import IODAAgent
from agents.news_agent import NewsAgent


def load_config(config_path: str = "configs/config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


# Initialize the MCP server
app = Server("outage-analyzer")

# Load config and initialize agents
config = load_config()
ioda_agent = IODAAgent(config.get("ioda_base_url"))
news_agent = NewsAgent(config.get("news_api_key"))


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="fetch_outage_data",
            description=(
                "Fetch internet outage data for a specific location and time window. "
                "Returns network connectivity signals from IODA (Internet Outage Detection and Analysis). "
                "Use this to get BGP routing, active probing, and traffic data that indicates internet disruptions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to analyze (e.g., 'Sanaa, Yemen', 'New York, USA')"
                    },
                    "window_hours": {
                        "type": "number",
                        "description": "Time window in hours to look back from now",
                        "default": 4
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="fetch_news",
            description=(
                "Fetch recent news articles related to a location and timeframe. "
                "Returns news articles that might provide context about network outages, "
                "infrastructure issues, or other relevant events in the region."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to search news for (e.g., 'Sanaa, Yemen')"
                    },
                    "window_hours": {
                        "type": "number",
                        "description": "Time window in hours to look back from now",
                        "default": 4
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_visualization_url",
            description=(
                "Get the IODA visualization URL for a specific location and time window. "
                "This URL shows interactive graphs of network connectivity metrics."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to visualize (e.g., 'Sanaa, Yemen')"
                    },
                    "window_hours": {
                        "type": "number",
                        "description": "Time window in hours to look back from now",
                        "default": 4
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="analyze_outage",
            description=(
                "Comprehensive analysis that fetches outage data, news, and visualization "
                "for a location. Returns a structured summary of all available information. "
                "Use this as a one-stop tool to gather all context for outage analysis."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "Location to analyze (e.g., 'Sanaa, Yemen')"
                    },
                    "window_hours": {
                        "type": "number",
                        "description": "Time window in hours to look back from now",
                        "default": 4
                    }
                },
                "required": ["location"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""
    
    location = arguments.get("location", "")
    window_hours = arguments.get("window_hours", 4)
    
    # Calculate time window
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=window_hours)
    
    try:
        if name == "fetch_outage_data":
            outage_data = ioda_agent.fetch_outage_data(location, start_time, end_time)
            return [TextContent(
                type="text",
                text=json.dumps(outage_data, indent=2, default=str)
            )]
        
        elif name == "fetch_news":
            news_articles = news_agent.fetch_news(location, start_time, end_time)
            return [TextContent(
                type="text",
                text=json.dumps(news_articles, indent=2, default=str)
            )]
        
        elif name == "get_visualization_url":
            viz_url = ioda_agent.get_visualization_url(location, start_time, end_time)
            return [TextContent(
                type="text",
                text=viz_url or "No visualization URL available"
            )]
        
        elif name == "analyze_outage":
            # Comprehensive analysis
            outage_data = ioda_agent.fetch_outage_data(location, start_time, end_time)
            news_articles = news_agent.fetch_news(location, start_time, end_time)
            viz_url = ioda_agent.get_visualization_url(location, start_time, end_time)
            
            analysis = {
                "location": location,
                "time_window": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": window_hours
                },
                "outage_data": outage_data,
                "news_articles": news_articles,
                "visualization_url": viz_url
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(analysis, indent=2, default=str)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

