"""Analyzer Agent - Evaluates result quality"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from parent directory (root of Agentic_ai)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class AnalyzerAgent:
    """
    Agent responsible for analyzing search result quality.
    
    This is a NODE in the graph that decides if we need more research.
    """
    
    def __init__(self):
        """Initialize the LLM for analysis"""
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash-lite")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Configure Google GenerativeAI
        genai.configure(api_key=api_key)
        
        # Create model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.2,  # Low temperature for consistent analysis
                "top_p": 0.8,
                "top_k": 40,
            }
        )
    
    def analyze(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the quality of search results.
        
        Returns a score from 0-10 and decides if more research is needed.
        """
        topic = state["topic"]
        results = state["search_results"]
        attempts = state["search_attempts"]
        
        print(f"\n🔬 Analyzer Agent: Evaluating results...")
        
        if not results:
            print("❌ No results to analyze")
            state["quality_score"] = 0.0
            state["needs_more_research"] = attempts < 3  # Try max 3 times
            return state
        
        # Prepare prompt for LLM
        results_text = str(results[-1]["results"])[:500]  # Last search results
        
        prompt = f"""Analyze the quality of these search results for the topic: "{topic}"

Search Results:
{results_text}

Rate the quality from 0-10 where:
- 0-3: Poor quality, irrelevant or insufficient
- 4-6: Moderate quality, some useful info
- 7-10: High quality, comprehensive and relevant

Respond with ONLY a number between 0-10."""
        
        try:
            # Ask LLM to rate quality
            response = self.model.generate_content(prompt)
            score_text = response.text.strip()
            
            # Extract number
            try:
                score = float(score_text)
                score = max(0.0, min(10.0, score))  # Clamp between 0-10
            except ValueError:
                score = 5.0  # Default to moderate if parsing fails
            
            state["quality_score"] = score
            
            # Decide if more research needed
            # If score < 7 AND we haven't tried 3 times, search again
            if score < 7.0 and attempts < 3:
                state["needs_more_research"] = True
                print(f"📊 Quality Score: {score}/10 - Need more research")
            else:
                state["needs_more_research"] = False
                print(f"📊 Quality Score: {score}/10 - Sufficient!")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            state["error"] = str(e)
            state["quality_score"] = 0.0
            state["needs_more_research"] = False
        
        return state


# Create global instance
analyzer_agent = AnalyzerAgent()
