"""Tool Manager - Handles tool execution and mapping"""

from google.genai import types
from .search import SearchTool
from .calendar import CalendarTool


class ToolManager:
    """
    Manages tool execution for Gemini Live API
    
    Responsibilities:
    - Map function names to implementations
    - Execute tools asynchronously
    - Format responses for Gemini
    - Handle errors
    """
    
    def __init__(self):
        """Initialize tool manager with available tools"""
        
        print("🔧 Initializing Tool Manager...")
        
        # Initialize all tools
        self.search_tool = SearchTool()
        
        # Initialize Calendar tool (may require OAuth)
        try:
            self.calendar_tool = CalendarTool()
            calendar_available = True
        except FileNotFoundError as e:
            print(f"⚠️  Calendar tool not available: {e}")
            print("   Follow GOOGLE_CALENDAR_SETUP.md to enable it.")
            self.calendar_tool = None
            calendar_available = False
        
        # Map function names to methods
        self.tool_map = {
            "search_web": self._execute_search
        }
        
        if calendar_available:
            self.tool_map["create_calendar_event"] = self._execute_calendar
        
        print(f"✅ Tool Manager ready with {len(self.tool_map)} tools")
    
    async def execute_tool_calls(self, tool_call) -> list:
        """
        Execute tool calls from Gemini
        
        Args:
            tool_call: ToolCall object from Gemini Live API
            
        Returns:
            List of FunctionResponse objects
        """
        function_responses = []
        
        # Gemini can request multiple tools in one turn
        for fc in tool_call.function_calls:
            print(f"\n🛠️  Executing tool: {fc.name}")
            print(f"📝 Arguments: {fc.args}")
            
            try:
                # Execute the tool
                result = await self._execute_tool(fc.name, fc.args)
                
                # Create response for Gemini
                function_response = types.FunctionResponse(
                    id=fc.id,
                    name=fc.name,
                    response={"result": result}
                )
                
                function_responses.append(function_response)
                
                # 🐛 DEBUG: Show what we're sending to Gemini
                print(f"\n📤 Sending to Gemini:")
                print(f"   Tool: {fc.name}")
                print(f"   Result Length: {len(str(result))} chars")
                print(f"   Preview: {str(result)[:200]}...")
                
                print(f"✅ Tool {fc.name} completed successfully\n")
                
            except Exception as e:
                print(f"❌ Tool {fc.name} failed: {str(e)}")
                
                # Send error response to Gemini
                error_response = types.FunctionResponse(
                    id=fc.id,
                    name=fc.name,
                    response={
                        "error": str(e),
                        "success": False
                    }
                )
                function_responses.append(error_response)
        
        return function_responses
    
    async def _execute_tool(self, tool_name: str, args: dict):
        """
        Execute a specific tool
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments dict
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Get the tool method
        tool_method = self.tool_map[tool_name]
        
        # Execute with args
        result = await tool_method(**args)
        
        return result
    
    async def _execute_search(self, query: str, max_results: int = 2) -> str:
        """
        Execute web search
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            Search results as formatted string
        """
        print(f"\n🔍 Searching Tavily for: '{query}'")
        
        result = await self.search_tool.search(query, max_results)
        
        # 🐛 DEBUG: Print what Tavily returned
        print(f"\n📊 Tavily Response:")
        print(f"   Success: {result.get('success')}")
        print(f"   Query: {result.get('query')}")
        print(f"   Count: {result.get('count')}")
        
        if result["success"]:
            results_text = result["results"]
            print(f"\n📄 Search Results ({len(results_text)} chars):")
            print("─" * 60)
            print(results_text[:500] + "..." if len(results_text) > 500 else results_text)
            print("─" * 60)
            
            return results_text
        else:
            error_msg = f"Search failed: {result.get('error', 'Unknown error')}"
            print(f"\n❌ {error_msg}")
            return error_msg
    
    async def _execute_calendar(
        self,
        title: str,
        start_time: str,
        duration_hours: int = 1,
        description: str = None
    ) -> str:
        """
        Execute calendar event creation
        
        Args:
            title: Event title
            start_time: Start time string
            duration_hours: Duration in hours
            description: Optional description
            
        Returns:
            Success/failure message
        """
        if not self.calendar_tool:
            return "Calendar tool not available. Please set up Google Calendar API."
        
        print(f"\n📅 Creating calendar event: '{title}'")
        print(f"   Start: {start_time}")
        print(f"   Duration: {duration_hours}h")
        
        result = await self.calendar_tool.create_event(
            title=title,
            start_time=start_time,
            duration_hours=duration_hours,
            description=description
        )
        
        if result["success"]:
            response = (
                f"✅ Event created successfully!\n"
                f"   Title: {result['title']}\n"
                f"   Start: {result['start']}\n"
                f"   End: {result['end']}\n"
                f"   Link: {result.get('link', 'N/A')}"
            )
            print(f"\n{response}")
            return response
        else:
            error_msg = f"❌ Failed to create event: {result.get('error', 'Unknown error')}"
            print(f"\n{error_msg}")
            return error_msg
