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
                },
                {
                    "name": "create_calendar_event",
                    "description": """Create an event in Google Calendar. Use this when the user wants to:
                    - Schedule a meeting
                    - Set a reminder
                    - Create an appointment
                    - Block time on their calendar
                    Example: 'Schedule a meeting tomorrow at 3pm' or 'Create event for Dec 25 at 10am'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Event title/summary. Be descriptive."
                            },
                            "start_time": {
                                "type": "string",
                                "description": "When the event starts. Examples: 'tomorrow 3pm', 'today 2pm', '2024-12-25 10:00', 'next monday 9am'"
                            },
                            "duration_hours": {
                                "type": "integer",
                                "description": "Duration in hours (default: 1)",
                                "default": 1
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional event description/notes"
                            }
                        },
                        "required": ["title", "start_time"]
                    }
                },
                {
                    "name": "send_email",
                    "description": """Send an email via Gmail. Use this when the user wants to:
                    - Send an email to someone
                    - Email information or summaries
                    - Share details via email
                    Example: 'Email me the search results' or 'Send summary to john@example.com'""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address. If user says 'email me', use their authenticated Gmail address."
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content (plain text)"
                            }
                        },
                        "required": ["to", "subject", "body"]
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
        "search_web": "Searches the internet using Tavily API",
        "create_calendar_event": "Creates events in Google Calendar",
        "send_email": "Sends emails via Gmail"
    }
