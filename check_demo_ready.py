#!/usr/bin/env python3
"""
Pre-flight check before recording demo video.
Verifies all dependencies and configurations are ready.
"""

import sys
import os
from pathlib import Path

def check_item(name, condition, fix_hint=""):
    """Check a single item and print result."""
    if condition:
        print(f"✅ {name}")
        return True
    else:
        print(f"❌ {name}")
        if fix_hint:
            print(f"   → {fix_hint}")
        return False

def main():
    print("🎥 Video Demo Pre-Flight Check")
    print("=" * 50)
    print()
    
    all_good = True
    
    # Check Python packages
    print("📦 Python Dependencies:")
    try:
        import fastapi
        check_item("FastAPI", True)
    except ImportError:
        all_good &= check_item("FastAPI", False, "Run: pip install fastapi")
    
    try:
        import uvicorn
        check_item("Uvicorn", True)
    except ImportError:
        all_good &= check_item("Uvicorn", False, "Run: pip install uvicorn")
    
    try:
        import openai
        check_item("OpenAI SDK", True)
    except ImportError:
        all_good &= check_item("OpenAI SDK", False, "Run: pip install openai")
    
    print()
    
    # Check configuration
    print("⚙️  Configuration:")
    config_path = Path("configs/config.yaml")
    config_exists = config_path.exists()
    all_good &= check_item(
        "config.yaml exists", 
        config_exists,
        "Copy configs/config.yaml.example to configs/config.yaml"
    )
    
    if config_exists:
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        has_openai_key = bool(config.get("openai_api_key")) or bool(os.getenv("OPENAI_API_KEY"))
        check_item(
            "OpenAI API key configured", 
            has_openai_key,
            "Set openai_api_key in config.yaml or OPENAI_API_KEY env var"
        )
        
        has_news_key = bool(config.get("news_api_key") and config.get("news_api_key") != "YOUR_NEWSAPI_KEY")
        check_item(
            "NewsAPI key configured (optional)", 
            has_news_key,
            "Get free key from https://newsapi.org (optional for demo)"
        )
    
    print()
    
    # Check frontend
    print("🎨 Frontend:")
    web_exists = Path("web").exists()
    all_good &= check_item("web/ directory exists", web_exists)
    
    if web_exists:
        node_modules = Path("web/node_modules").exists()
        check_item(
            "node_modules installed",
            node_modules,
            "Run: cd web && npm install"
        )
    
    print()
    
    # Check scripts
    print("🚀 Startup Scripts:")
    start_script = Path("start_web.sh")
    all_good &= check_item("start_web.sh exists", start_script.exists())
    if start_script.exists():
        all_good &= check_item("start_web.sh is executable", os.access(start_script, os.X_OK))
    
    print()
    
    # Check ports
    print("🔌 Port Availability:")
    import socket
    
    def is_port_free(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    
    port_8000 = is_port_free(8000)
    check_item(
        "Port 8000 available (backend)",
        port_8000,
        "Kill process using port 8000: lsof -ti:8000 | xargs kill -9"
    )
    
    port_5173 = is_port_free(5173)
    check_item(
        "Port 5173 available (frontend)",
        port_5173,
        "Kill process using port 5173: lsof -ti:5173 | xargs kill -9"
    )
    
    print()
    print("=" * 50)
    
    if all_good:
        print("🎉 All systems ready! You can start recording.")
        print()
        print("Next steps:")
        print("  1. Run: ./start_web.sh")
        print("  2. Open browser: http://localhost:5173")
        print("  3. Start recording your demo!")
        print()
        print("📖 See VIDEO_DEMO_CHECKLIST.md for demo script")
        return 0
    else:
        print("⚠️  Please fix the issues above before recording.")
        print()
        print("Quick fixes:")
        print("  • Install deps: pip install -r requirements.txt")
        print("  • Setup config: cp configs/config.yaml.example configs/config.yaml")
        print("  • Install frontend: cd web && npm install")
        return 1

if __name__ == "__main__":
    sys.exit(main())

