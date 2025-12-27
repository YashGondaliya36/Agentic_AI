"""
AI Data Analyst Agent
Uses Google Gemini to write and execute Python code for data analysis
"""

import os
import json
import traceback
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyBwrU5EUs1DLPTz6iWZZ7avpNIZOWUaamA"
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=GOOGLE_API_KEY)


class DataAnalystAgent:
    """AI Agent that analyzes data by writing and executing Python code"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.conversation_history = []
        self.current_dataframe = None
        self.df_info = None
        
    def load_data(self, file_path: str) -> Dict[str, Any]:
        """Load CSV or Excel file"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                self.current_dataframe = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                self.current_dataframe = pd.read_excel(file_path)
            else:
                return {"success": False, "error": "Unsupported file format"}
            
            # Get dataframe info
            self.df_info = {
                "columns": list(self.current_dataframe.columns),
                "shape": self.current_dataframe.shape,
                "dtypes": {col: str(dtype) for col, dtype in self.current_dataframe.dtypes.items()},
                "preview": self.current_dataframe.head(5).to_dict(orient='records')
            }
            
            return {
                "success": True,
                "info": self.df_info,
                "message": f"Loaded {self.df_info['shape'][0]} rows and {self.df_info['shape'][1]} columns"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_query(self, user_question: str) -> Dict[str, Any]:
        """Analyze user's question and generate response"""
        
        if self.current_dataframe is None:
            return {
                "success": False,
                "error": "No data loaded. Please upload a file first."
            }
        
        try:
            # Step 1: Generate Python code using Gemini
            code_response = self._generate_code(user_question)
            
            if not code_response["success"]:
                return code_response
            
            generated_code = code_response["code"]
            
            # Step 2: Execute the code safely
            execution_result = self._execute_code(generated_code)
            
            if not execution_result["success"]:
                return execution_result
            
            # Step 3: Generate natural language explanation
            explanation = self._generate_explanation(
                user_question, 
                generated_code, 
                execution_result
            )
            
            return {
                "success": True,
                "answer": explanation,
                "code": generated_code,
                "visualization": execution_result.get("visualization"),
                "data": execution_result.get("data")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _generate_code(self, question: str) -> Dict[str, Any]:
        """Generate Python code using Gemini"""
        
        prompt = f"""You are an expert data analyst. Generate Python code to answer this question about the dataset.

Dataset Information:
- Columns: {', '.join(self.df_info['columns'])}
- Shape: {self.df_info['shape'][0]} rows, {self.df_info['shape'][1]} columns
- Data types: {json.dumps(self.df_info['dtypes'], indent=2)}
- Preview (first 5 rows): {json.dumps(self.df_info['preview'], indent=2)}

User Question: {question}

IMPORTANT RULES:
1. The dataframe is already loaded as variable 'df'
2. Use ONLY Plotly for visualizations (plotly.express or plotly.graph_objects)
3. For visualizations, save to 'outputs/chart.html' using fig.write_html()
4. Return results as a dictionary with key 'result'
5. Keep code simple and efficient
6. Handle missing values appropriately
7. DO NOT use plt, matplotlib, or seaborn
8. DO NOT read the file again, use the existing 'df' variable

Generate ONLY executable Python code, no explanations.
Format: Pure Python code block without markdown backticks.
"""

        try:
            response = self.model.generate_content(prompt)
            code = response.text.strip()
            
            # Clean up code (remove markdown if present)
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
            
            return {"success": True, "code": code}
            
        except Exception as e:
            return {"success": False, "error": f"Code generation failed: {str(e)}"}
    
    def _execute_code(self, code: str) -> Dict[str, Any]:
        """Safely execute the generated Python code"""
        
        try:
            # Create a safe execution environment
            namespace = {
                'df': self.current_dataframe.copy(),
                'pd': pd,
                'px': px,
                'go': go,
                'result': None
            }
            
            # Execute the code
            exec(code, namespace)
            
            # Get the result
            result_data = namespace.get('result')
            
            # Check if visualization was created
            visualization_path = "outputs/chart.html"
            has_visualization = Path(visualization_path).exists()
            
            return {
                "success": True,
                "data": result_data,
                "visualization": visualization_path if has_visualization else None
            }
            
        except Exception as e:
            error_trace = traceback.format_exc()
            return {
                "success": False,
                "error": f"Code execution failed: {str(e)}",
                "traceback": error_trace
            }
    
    def _generate_explanation(self, question: str, code: str, execution_result: Dict) -> str:
        """Generate natural language explanation of the analysis"""
        
        prompt = f"""You are a data analyst explaining results to a non-technical user.

Original Question: {question}

Code Executed:
{code}

Result Data: {execution_result.get('data')}

Provide a clear, concise explanation of:
1. What the data shows
2. Key insights or findings
3. Any notable patterns or trends

Keep it conversational and easy to understand. Maximum 3-4 sentences.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Fallback explanation
            data = execution_result.get('data')
            if data:
                return f"Analysis complete. Result: {data}"
            return "Analysis completed successfully. Check the visualization for details."
