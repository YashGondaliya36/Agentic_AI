"""State definition for the research workflow"""

from typing import TypedDict, List, Annotated, Optional
from operator import add


class ResearchState(TypedDict):
    """
    The shared state that flows through the entire graph.
    
    Think of this as the "notebook" that all agents read and write to.
    """
    
    # User input
    topic: str  # What to research
    
    # Research phase
    search_attempts: int  # How many times we've searched
    search_results: Annotated[List[dict], add]  # All search results (accumulate)
    
    # Analysis phase
    quality_score: float  # 0-10 rating of result quality
    needs_more_research: bool  # Should we search again?
    
    # Writing phase
    summary: str  # Final summary
    key_points: List[str]  # Main findings
    
    # Metadata
    next_action: str  # What to do next
    error: Optional[str]  # Any errors that occurred


def create_initial_state(topic: str) -> ResearchState:
    """Create the starting state for a new research task"""
    return {
        "topic": topic,
        "search_attempts": 0,
        "search_results": [],
        "quality_score": 0.0,
        "needs_more_research": True,
        "summary": "",
        "key_points": [],
        "next_action": "search",
        "error": None
    }
