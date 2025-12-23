"""Email Classifier Agent - Categorizes and prioritizes emails"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env from root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class ClassifierAgent:
    """
    Classifies emails into categories and assigns priority.
    
    Categories:
    - urgent: Needs immediate response
    - important: High priority, respond today
    - normal: Standard email
    - promotional: Marketing/newsletters
    - spam: Junk/unwanted
    """
    
    def __init__(self):
        """Initialize the classifier"""
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.1,  # Low temp for consistent classification
                "top_p": 0.8,
                "top_k": 40,
            }
        )
    
    def classify(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify an email.
        
        Returns updated state with:
        - category
        - priority (1-5)
        - action_required (bool)
        """
        email = state["email"]
        
        print(f"\n📊 Classifying: '{email['subject']}'")
        print(f"   From: {email['from_name']}")
        
        prompt = f"""Classify this email:

From: {email['from_name']} <{email['from_email']}>
Subject: {email['subject']}
Body: {email['body'][:500]}

Provide:
1. Category: urgent/important/normal/promotional/spam
2. Priority: 1-5 (5=highest)
3. Action Required: yes/no (does this need a response?)

Respond ONLY in this exact format:
CATEGORY: [category]
PRIORITY: [number]
ACTION: [yes/no]
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # Parse response
            lines = result.split('\n')
            category = "normal"
            priority = 3
            action_required = False
            
            for line in lines:
                if line.startswith("CATEGORY:"):
                    category = line.split(':')[1].strip().lower()
                elif line.startswith("PRIORITY:"):
                    try:
                        priority = int(line.split(':')[1].strip())
                        priority = max(1, min(5, priority))
                    except:
                        priority = 3
                elif line.startswith("ACTION:"):
                    action_text = line.split(':')[1].strip().lower()
                    action_required = action_text in ['yes', 'true', 'y']
            
            state["category"] = category
            state["priority"] = priority
            state["action_required"] = action_required
            state["processing_step"] = "context_gathering"
            
            print(f"   ✅ Category: {category.upper()}")
            print(f"   ⭐ Priority: {priority}/5")
            print(f"   📝 Action Required: {action_required}")
            
        except Exception as e:
            print(f"   ❌ Classification failed: {e}")
            state["error"] = str(e)
            state["category"] = "normal"
            state["priority"] = 3
        
        return state


# Global instance
classifier_agent = ClassifierAgent()
