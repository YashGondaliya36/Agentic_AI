# 🚀 How to Push to GitHub

## ⚠️ IMPORTANT: Before Pushing

**Make sure you have `.env` in `.gitignore`!** This prevents your API keys from being exposed.

Already done ✅: `.gitignore` file created

---

## 📝 Step 1: Initialize Git (If Not Already)

```bash
cd f:\Data_Science_Project\Agentic_ai
git init
```

---

## 📝 Step 2: Add All Files

```bash
# Add project_02_voice_assistant
git add project_02_voice_assistant/

# Or add everything
git add .
```

---

## 📝 Step 3: Create First Commit

```bash
git commit -m "feat: Voice Assistant with Gemini Live API and LangChain tools integration

- Real-time voice conversation
- Tavily web search integration
- Turn-based transcription
- Modular architecture (config, tools, core)
- Full async implementation
- Production-ready structure"
```

---

## 📝 Step 4: Create GitHub Repository

### Option A: Using GitHub Website
1. Go to https://github.com/new
2. Repository name: `Agentic_ai` (or `voice-assistant-gemini`)
3. Description: "Real-time voice assistant with Gemini Live API and LangChain tools"
4. Choose: **Public** or **Private**
5. **Don't** initialize with README (you already have one)
6. Click "Create repository"

### Option B: Using GitHub CLI (if installed)
```bash
gh repo create Agentic_ai --public --source=. --remote=origin
```

---

## 📝 Step 5: Connect to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/Agentic_ai.git

# Verify
git remote -v
```

---

## 📝 Step 6: Push to GitHub

```bash
# Push to main branch
git push -u origin main

# Or if default branch is master
git push -u origin master
```

---

## ✅ Verify Upload

Go to: `https://github.com/YOUR_USERNAME/Agentic_ai`

You should see:
- ✅ `project_01_customer_support/` (your RAG chatbot)
- ✅ `project_02_voice_assistant/` (your new voice assistant)
- ✅ `README.md`
- ✅ `LICENSE`
- ❌ `.env` files (NOT visible - good!)

---

## 🔒 Security Checklist

Before pushing, verify:

```bash
# Check what will be committed
git status

# Make sure .env is NOT listed
# If it is, add to .gitignore immediately!
```

**Files that SHOULD NOT appear:**
- ❌ `.env`
- ❌ Any file with API keys
- ❌ `__pycache__/`
- ❌ `.venv/` or `venv/`

---

## 📊 What Gets Pushed

### ✅ Safe to push:
- All `.py` source code
- `README.md` documentation
- `requirements.txt`
- `.env.example` (template without real keys)
- `.gitignore`
- Project structure

### ❌ NOT pushed (in .gitignore):
- `.env` (your actual API keys)
- `__pycache__/`
- Virtual environments
- Temporary files

---

## 🎯 Future Updates

After making changes:

```bash
# Check what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "fix: improved search tool error handling"

# Push
git push
```

---

## 💡 Good Commit Message Format

```bash
# Feature
git commit -m "feat: add Google Calendar integration"

# Bug fix
git commit -m "fix: resolve transcription AttributeError"

# Documentation
git commit -m "docs: update setup guide"

# Refactor
git commit -m "refactor: modularize tool manager"
```

---

## 🚨 Emergency: If You Accidentally Committed .env

```bash
# Remove from git (keeps local file)
git rm --cached .env

# Commit the removal
git commit -m "fix: remove sensitive .env file"

# Push
git push

# Regenerate API keys (they're now compromised!)
```

---

## ✅ Ready to Push!

Run these commands in order:

```bash
cd f:\Data_Science_Project\Agentic_ai
git status                    # Check files
git add .                     # Add all
git commit -m "Initial commit: RAG chatbot + Voice Assistant"
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/Agentic_ai.git
git push -u origin main
```

Done! 🎉
