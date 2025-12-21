# 📅 Google Calendar API Setup Guide

## Step 1: Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## Step 2: Get Google Calendar API Credentials

### 2.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2.2 Create a New Project (or use existing)
1. Click "Select a project" → "New Project"
2. Name: `Voice Assistant`
3. Click "Create"

### 2.3 Enable Google Calendar API
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Google Calendar API"
3. Click on it
4. Click "Enable"

### 2.4 Create OAuth Credentials
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: `Voice Assistant`
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Skip for now
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Create OAuth Client:
   - Application type: **Desktop app**
   - Name: `Voice Assistant Desktop`
   - Click "Create"

5. Download credentials:
   - Click the download icon (⬇️) next to your OAuth client
   - Save file as: `credentials.json`
   - Move to: `f:\Data_Science_Project\Agentic_ai\project_02_voice_assistant\credentials.json`

## Step 3: Add to .gitignore

Make sure these are in `.gitignore`:
```
credentials.json
token.json
*.json
```

## Step 4: First Run Authentication

When you first run the calendar tool:
1. Browser will open automatically
2. Sign in with your Google account
3. Click "Allow" to grant calendar access
4. A `token.json` file will be created
5. Future runs won't need browser login

## Step 5: Update .env

Add to `.env`:
```
GOOGLE_CALENDAR_ENABLED=true
```

## ✅ Ready!

Once you have `credentials.json`, the calendar tool will work!

## 🔒 Security Notes

**DO NOT commit to GitHub:**
- ❌ `credentials.json` (OAuth client secret)
- ❌ `token.json` (Your access token)
- ✅ Already in `.gitignore`

## 🐛 Troubleshooting

### "Access blocked" error
- Go to OAuth consent screen
- Add your email as test user
- App is in "Testing" mode (that's fine for personal use)

### "Invalid credentials" error
- Re-download `credentials.json`
- Delete `token.json` and try again

### Browser doesn't open
- Copy the URL from terminal
- Paste in browser manually
