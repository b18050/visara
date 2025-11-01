#!/usr/bin/env python3
"""Test script to verify the Visara setup is working correctly.

This script checks:
1. Python version
2. Required dependencies
3. Core module imports
4. Basic functionality
"""

import sys

print("=" * 60)
print("🔍 Visara Setup Verification")
print("=" * 60)

# 1. Check Python version
print("\n1️⃣  Checking Python version...")
py_version = sys.version_info
print(f"   Python {py_version.major}.{py_version.minor}.{py_version.micro}")

if py_version >= (3, 10):
    print("   ✅ Python 3.10+ (Full support including MCP)")
elif py_version >= (3, 9):
    print("   ✅ Python 3.9+ (Core features work, MCP requires 3.10+)")
else:
    print("   ❌ Python 3.9+ required")
    sys.exit(1)

# 2. Check dependencies
print("\n2️⃣  Checking dependencies...")
deps_ok = True

try:
    import yaml
    print("   ✅ PyYAML")
except ImportError:
    print("   ❌ PyYAML - run: pip install PyYAML")
    deps_ok = False

try:
    import openai
    print(f"   ✅ OpenAI ({openai.__version__})")
except ImportError:
    print("   ❌ OpenAI - run: pip install 'openai>=1.40.0'")
    deps_ok = False

try:
    import httpx
    print("   ✅ httpx")
except ImportError:
    print("   ❌ httpx - run: pip install httpx")
    deps_ok = False

try:
    import fastapi
    print("   ✅ FastAPI")
except ImportError:
    print("   ❌ FastAPI - run: pip install 'fastapi>=0.110'")
    deps_ok = False

try:
    import uvicorn
    print("   ✅ Uvicorn")
except ImportError:
    print("   ❌ Uvicorn - run: pip install 'uvicorn[standard]>=0.24'")
    deps_ok = False

# Check MCP (optional for Python 3.9)
if py_version >= (3, 10):
    try:
        import mcp
        print("   ✅ MCP (Model Context Protocol)")
    except ImportError:
        print("   ⚠️  MCP not installed (optional)")
        print("      To install: pip install 'mcp>=1.0.0'")
else:
    print("   ⚠️  MCP requires Python 3.10+ (skipped)")

if not deps_ok:
    print("\n❌ Missing dependencies. Install with:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# 3. Check core imports
print("\n3️⃣  Checking core modules...")
try:
    from agents.ioda_agent import IODAAgent
    from agents.news_agent import NewsAgent
    from agents.report_agent import ReportAgent
    from agents.coordinator import Coordinator
    print("   ✅ All agent modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import error: {e}")
    sys.exit(1)

# 4. Check configuration
print("\n4️⃣  Checking configuration...")
try:
    with open("configs/config.yaml", 'r') as f:
        import yaml
        config = yaml.safe_load(f)
    print("   ✅ Configuration file loaded")
    
    # Check OpenAI key
    import os
    openai_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    if openai_key and len(openai_key) > 10:
        print("   ✅ OpenAI API key configured")
    else:
        print("   ⚠️  OpenAI API key not set (offline mode only)")
        print("      Set in configs/config.yaml or export OPENAI_API_KEY")
    
    # Check NewsAPI key
    news_key = config.get("news_api_key")
    if news_key and news_key != "YOUR_NEWSAPI_KEY":
        print("   ✅ NewsAPI key configured")
    else:
        print("   ⚠️  NewsAPI key not set (news features disabled)")
        print("      Get free key: https://newsapi.org")
        
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    sys.exit(1)

# 5. Test basic functionality
print("\n5️⃣  Testing basic functionality...")
try:
    from datetime import datetime, timedelta
    
    # Test IODA agent
    ioda = IODAAgent("https://api.ioda.inetintel.cc.gatech.edu/v2")
    print("   ✅ IODA agent initialized")
    
    # Test News agent
    news = NewsAgent(None)
    print("   ✅ News agent initialized")
    
    # Test Report agent (offline mode)
    report = ReportAgent(
        api_key=None,
        prompt_template="Test {outage_data}",
        use_llm=False
    )
    print("   ✅ Report agent initialized")
    
    # Test report generation (offline)
    test_report = report.generate_report(
        outage_data={"test": "data"},
        news_articles=[],
        visualization_url="http://test.com"
    )
    if test_report and len(test_report) > 0:
        print("   ✅ Report generation works (offline mode)")
    
except Exception as e:
    print(f"   ❌ Functionality test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. Check FastAPI server
print("\n6️⃣  Checking web server...")
try:
    from server.app import app
    print(f"   ✅ FastAPI app loaded ({len(app.routes)} routes)")
except Exception as e:
    print(f"   ❌ FastAPI app error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✅ Setup verification complete!")
print("=" * 60)
print("\n📋 Next steps:")
print("   1. Run CLI:  python3 main.py")
print("   2. Run Web:  uvicorn server.app:app --reload")
print("   3. Frontend: cd web && npm install && npm run dev")

if py_version >= (3, 10):
    try:
        import mcp
        print("   4. Run MCP:  python3 mcp_server.py")
    except ImportError:
        pass

print("\n💡 Tips:")
if not (openai_key and len(openai_key) > 10):
    print("   - Add OpenAI API key for AI features")
    print("     Get key: https://platform.openai.com/api-keys")
if not (news_key and news_key != "YOUR_NEWSAPI_KEY"):
    print("   - Add NewsAPI key for news features")
    print("     Get key: https://newsapi.org (free tier available)")

print("\n📚 Documentation:")
print("   - README.md - Full documentation")
print("   - GETTING_STARTED.md - Setup guide")
print("   - BEFORE_VS_AFTER.md - See what changed")

print("\n" + "=" * 60)

