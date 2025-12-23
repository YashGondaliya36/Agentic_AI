# 🔬 LangGraph Research Assistant

A **multi-agent AI research system** built with LangGraph that demonstrates:
- ✅ Stateful workflows
- ✅ Multiple AI agents
- ✅ Conditional routing
- ✅ Loops and cycles
- ✅ Quality control

## 🎯 What It Does

This system researches any topic you give it:

1. **Research Agent** → Searches the web
2. **Analyzer Agent** → Evaluates result quality
3. **Decision Node** → Good enough? Or need more?
   - If quality < 7/10 → Loop back and search again
   - If quality ≥ 7/10 → Move to next step
4. **Writer Agent** → Creates comprehensive summary
5. **Result** → Professional report with key points

## 🏗️ Architecture

```
project_03_langgraph_research/
├── main.py                    # Entry point
├── agents/
│   ├── researcher.py          # Web search agent
│   ├── analyzer.py            # Quality checker
│   └── writer.py              # Summary generator
├── graph/
│   ├── state.py               # State definition
│   └── workflow.py            # Graph construction
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Setup

### 1. Install Dependencies

```bash
cd project_03_langgraph_research
pip install -r requirements.txt
```

### 2. Configure Environment

**This project uses the centralized `.env` file from the parent directory!**

```bash
# Go to root directory
cd ..

# Copy example file (if you haven't already)
cp .env.example .env

# Edit .env and add your API keys
# GOOGLE_API_KEY=your_key
# TAVILY_API_KEY=your_key
```

The project will automatically load `.env` from the root `Agentic_ai/` directory.

### 3. Run

```bash
cd project_03_langgraph_research
python main.py
```

## 📊 Workflow Visualization

```
    START
      ↓
┌─────────┐
│ RESEARCH│ ← Loop back if needed
│ (Search)│ ←─────────┐
└─────────┘           │
      ↓               │
┌─────────┐           │
│ ANALYZE │           │
│(Quality)│           │
└─────────┘           │
      ↓               │
[DECISION]            │
  ↙     ↘            │
Need      Good        │
More      Enough       │
  │         │          │
  └─────────┘          │
            ↓          │
      ┌─────────┐      │
      │  WRITE  │      │
      │(Summary)│      │
      └─────────┘
            ↓
          END
```

## 🎓 Learning Points

### 1. **State Management**
```python
class ResearchState(TypedDict):
    topic: str
    search_attempts: int
    search_results: list
    quality_score: float
    summary: str
    # ... State flows through entire graph
```

### 2. **Nodes (Agents)**
```python
# Each agent is a node that processes state
def search(state):
    # Do work
    state["results"] = search_web(state["topic"])
    return state  # Return updated state
```

### 3. **Conditional Routing**
```python
# Decision function
def decide_next(state):
    if state["quality_score"] < 7:
        return "research"  # Loop back
    else:
        return "write"  # Continue
        
# Add to graph
workflow.add_conditional_edges("analyze", decide_next)
```

### 4. **Loops/Cycles**
```python
# LangGraph supports cycles!
Research → Analyze → (if bad) → Research again
```

## 💡 Example Usage

```bash
$ python main.py

🎯 What would you like to research?
📝 Enter research topic: Latest AI agents developments

🚀 Starting research on: 'Latest AI agents developments'

🔍 Research Agent: Searching (Attempt 1/3)
✅ Found results!

🔬 Analyzer Agent: Evaluating results...
📊 Quality Score: 6/10 - Need more research

🔄 Decision: Need more research, looping back...

🔍 Research Agent: Searching (Attempt 2/3)
✅ Found results!

🔬 Analyzer Agent: Evaluating results...
📊 Quality Score: 8/10 - Sufficient!

✅ Decision: Sufficient research, creating summary...

✍️  Writer Agent: Creating summary...
✅ Summary created

📋 RESEARCH RESULTS
====================================
📌 Topic: Latest AI agents developments
🔍 Search Attempts: 2
⭐ Quality Score: 8/10

📄 SUMMARY
====================================
[Comprehensive summary here...]

🔑 KEY POINTS
====================================
1. Multi-agent systems are trending
2. LangGraph popularity increasing
3. Production deployments growing
...
```

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Agent** | 3 specialized agents work together |
| **Quality Control** | Automatically retries if results poor |
| **Stateful** | Maintains context across all steps |
| **Conditional** | Intelligent routing based on results |
| **Loops** | Can search multiple times if needed |
| **Production-Ready** | Error handling, logging, clean structure |

## 🔧 Customization

### Change Quality Threshold
```python
# In agents/analyzer.py
if score < 7.0:  # Change to 8.0 for stricter quality
    state["needs_more_research"] = True
```

### Change Max Search Attempts
```python
# In agents/analyzer.py
if score < 7.0 and attempts < 3:  # Change to 5 for more attempts
```

### Add More Agents
```python
# Create new agent file
# Add to workflow in graph/workflow.py
workflow.add_node("new_agent", new_agent_function)
workflow.add_edge("analyze", "new_agent")
```

## 🚀 Next Steps

1. **Add Email Agent** - Send results via email
2. **Add Database** - Store research history
3. **Add Visualization** - Show graph execution
4. **Deploy** - Make it a web service

## 📚 Learn More

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Tavily Search API](https://tavily.com/)

## ✅ Completion Checklist

- [x] Project structure created
- [x] State definition
- [x] Research agent
- [x] Analyzer agent
- [x] Writer agent
- [x] Graph workflow
- [x] Conditional routing
- [x] Loop implementation
- [ ] Install dependencies
- [ ] Configure .env
- [ ] Test run
- [ ] Understand flow

**Ready to learn LangGraph hands-on!** 🎉
