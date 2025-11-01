# Quick Reference Guide

## 🚀 One-Command Shortcuts

### Test if everything works:
```bash
python3 test_setup.py
```

### Generate a report (CLI):
```bash
python3 main.py
```

### Start web server:
```bash
uvicorn server.app:app --reload
```

### Interactive launcher:
```bash
./run.sh
```

### View latest report:
```bash
ls -lt outputs/reports/ | head -5
cat outputs/reports/report_*.txt | tail -30
```

## 📋 Status Check Commands

### Check Python version:
```bash
python3 --version
```

### Check if dependencies are installed:
```bash
python3 -c "import openai, yaml, httpx, fastapi; print('✅ All deps OK')"
```

### Check if OpenAI key is set:
```bash
echo $OPENAI_API_KEY
# or
grep openai_api_key configs/config.yaml
```

## 🔧 Common Tasks

### Add OpenAI API Key:
```bash
# Option 1: Environment variable (temporary)
export OPENAI_API_KEY="sk-your-key-here"

# Option 2: Config file (permanent)
# Edit configs/config.yaml and set openai_api_key
```

### Install/Update Dependencies:
```bash
pip3 install -r requirements.txt --upgrade
```

### Run with AI enabled:
```bash
export OPENAI_API_KEY="sk-..."
python3 main.py
```

### Run in offline mode (no API keys needed):
```bash
python3 main.py  # Just works!
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point |
| `test_setup.py` | Verify installation |
| `run.sh` | Interactive launcher |
| `mcp_server.py` | MCP server (requires Python 3.10+) |
| `configs/config.yaml` | Main configuration |
| `requirements.txt` | Python dependencies |
| `server/app.py` | FastAPI web server |

## 🔗 Important URLs

### When server is running:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173 (after `cd web && npm run dev`)

### External Services:
- OpenAI API Keys: https://platform.openai.com/api-keys
- NewsAPI Keys: https://newsapi.org
- IODA Dashboard: https://ioda.inetintel.cc.gatech.edu

## 🐛 Troubleshooting

### "python: command not found"
Use `python3` instead of `python`

### "ModuleNotFoundError: No module named 'openai'"
Run: `pip3 install -r requirements.txt`

### "MCP requires Python 3.10+"
Your Python 3.9 works for everything except MCP. Options:
1. Skip MCP (optional feature)
2. Upgrade Python: https://www.python.org/downloads/

### "OpenAI API error"
Check your API key:
```bash
echo $OPENAI_API_KEY
```
Or run in offline mode (no key needed)

### "No report generated"
Check `outputs/reports/` directory:
```bash
ls -la outputs/reports/
```

## 📊 Feature Matrix

| Feature | Works Without API Keys? | Notes |
|---------|------------------------|-------|
| Generate Reports | ✅ Yes | Offline mode |
| Web Interface | ✅ Yes | Full UI works |
| FastAPI Server | ✅ Yes | All endpoints |
| AI-Powered Reports | ❌ Needs OpenAI key | ChatGPT integration |
| News Integration | ❌ Needs NewsAPI key | Optional |
| MCP Server | ⚠️  Needs Python 3.10+ | Optional |
| Go Gateway | ⚠️  Optional | For learning |

## 🎯 What Works Right Now

✅ **Core Features (No Setup Needed):**
- CLI report generation
- FastAPI server with 8 routes
- Offline mode (template-based reports)
- All agent modules
- Configuration loading
- Report saving to disk

⏸️ **Optional Features (Needs Setup):**
- AI-powered reports (add OpenAI key)
- News integration (add NewsAPI key)
- MCP server (upgrade to Python 3.10+)
- Web frontend (run `npm install`)
- Go gateway (optional learning)

## 💡 Quick Tips

1. **Start simple**: Run `python3 main.py` first
2. **Test setup**: Run `python3 test_setup.py` anytime
3. **Offline mode works**: Don't wait for API keys
4. **Python 3.9 is fine**: Upgrade to 3.10+ only for MCP
5. **Check docs**: `README.md` has full details

## 🎓 Learning Path

### Week 1: Get it Working
- [x] Run test_setup.py ✅ DONE
- [ ] Generate your first report
- [ ] Get OpenAI API key
- [ ] Generate AI-powered report

### Week 2: Deploy It
- [ ] Set up web frontend
- [ ] Deploy to Vercel (frontend)
- [ ] Deploy to Railway (backend)
- [ ] Take screenshots

### Week 3-4: Add Go (Optional)
- [ ] Install Go
- [ ] Run basic gateway
- [ ] Add rate limiting
- [ ] Add caching

### Month 2: Polish
- [ ] Add tests
- [ ] Improve error handling
- [ ] Write blog post
- [ ] Add to LinkedIn

## 📞 Get Help

**Something not working?**

1. Run: `python3 test_setup.py`
2. Check: `IT_WORKS.md`
3. Read: `GETTING_STARTED.md`
4. See: `README.md`

**Still stuck?**
- Check Python version: `python3 --version` (need 3.9+)
- Check dependencies: `pip3 list | grep -E "openai|fastapi|yaml"`
- Check config: `cat configs/config.yaml`

---

**Remember**: The project already works! You just saw it generate a report. Everything else is optional enhancements.

