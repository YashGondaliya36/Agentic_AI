# 🔬 Agentic AI Projects

A collection of production-ready AI projects demonstrating different architectures and use cases.

## 📁 Projects

### 1️⃣ **Customer Support Chatbot** (`project_01_customer_support/`)
- **Tech**: RAG (Retrieval-Augmented Generation) with Pinecone
- **Features**: Document embeddings, semantic search, context-aware responses
- **Use Case**: Customer support automation

### 2️⃣ **Voice Assistant** (`project_02_voice_assistant/`)
- **Tech**: Gemini Live API, LangChain Tools
- **Features**: Real-time voice, multi-tool integration (Search, Calendar, Gmail)
- **Use Case**: Voice-controlled productivity assistant

### 3️⃣ **LangGraph Research Assistant** (`project_03_langgraph_research/`)
- **Tech**: LangGraph, Multi-agent workflows
- **Features**: State graphs, conditional routing, loops, quality control
- **Use Case**: Automated research and reporting

### 4️⃣ **Smart Email Assistant** (`project_04_smart_email_assistant/`)
- **Tech**: LangGraph, Human-in-the-Loop, Gmail API
- **Features**: Email classification, AI draft generation, human approval, auto-responses
- **Use Case**: Automated email management with human oversight

### 5️⃣ **InvoiceIQ - AI Invoice Processor** (`project_05_invoice_processor/`)
- **Tech**: FastAPI, Gemini Vision AI, SQLite
- **Features**: Purchase/Sales invoicing, stock management, profit tracking, analytics dashboard
- **Use Case**: Complete invoice management system for hardware distributors

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/YashGondaliya36/Agentic_ai.git
cd Agentic_ai
```

### 2. Setup Environment

**Create centralized `.env` file:**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API keys
```

**Required API Keys:**
- `GOOGLE_API_KEY` - For Gemini AI (all projects)
- `TAVILY_API_KEY` - For web search (projects 2 & 3)
- `PINECONE_API_KEY` - For vector database (project 1 only)

### 3. Run Any Project

**Project 1: Customer Support**
```bash
cd project_01_customer_support
pip install -r requirements.txt
python main.py
```

**Project 2: Voice Assistant**
```bash
cd project_02_voice_assistant
pip install -r requirements.txt
python main.py
```

**Project 3: LangGraph Research**
```bash
cd project_03_langgraph_research
pip install -r requirements.txt
python main.py
```

**Project 4: Smart Email Assistant**
```bash
cd project_04_smart_email_assistant
pip install -r requirements.txt
python main.py
```

**Project 5: InvoiceIQ (Invoice Processor)**
```bash
cd project_05_invoice_processor
pip install -r requirements.txt
python app.py
# Open browser at http://localhost:8000
```

---

## 🎓 What You'll Learn

| Project | Key Concepts |
|---------|-------------|
| **Project 1** | RAG, Vector embeddings, Pinecone, Semantic search |
| **Project 2** | Gemini Live API, OAuth, Tool calling, Voice I/O |
| **Project 3** | LangGraph, State graphs, Multi-agent, Conditional routing |
| **Project 4** | Human-in-the-Loop, Email automation, LangGraph interrupts, Gmail API |
| **Project 5** | FastAPI, Gemini Vision, OCR, Database design, Business analytics |

---

## 🏗️ Architecture Overview

### Project 1: RAG Pipeline
```
Documents → Embeddings → Pinecone → Query → Retrieve → Generate
```

### Project 2: Voice Assistant
```
Voice Input → Gemini Live → Tool Calling → (Search/Calendar/Gmail) → Voice Output
```

### Project 3: LangGraph Workflow
```
Research → Analyze → Decision (Loop/Continue) → Write → Result
```

### Project 4: Email Automation
```
Email → Classify → Need Reply? → Generate Draft → 👤 Human Approval → Send
```

### Project 5: Invoice Processing
```
Invoice → AI Extract → Match Items → Calculate Profit → Save → Update Stock
```

