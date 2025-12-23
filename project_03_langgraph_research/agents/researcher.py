"""Research Agent - Searches for information"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load .env from parent directory (root of Agentic_ai)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Import Tavily search tool
try:
    from langchain_tavily import TavilySearch
    USE_NEW_API = True
except ImportError:
    from langchain_community.tools import TavilySearchResults
    USE_NEW_API = False


class ResearchAgent:
    """
    Agent responsible for searching the web for information.
    
    This is a NODE in the graph.
    """
    
    def __init__(self):
        """Initialize the search tool"""
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        if not tavily_api_key:
            raise ValueError("TAVILY_API_KEY not found in environment")
        
        if USE_NEW_API:
            self.search_tool = TavilySearch(api_key=tavily_api_key)
        else:
            self.search_tool = TavilySearchResults(api_key=tavily_api_key)
    
    def search(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for information on the topic.
        
        This function:
        1. Takes current state
        2. Performs search
        3. Updates state with results
        4. Returns updated state
        """
        topic = state["topic"]
        search_attempts = state["search_attempts"]
        
        print(f"\n🔍 Research Agent: Searching for '{topic}' (Attempt {search_attempts + 1}/3)")
        
        try:
            # Perform search
            if USE_NEW_API:
                results = self.search_tool.invoke(topic)
            else:
                results = self.search_tool.invoke({"query": topic})
            
            # Update state
            state["search_results"].append({
                "attempt": search_attempts + 1,
                "results": results
            })
            state["search_attempts"] += 1
            
            print(f"✅ Found results!")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            state["error"] = str(e)
        
        return state


# Create global instance
research_agent = ResearchAgent()
