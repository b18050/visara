# 🚀 Uploading to GitHub - Safety Guide

This guide ensures you don't accidentally upload your API keys to GitHub.

## ✅ What's Protected

The `.gitignore` file prevents these sensitive files from being uploaded:

### 🔒 Never Uploaded (Safe):
- ✅ `configs/config.yaml` - Contains your API keys
- ✅ `.env` files - Environment variables
- ✅ `.python-version` - Local Python config
- ✅ `outputs/` - Generated reports (may contain sensitive data)
- ✅ `*.log` files - May contain API responses
- ✅ `node_modules/` - Dependencies (huge, auto-downloaded)
- ✅ `__pycache__/` - Python bytecode

### 📤 Uploaded (Safe Templates):
- ✅ `configs/config.yaml.example` - Template without keys
- ✅ All source code files
- ✅ Documentation files
- ✅ Requirements.txt, package.json

---

## 🔍 Pre-Upload Verification

Before pushing to GitHub, run these checks:

### 1. Verify Your Secrets Are Protected
```bash
cd /Users/chandapr/visara

# This should show NO results (config.yaml is ignored)
git status | grep "config.yaml"

# If you see "config.yaml", DON'T PUSH! It means .gitignore isn't working.
```

### 2. Check What Will Be Committed
```bash
# See all files that will be uploaded
git status

# Make sure you DON'T see:
#   - configs/config.yaml (should be deleted/ignored)
#   - Any files with API keys
#   - .env files
```

### 3. Double-Check Sensitive Files
```bash
# These commands should return "ignored" or "not in git"
git check-ignore configs/config.yaml  # Should say: configs/config.yaml
```

---

## 📝 Step-by-Step Upload Process

### Step 1: Stage Your Changes
```bash
cd /Users/chandapr/visara

# Add all safe files
git add .

# Review what will be committed
git status
```

### Step 2: Commit Your Changes
```bash
git commit -m "Add network outage analyzer with web UI and video demo support"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `network-outage-analyzer` (or your choice)
3. Description: "AI-powered network outage analysis system with React UI"
4. Choose "Public" (for your portfolio) or "Private"
5. **DON'T** initialize with README (you already have one)
6. Click "Create repository"

### Step 4: Push to GitHub
```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/network-outage-analyzer.git

# Push your code
git push -u origin main

# If you're on 'master' branch instead:
git push -u origin master
```

---

## ⚠️ IMPORTANT: Final Safety Check

After pushing, immediately check your GitHub repository:

### What to Verify:
1. Visit: `https://github.com/YOUR_USERNAME/network-outage-analyzer`
2. Navigate to `configs/` folder
3. **Verify you see**: `config.yaml.example` ✅
4. **Verify you DON'T see**: `config.yaml` ❌

If you accidentally see `config.yaml`:
```bash
# IMMEDIATELY delete it from the repo:
git rm configs/config.yaml
git commit -m "Remove sensitive config file"
git push

# Then rotate (change) your API keys:
# - OpenAI: https://platform.openai.com/api-keys
# - NewsAPI: https://newsapi.org/account
```

---

## 🎯 What Your GitHub Repo Should Look Like

```
network-outage-analyzer/
├── README.md                    ✅ Safe (no keys)
├── requirements.txt             ✅ Safe
├── main.py                      ✅ Safe
├── start_web.sh                 ✅ Safe
├── VIDEO_DEMO_CHECKLIST.md      ✅ Safe
├── agents/                      ✅ Safe (source code)
├── configs/
│   ├── config.yaml.example      ✅ Safe (template only)
│   └── prompts/                 ✅ Safe
├── server/                      ✅ Safe
├── web/                         ✅ Safe (no node_modules)
└── utils/                       ✅ Safe

NOT in repo (gitignored):
├── configs/config.yaml          🔒 Protected
├── outputs/                     🔒 Protected
├── node_modules/                🔒 Protected
└── *.log                        🔒 Protected
```

---

## 📖 Setting Up for Others

After uploading, others can set up your project:

### Their Setup Steps:
```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/network-outage-analyzer.git
cd network-outage-analyzer

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Copy config template
cp configs/config.yaml.example configs/config.yaml

# 4. Edit config.yaml and add their own API keys
nano configs/config.yaml  # or use any editor

# 5. Install frontend dependencies
cd web && npm install && cd ..

# 6. Run the demo
./start_web.sh
```

---

## 🌟 Bonus: Make Your Repo Look Professional

### Add These Badges to README.md (Top):
```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)
![React](https://img.shields.io/badge/React-18.3+-61DAFB.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

### Add Topics to Your GitHub Repo:
- `network-analysis`
- `outage-detection`
- `openai`
- `chatgpt`
- `fastapi`
- `react`
- `typescript`
- `artificial-intelligence`
- `data-analysis`

### Pin This Repo to Your Profile:
1. Go to your GitHub profile
2. Click "Customize your pins"
3. Select this repository
4. Add it to your pinned repos

---

## 🎥 Add Your Demo Video

After recording your video:

### Option 1: Upload to YouTube
1. Upload video to YouTube
2. Add link to README.md:
```markdown
## 🎥 Demo Video

[![Watch Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
```

### Option 2: Add to GitHub
1. Create `demo.gif` (use tool like Gifox, LICEcap)
2. Add to repo:
```bash
git add demo.gif
git commit -m "Add demo GIF"
git push
```
3. Update README.md:
```markdown
![Demo](demo.gif)
```

---

## ✅ Final Checklist

Before considering your upload complete:

- [ ] Pushed to GitHub successfully
- [ ] Verified `config.yaml` is NOT visible on GitHub
- [ ] Verified `config.yaml.example` IS visible on GitHub
- [ ] README.md looks good on GitHub
- [ ] Repository is public (if you want it in your portfolio)
- [ ] Added relevant topics/tags to repo
- [ ] Tested that `git clone` → setup works
- [ ] (Optional) Added demo video/GIF
- [ ] (Optional) Pinned repo to your profile

---

## 🆘 Troubleshooting

### "I accidentally pushed my API key!"

**Don't panic. Act fast:**

1. **Revoke/rotate your API keys immediately:**
   - OpenAI: https://platform.openai.com/api-keys → Revoke → Create new
   - NewsAPI: https://newsapi.org/account → Delete → Create new

2. **Remove from git history:**
```bash
# Remove the sensitive commit
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch configs/config.yaml" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (overwrites GitHub history)
git push origin --force --all
```

3. **Or: Delete and recreate the repository**
   - Delete repo on GitHub
   - Create new repo
   - Push again (after fixing .gitignore)

### "Git says my repo is too large"

Large files to remove:
```bash
# Remove node_modules if accidentally committed
git rm -r --cached web/node_modules
git commit -m "Remove node_modules"

# Remove output files if accidentally committed  
git rm -r --cached outputs
git commit -m "Remove outputs"
```

---

**Your code is now safely on GitHub! 🎉**

Remember: Never commit API keys, always use `.gitignore`, and verify before pushing!

