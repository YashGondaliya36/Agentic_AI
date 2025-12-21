# 🚀 Quick Setup Guide

## Step 1: Install Dependencies

```bash
cd project_02_voice_assistant
pip install -r requirements.txt
```

## Step 2: Get API Keys

### Gemini API (FREE)
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### Tavily API (FREE - 1000 searches/month)
1. Go to: https://tavily.com
2. Sign up (free account)
3. Get your API key from dashboard

## Step 3: Configure Environment

```bash
# Copy the example file
cp .env.example .env

# Edit .env file and add your keys
# GEMINI_API_KEY=your_actual_key_here
# TAVILY_API_KEY=your_actual_key_here
```

## Step 4: Run the Assistant

```bash
python main.py
```

## Step 5: Test It!

### Voice Input (Recommended)
Just speak into your microphone:
- "Search for the latest AI news"
- "What's trending in machine learning?"
- "Find information about LangGraph"

### Text Input (Fallback)
Type at the prompt:
```
💬 Type message: Search for Python tutorials
```

## Expected Output

```
╔══════════════════════════════════════════════════════════════╗
║        🎙️  VOICE ASSISTANT WITH TOOL INTEGRATION             ║
╚══════════════════════════════════════════════════════════════╝

🎙️  Initializing Voice Assistant...
🔧 Initializing Tool Manager...
✅ Tool Manager ready with 1 tools
✅ Voice Assistant initialized!
📱 Model: models/gemini-2.5-flash-native-audio-preview-12-2025
🎤 Microphone: Ready
🔊 Speaker: Ready
🛠️  Tools: 1 available

🎙️  VOICE ASSISTANT IS READY!

🎤 Listening... Speak into your microphone!
```

## What Happens When You Speak?

1. **You say**: "Search for AI news"
2. **Gemini hears** your voice (native audio)
3. **Gemini decides**: "I need to use the search_web tool"
4. **Tool executes**: Tavily searches the web
5. **Results return**: Top 3 AI news articles
6. **Gemini speaks**: Summarizes the news in voice!

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created `.env` file (not `.env.example`)
- Check the key is pasted correctly (no extra spaces)

### "TAVILY_API_KEY not found"  
- Get your free key from https://tavily.com
- Add to `.env` file

### No audio input/output
- Check microphone permissions
- Restart terminal after installing pyaudio
- On Windows: May need to install portaudio

### Tool not executing
- Check internet connection
- Verify API keys are valid
- Look for error messages in console

## Next Steps

Once this works:
1. ✅ Test different search queries
2. ✅ Try complex questions
3. ✅ Add more tools (Calendar, Email)
4. ✅ Explore LangGraph for workflows

## Need Help?

Check the main README.md for detailed documentation!
