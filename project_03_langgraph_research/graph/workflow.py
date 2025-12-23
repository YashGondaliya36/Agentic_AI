"""Workflow - The LangGraph definition"""

from typing import Literal
from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from agents.researcher import research_agent
from agents.analyzer import analyzer_agent
from agents.writer import writer_agent


def create_research_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    
    This is the BRAIN - it defines how agents work together!
    
    Workflow:
    1. Research (search)
    2. Analyze (check quality)
    3. Decision: Good enough? OR Need more research?
       - If need more → Loop back to Research
       - If good → Go to Writer
    4. Writer (create summary)
    5. End
    """
    
    # Create the graph with our state type
    workflow = StateGraph(ResearchState)
    
    # ========= ADD NODES (Agents) =========
    # Each node is a function that takes state and returns updated state
    
    workflow.add_node("research", research_agent.search)
    workflow.add_node("analyze", analyzer_agent.analyze)
    workflow.add_node("write", writer_agent.write_summary)
    
    # ========= ADD EDGES (Flow Control) =========
    
    # 1. Start → Research (always start here)
    workflow.set_entry_point("research")
    
    # 2. Research → Analyze (always analyze after search)
    workflow.add_edge("research", "analyze")
    
    # 3. Analyze → Decision (conditional routing)
    # This is the KEY feature of LangGraph!
    def decide_next_step(state: ResearchState) -> Literal["research", "write"]:
        """
        Decide what to do after analysis.
        
        This function is called AFTER the analyze node.
        It looks at the state and decides the next step.
        """
        needs_more = state.get("needs_more_research", False)
        max_attempts_reached = state.get("search_attempts", 0) >= 3
        
        if needs_more and not max_attempts_reached:
            print("\n🔄 Decision: Need more research, looping back...")
            return "research"  # LOOP BACK!
        else:
            print("\n✅ Decision: Sufficient research, creating summary...")
            return "write"
    
    # Add conditional edge with our decision function
    workflow.add_conditional_edges(
        "analyze",  # From this node
        decide_next_step,  # Use this function to decide
        {
            "research": "research",  # If returns "research", go to research node
            "write": "write"  # If returns "write", go to write node
        }
    )
    
    # 4. Write → End (always end after writing)
    workflow.add_edge("write", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def visualize_workflow():
    """
    Print a text representation of the workflow.
    
    This helps you understand the graph structure!
    """
    print("\n" + "="*60)
    print("📊 LANGGRAPH WORKFLOW STRUCTURE")
    print("="*60)
    print("""
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
  Need      Good         │
  More      Enough       │
    │         │          │
    └─────────┘          │
                ↓        │
          ┌─────────┐    │
          │  WRITE  │    │
          │(Summary)│    │
          └─────────┘
                ↓
              END
    
    KEY FEATURES:
    ✅ Loop/Cycle (Research can repeat)
    ✅ Conditional routing (Decision node)
    ✅ State management (Shared memory)
    ✅ Multi-agent (3 agents collaborate)
    """)
    print("="*60 + "\n")
