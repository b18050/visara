# 🎥 Video Demo Checklist

This guide will help you prepare for recording your demo video.

## ✅ Pre-Recording Checklist

### 1. API Keys Setup
- [ ] Copy `configs/config.yaml.example` to `configs/config.yaml`
- [ ] Add your OpenAI API key (or set `OPENAI_API_KEY` environment variable)
- [ ] Add your NewsAPI key (optional, get from https://newsapi.org)
- [ ] Verify `use_llm: true` in config.yaml

### 2. Test Run (Before Recording)
```bash
# Quick test
python3 test_setup.py

# If all checks pass, you're ready!
```

### 3. Start the Application
```bash
# Simple one-command startup
./start_web.sh
```

This will:
- ✅ Start backend API on http://localhost:8000
- ✅ Start frontend UI on http://localhost:5173
- ✅ Verify both are healthy
- ✅ Show you when ready to open browser

### 4. Open Your Browser
Navigate to: **http://localhost:5173**

---

## 🎬 Demo Script (Follow this in your video)

### Part 1: Introduction (15 seconds)
"Hi! Today I'm showing you Visara, a network outage analysis system that combines real-time data, news articles, and AI to generate comprehensive outage reports."

### Part 2: Upload Image (20 seconds)
1. Click on "Outage Image" file picker
2. Select your network outage map/image (PNG or JPEG)
3. Show the preview appearing

**Say**: "First, I'll upload an image showing network outage data..."

### Part 3: Configure Location (10 seconds)
1. Enter location (e.g., "Sanaa, Yemen" or "Istanbul, Turkey")
2. Set hours lookback (e.g., 24 hours)

**Say**: "I'll set the location and time window..."

### Part 4: Fetch News (30 seconds)
1. Click "Fetch Latest News" button
2. Wait for articles to load
3. Show the articles appearing

**Say**: "Now I'll fetch recent news articles related to this location..."

### Part 5: Select Articles (20 seconds)
1. Check 2-3 relevant articles
2. Show the counter updating

**Say**: "I'll select the most relevant articles for the analysis..."

### Part 6: Generate Report (45 seconds)
1. Verify "Use LLM" is checked
2. Show model name (e.g., "gpt-4o-mini" or "phi3:mini")
3. Click "Generate Report" button
4. Wait for loading spinner
5. Show the generated report appearing in the right panel

**Say**: "Now I'll generate the AI-powered report... and here we have a comprehensive analysis combining the image, news articles, and outage data."

### Part 7: Show Report (30 seconds)
1. Scroll through the generated report
2. Highlight key sections

**Say**: "As you can see, the system has generated a detailed report with analysis of the outage, possible causes, and relevant context from the news."

### Part 8: Conclusion (15 seconds)
**Say**: "This system demonstrates integration of multiple APIs, AI/LLM capabilities, and a modern React frontend—all working together for real-time network analysis. Thanks for watching!"

---

## 📝 Demo Variations

### Quick Demo (1 minute)
Skip the narration, just show:
1. Upload image → 2. Enter location → 3. Fetch news → 4. Select articles → 5. Generate report

### Detailed Demo (3 minutes)
Add these points:
- Show the API endpoint indicator in the header
- Demonstrate the "No LLM" fallback mode
- Show multiple locations/scenarios
- Explain the architecture briefly

---

## 🐛 Troubleshooting During Recording

### Backend Not Starting?
```bash
# Check if port is in use
lsof -i :8000

# Kill and restart
pkill -f "uvicorn server.app:app"
./start_web.sh
```

### Frontend Not Loading?
```bash
# Check if port is in use
lsof -i :5173

# Reinstall dependencies
cd web
rm -rf node_modules
npm install
cd ..
./start_web.sh
```

### No News Articles Loading?
- Check your NewsAPI key in `configs/config.yaml`
- Try a different location
- Check internet connection

### Report Generation Fails?
- Verify OpenAI API key is set
- Check you have credits in your OpenAI account
- Try setting `use_llm: false` for offline demo mode

---

## 🎨 Pro Tips for Great Video

1. **Clear Browser Cache** before recording
2. **Use Incognito/Private Window** for clean browser UI
3. **Zoom Browser to 100%** for consistent sizing
4. **Close Unnecessary Browser Tabs** to avoid distractions
5. **Prepare Sample Images** beforehand (have 2-3 ready)
6. **Test Your Microphone** if recording audio
7. **Use Screen Recording Software**: QuickTime (Mac), OBS (cross-platform)
8. **Keep Video Under 3 Minutes** for best engagement

---

## 📦 After Recording

### Stopping the Application
Press `Ctrl+C` in the terminal where `start_web.sh` is running.

Or manually:
```bash
# Stop all processes
pkill -f uvicorn
pkill -f vite
```

### Uploading to GitHub (IMPORTANT!)

**Before you push**, verify your secrets are not included:

```bash
# Check what will be committed
git status

# Verify config.yaml is NOT in the list
# It should be ignored by .gitignore

# Safe to commit:
git add .
git commit -m "Add network outage analyzer with web UI"
git push
```

The `.gitignore` file ensures:
- ❌ `configs/config.yaml` (contains API keys) - **NOT uploaded**
- ❌ `.env` files - **NOT uploaded**  
- ❌ `node_modules/` - **NOT uploaded**
- ❌ Log files - **NOT uploaded**
- ✅ `configs/config.yaml.example` - **IS uploaded** (safe template)

---

## ✨ Bonus: Sample Test Data

### Good Test Locations:
- "Sanaa, Yemen" (historical outages)
- "Istanbul, Turkey" (recent events)
- "Kyiv, Ukraine" (infrastructure impacts)
- "Tehran, Iran" (network restrictions)

### Sample Images to Use:
- IODA dashboard screenshots
- Network traffic graphs
- BGP routing visualizations
- Internet connectivity heat maps

You can download examples from: https://ioda.inetintel.cc.gatech.edu

---

**Good luck with your recording! 🎉**