---

## 📊 Comparison

| Feature | Project 1 | Project 2 | Project 3 | Project 4 | Project 5 |
|---------|-----------|-----------|-----------|-----------|-----------|
| **Type** | RAG Chatbot | Voice Assistant | Research System | Email Assistant | Invoice System |
| **LLM** | Gemini Flash | Gemini Live | Gemini Flash | Gemini Flash | Gemini 2.5 Flash |
| **State** | Conversation | Tool calls | Complex graph | Human-in-Loop | Database |
| **I/O** | Text | Voice + Text | Text | Email | Web UI |
| **Tools** | Vector DB | 3 tools | 3 agents | Gmail API | FastAPI + SQLite |
| **Complexity** | Medium | Medium | High | High | High |
| **UI** | CLI | CLI | CLI | CLI | Web Dashboard |

---

## 🔧 Configuration

All projects use the **centralized `.env`** file at the root level.

```
Agentic_ai/
├── .env                             ← Single config file
├── .env.example                     ← Template
├── project_01_customer_support/
├── project_02_voice_assistant/
├── project_03_langgraph_research/
├── project_04_smart_email_assistant/
└── project_05_invoice_processor/
```

**Benefits:**
- ✅ Single source of truth
- ✅ No duplicate config
- ✅ Easy to manage API keys
- ✅ Consistent across projects

---

## 🎯 Use Cases

### **Customer Support** (Project 1)
- Knowledge base search
- Automated support responses
- Document Q&A
- FAQ automation

### **Voice Assistant** (Project 2)
- Voice-controlled scheduling
- Email automation
- Web research
- Productivity workflows

### **Research Assistant** (Project 3)
- Automated research
- Quality-controlled information gathering
- Report generation
- Multi-source analysis

### **Email Assistant** (Project 4)
- Auto-classify emails by priority
- Generate professional responses
- Human-in-the-loop approval
- Customer support automation
- Sales lead follow-ups

### **Invoice Processor** (Project 5)
- Automated invoice data extraction
- Stock management (IN/OUT)
- Real-time profit tracking
- Business analytics dashboard
- Supplier & customer management

---

## 🚀 Next Steps

1. **Get API Keys**
   - Google Gemini: https://ai.google.dev/
   - Tavily Search: https://tavily.com/
   - Pinecone: https://www.pinecone.io/

2. **Setup `.env`**
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

3. **Choose a Project**
   - **Beginners**: Start with Project 3 (simplest setup)
   - **Web UI Fans**: Try Project 5 (beautiful dashboard)
   - **Voice AI**: Explore Project 2 (most impressive)
   - **Email Automation**: Check out Project 4 (practical HITL)
   - **Advanced**: Project 1 (requires Pinecone setup)

4. **Experiment & Learn**
   - Modify agents
   - Add new tools
   - Combine projects

---

## 📚 Documentation

Each project has detailed README:
- [Project 1 README](project_01_customer_support/README.md)
- [Project 2 README](project_02_voice_assistant/README.md)
- [Project 3 README](project_03_langgraph_research/README.md)
- [Project 4 README](project_04_smart_email_assistant/README.md)
- [Project 5 README](project_05_invoice_processor/README.md)

---

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest improvements
- Add new features
- Share your implementations

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

---

## 🎉 Achievements

You've built:
- ✅ RAG system with vector embeddings
- ✅ Real-time voice AI assistant
- ✅ Multi-agent workflow system
- ✅ OAuth integration
- ✅ Tool orchestration
- ✅ State management
- ✅ Production-ready architecture
- ✅ Human-in-the-loop email automation
- ✅ AI-powered invoice processing
- ✅ Complete business management system
- ✅ FastAPI web application
- ✅ Computer vision with Gemini Vision
- ✅ Database design & analytics

**Congratulations! 🎓**

---

Made with ❤️ using Google Gemini, LangChain, and LangGraph