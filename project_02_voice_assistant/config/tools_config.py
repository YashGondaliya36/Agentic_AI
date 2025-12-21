"""Tool declarations for Gemini Live API"""


def get_tools_config():
    """
    Get tool declarations in Gemini format
    
    Returns:
        List of tool configurations
    """
    
    tools = [
        {
            "function_declarations": [
                {
                    "name": "search_web",
                    "description": """Search the internet for current information, news, and facts. 
                    Use this when the user asks about recent events, current information, 
                    or anything requiring up-to-date knowledge. Also use for research queries.""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query. Be specific and include relevant keywords."
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        }
    ]
    
    return tools


def get_tool_descriptions():
    """
    Get human-readable tool descriptions for logging/debugging
    
    Returns:
        Dict mapping tool names to descriptions
    """
    return {
        "search_web": "Searches the internet using Tavily API"
    }
