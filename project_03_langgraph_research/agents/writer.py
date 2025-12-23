"""Writer Agent - Creates summaries"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from parent directory (root of Agentic_ai)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class WriterAgent:
    """
    Agent responsible for writing summaries and extracting key points.
    
    This is the final NODE in the graph.
    """
    
    def __init__(self):
        """Initialize the LLM for writing"""
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-exp")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Configure Google GenerativeAI
        genai.configure(api_key=api_key)
        
        # Create model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.7,  # Higher temperature for creative writing
                "top_p": 0.9,
                "top_k": 40,
            }
        )
    
    def write_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive summary from all search results.
        """
        topic = state["topic"]
        all_results = state["search_results"]
        
        print(f"\n✍️  Writer Agent: Creating summary...")
        
        if not all_results:
            print("❌ No results to summarize")
            state["summary"] = "No information found."
            state["key_points"] = []
            return state
        
        # Combine all search results
        combined_results = ""
        for idx, result_set in enumerate(all_results, 1):
            combined_results += f"\n\n=== Search Attempt {idx} ===\n"
            combined_results += str(result_set["results"])[:1000]  # Limit length
        
        # Create prompt
        prompt = f"""Based on the search results below, create a comprehensive summary about: "{topic}"

Search Results:
{combined_results}

Please provide:
1. A clear, well-structured summary (3-5 paragraphs)
2. List 5 key points (bullet points)

Format your response as:

SUMMARY:
[Your summary here]

KEY POINTS:
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5
"""
        
        try:
            # Generate summary
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Parse response
            if "SUMMARY:" in content and "KEY POINTS:" in content:
                parts = content.split("KEY POINTS:")
                summary = parts[0].replace("SUMMARY:", "").strip()
                key_points_text = parts[1].strip()
                
                # Extract bullet points
                key_points = [
                    point.strip("- ").strip() 
                    for point in key_points_text.split("\n") 
                    if point.strip() and (point.strip().startswith("-") or point.strip().startswith("*"))
                ]
            else:
                # Fallback if format not followed
                summary = content
                key_points = []
            
            state["summary"] = summary
            state["key_points"] = key_points
            
            print(f"✅ Summary created ({len(summary)} chars, {len(key_points)} key points)")
            
        except Exception as e:
            print(f"❌ Writing failed: {e}")
            state["error"] = str(e)
            state["summary"] = "Failed to create summary."
            state["key_points"] = []
        
        return state


# Create global instance
writer_agent = WriterAgent()
