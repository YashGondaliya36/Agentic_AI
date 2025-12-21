# 🎙️ Voice Assistant with Multi-Tool Integration

**Real-time voice assistant powered by Gemini Live API + LangChain Tools**

## 🎯 What This Does

- **Speak naturally** to the AI assistant
- **AI uses tools** to help you (search, calendar, email, etc.)
- **Responds in voice** with results
- **Multimodal**: Supports audio + video + text

## 🏗️ Architecture

```
Voice Input → Gemini Live API → Tool Detection → Execute LangChain Tool → Get Result → Voice Response
```

## 📦 Features

### Phase 1 (Current)
- ✅ Real-time audio streaming
- ✅ Tavily web search integration
- ✅ Async tool execution
- ✅ Voice responses with search results

### Phase 2 (Upcoming)
- ⏳ Google Calendar integration
- ⏳ Gmail integration
- ⏳ Multiple parallel tools
- ⏳ Conversation transcription

### Phase 3 (Future)
- ⏳ LangGraph orchestration
- ⏳ Complex multi-step workflows
- ⏳ State persistence
- ⏳ Tool chaining

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd project_02_voice_assistant
pip install -r requirements.txt
```

### 2. Set Up API Keys
```bash
cp .env.example .env
# Edit .env with your keys
```

Required keys:
- `GEMINI_API_KEY` - Get from https://makersuite.google.com/app/apikey
- `TAVILY_API_KEY` - Get from https://tavily.com (1000 searches/month free)

### 3. Run the Assistant
```bash
python main.py
```

### 4. Test It
Speak into your microphone:
- "Search for the latest AI news"
- "What's trending in machine learning?"
- "Find information about LangGraph"

## 📁 Project Structure

```
project_02_voice_assistant/
├── main.py                 # Main entry point
├── config/
│   ├── __init__.py
│   ├── gemini_config.py    # Gemini Live configuration
│   └── tools_config.py     # Tool declarations
├── tools/
│   ├── __init__.py
│   ├── manager.py          # Tool manager & executor
│   └── search.py           # Tavily search wrapper
├── core/
│   ├── __init__.py
│   └── assistant.py        # Main assistant logic
├── utils/
│   ├── __init__.py
│   └── audio.py            # Audio utilities
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ How It Works

### 1. Tool Configuration
Tools are defined in `config/tools_config.py` using Gemini's function declaration format.

### 2. Tool Execution
When Gemini detects it needs a tool:
1. Sends `tool_call` event
2. `ToolManager` identifies the LangChain tool
3. Tool executes asynchronously
4. Result sent back to Gemini
5. Gemini speaks the answer

### 3. Async Architecture
All components run concurrently:
- Audio input (microphone)
- Audio output (speaker)
- Tool execution
- Gemini communication

## 📊 Performance

- **Latency**: <3s end-to-end (voice → tool → voice)
- **Concurrency**: Multiple simultaneous tasks
- **Tool execution**: Non-blocking

## 🔑 API Keys

### Gemini API (FREE)
- 60 requests/minute free tier
- Get key: https://makersuite.google.com/app/apikey

### Tavily Search (FREE)
- 1000 searches/month free
- Get key: https://tavily.com

## 💡 Usage Examples

### Example 1: Simple Search
```
You: "Search for Python tutorials"
AI: "I found several Python tutorials..."
```

### Example 2: Current Events
```
You: "What's happening in AI today?"
AI: [Uses Tavily] "Here are today's top AI stories..."
```

### Example 3: Research
```
You: "Find information about Gemini 2.5"
AI: [Searches] "Gemini 2.5 Flash is Google's latest..."
```

## 🎓 Learning Outcomes

Building this project teaches:
- Async Python programming
- WebSocket real-time communication
- LangChain tool integration
- Gemini Live API
- Voice-first application design

## 🚧 Troubleshooting

### No audio input
- Check microphone permissions
- Verify default audio device

### Tool not executing
- Check API keys in `.env`
- Verify internet connection
- Check console for errors

### Slow responses
- Normal for first request (model initialization)
- Subsequent requests should be <3s

## 📈 Next Steps

1. **Add more tools**: Calendar, Email, Weather
2. **Enable transcription**: See conversation text
3. **Add LangGraph**: Complex workflows
4. **Build UI**: Web interface (optional)

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new tools
- Improve error handling
- Optimize performance
- Share your improvements!

## 📄 License

MIT License - Use freely for learning and projects

---

**Built with ❤️ using Gemini Live API + LangChain**
