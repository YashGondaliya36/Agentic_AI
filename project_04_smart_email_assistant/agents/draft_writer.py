"""Draft Writer Agent - Generates email responses"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class DraftWriterAgent:
    """
    Generates professional email responses.
    
    Uses context from:
    - Original email
    - Search results (if available)
    - Past emails (if available)
    """
    
    def __init__(self):
        """Initialize the writer"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.7,  # Balanced for professional writing
                "top_p": 0.9,
                "top_k": 40,
            }
        )
    
    def write_draft(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate email draft response.
        """
        email = state["email"]
        category = state.get("category", "normal")
        context = state.get("context", [])
        
        print(f"\n✍️  Writing draft response...")
        
        # Build context section
        context_text = ""
        if context:
            context_text = "\n\nAdditional Context:\n" + "\n".join(f"- {c}" for c in context)
        
        prompt = f"""You are a professional email assistant. Write a response to this email:

FROM: {email['from_name']} <{email['from_email']}>
SUBJECT: {email['subject']}
BODY:
{email['body']}
{context_text}

GUIDELINES:
- Be professional and friendly
- Keep it concise (3-5 paragraphs max)
- Match the tone of the original email
- If it's urgent ({category == 'urgent'}), acknowledge that
- If information is missing, ask for it politely
- End with appropriate closing

Write ONLY the email body (no subject line needed):
"""
        
        try:
            response = self.model.generate_content(prompt)
            draft = response.text.strip()
            
            state["draft_response"] = draft
            state["processing_step"] = "human_review"
            
            print(f"   ✅ Draft created ({len(draft)} chars)")
            print(f"\n{'='*60}")
            print("DRAFT PREVIEW:")
            print('='*60)
            print(draft[:200] + "..." if len(draft) > 200 else draft)
            print('='*60)
            
        except Exception as e:
            print(f"   ❌ Draft generation failed: {e}")
            state["error"] = str(e)
            state["draft_response"] = "Failed to generate draft."
        
        return state


# Global instance
draft_writer_agent = DraftWriterAgent()
