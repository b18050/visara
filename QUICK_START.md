# 🚀 Quick Start Guide

Get your demo running in 3 minutes!

## For Video Recording

### Step 1: Install Dependencies (One Time)
```bash
cd /Users/chandapr/visara

# Python packages
pip install -r requirements.txt

# Frontend packages
cd web && npm install && cd ..
```

### Step 2: Configure API Keys (One Time)
```bash
# Copy the template
cp configs/config.yaml.example configs/config.yaml

# Edit and add your keys
nano configs/config.yaml  # or open in your editor
```

Add your OpenAI API key to the file.

### Step 3: Check Everything is Ready
```bash
# Run pre-flight check
python3 check_demo_ready.py

# If all ✅, you're ready!
```

### Step 4: Start the Application
```bash
# One command to start everything
./start_web.sh
```

Wait for:
```
🎉 All systems ready!
   🌐 Open your browser to:
   👉 http://localhost:5173
```

### Step 5: Open Browser & Record!
1. Open http://localhost:5173
2. Start recording your screen
3. Follow the demo script in `VIDEO_DEMO_CHECKLIST.md`

### Step 6: Stop When Done
```bash
# Press Ctrl+C in the terminal
```

---

## For GitHub Upload

### Before Pushing
```bash
# Verify config.yaml won't be uploaded
git status | grep config.yaml

# You should see:
#   D  configs/config.yaml  (deleted from git)
# You should NOT see it as a new/modified file
```

### Push to GitHub
```bash
git add .
git commit -m "Add network outage analyzer with web UI"
git push
```

See `GITHUB_UPLOAD.md` for detailed safety instructions.

---

## Troubleshooting

### "Port already in use"
```bash
# Kill existing processes
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9

# Try again
./start_web.sh
```

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "npm: command not found"
Install Node.js from https://nodejs.org

### "Config file not found"
```bash
cp configs/config.yaml.example configs/config.yaml
# Then edit config.yaml with your API keys
```

---

## Quick Reference

| What                  | Command                     |
|-----------------------|-----------------------------|
| Start demo            | `./start_web.sh`            |
| Check if ready        | `python3 check_demo_ready.py` |
| Frontend URL          | http://localhost:5173       |
| Backend API           | http://localhost:8000       |
| API docs              | http://localhost:8000/docs  |
| Stop servers          | `Ctrl+C`                    |

---

**That's it! You're ready to record your demo! 🎬**

