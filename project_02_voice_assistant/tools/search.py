"""Tavily web search tool wrapper"""

import os
from dotenv import load_dotenv

# Try new import first, fallback to old if not available
try:
    from langchain_tavily import TavilySearch
    USE_NEW_API = True
except ImportError:
    from langchain_community.tools import TavilySearchResults
    USE_NEW_API = False

load_dotenv()


class SearchTool:
    """
    Wrapper for Tavily search tool
    Converts LangChain tool to async-compatible format
    """
    
    def __init__(self):
        """Initialize Tavily search tool"""
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            raise ValueError(
                "TAVILY_API_KEY not found in environment variables. "
                "Get a free key at https://tavily.com"
            )
        
        # Initialize Tavily tool (use new API if available)
        if USE_NEW_API:
            self.tavily = TavilySearch(
                max_results=3,
                api_key=api_key
            )
        else:
            # Fallback to old API
            self.tavily = TavilySearchResults(
                max_results=3,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False
            )
    
    async def search(self, query: str, max_results: int = 3) -> dict:
        """
        Perform web search
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            Dict with search results formatted for Gemini
        """
        try:
            # Execute search (Tavily tool is synchronous)
            import asyncio
            
            if USE_NEW_API:
                # New API returns string directly
                result = await asyncio.to_thread(
                    self.tavily.invoke,
                    query
                )
                # New API returns formatted string, not list
                results = result if isinstance(result, str) else str(result)
            else:
                # Old API returns list of dicts
                results = await asyncio.to_thread(
                    self.tavily.invoke,
                    {"query": query}
                )
            
            # Format results for better readability
            formatted_results = self._format_results(results, max_results)
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "count": len(results) if isinstance(results, list) else 1
            }
            
        except Exception as e:
            # Print detailed error for debugging
            import traceback
            print(f"\n⚠️  Search error details:")
            print(f"   Error: {str(e)}")
            print(f"   Type: {type(e).__name__}")
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _format_results(self, results, max_results: int) -> str:
        """
        Format search results into readable text
        
        Args:
            results: Raw results from Tavily (can be list, dict, or string)
            max_results: Max results to include
            
        Returns:
            Formatted string
        """
        if not results:
            return "No results found."
        
        # New API returns string directly (rare)
        if isinstance(results, str):
            return results
        
        # New API returns dict with 'results' key
        if isinstance(results, dict):
            # Extract the actual results array
            if 'results' in results and isinstance(results['results'], list):
                results_list = results['results']
            else:
                # If no 'results' key, just convert dict to string
                return str(results)
        elif isinstance(results, list):
            results_list = results
        else:
            return str(results)
        
        # Format the list of results
        formatted = []
        
        for i, result in enumerate(results_list[:max_results], 1):
            if isinstance(result, dict):
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', '')
                
                formatted.append(
                    f"{i}. {title}\n"
                    f"   {content}\n"
                    f"   Source: {url}\n"
                )
            else:
                formatted.append(f"{i}. {str(result)}\n")
        
        return "\n".join(formatted) if formatted else "No results found."
