import os
import google.generativeai as genai
from utils.constants import GEMINI_PROMPT_TEMPLATE, DASHBOARD_PROMPT_TEMPLATE
from utils.helpers import clean_sql, retry_with_backoff

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.model = None

    @retry_with_backoff(max_retries=3, initial_delay=2.0)
    def generate_sql(self, question: str, schema_context: str, history: list = None) -> str:
        """
        Uses Gemini API to generate SQL from natural language question.
        history: list of dicts with 'role' ('user'|'assistant') and 'content' (str)
        """
        if not self.model:
            raise Exception("Gemini API Key is not configured. Please add it to your .env file.")

        if history and len(history) > 0:
            gemini_history = []
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
            chat = self.model.start_chat(history=gemini_history)
            
            prompt = f"Schema:\n{schema_context}\n\nQuestion:\n{question}\n\nRemember rules: ONLY return raw SQL query, no markdown blocks, no explanations, PostgreSQL syntax."
            
            try:
                response = chat.send_message(prompt)
                raw_sql = response.text
                return clean_sql(raw_sql)
            except Exception as e:
                raise Exception(f"Failed to generate SQL from Gemini (Chat): {str(e)}")
        else:
            prompt = GEMINI_PROMPT_TEMPLATE.format(
                schema=schema_context,
                question=question
            )

            try:
                response = self.model.generate_content(prompt)
                raw_sql = response.text
                return clean_sql(raw_sql)
            except Exception as e:
                raise Exception(f"Failed to generate SQL from Gemini: {str(e)}")

    @retry_with_backoff(max_retries=3, initial_delay=2.0)
    def generate_dashboard_sqls(self, request: str, schema_context: str) -> list:
        """
        Uses Gemini API to generate multiple SQL queries for a dashboard layout.
        Returns a list of dicts: [{'title': '...', 'sql': '...'}, ...]
        """
        import json
        if not self.model:
            raise Exception("Gemini API Key is not configured. Please add it to your .env file.")

        prompt = DASHBOARD_PROMPT_TEMPLATE.format(
            schema=schema_context,
            request=request
        )

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
            # Clean possible markdown formatting
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            return json.loads(raw_text)
        except Exception as e:
            raise Exception(f"Failed to generate dashboard SQLs from Gemini: {str(e)}")

    def suggest_chart_type(self, question: str, columns: list) -> str:
        """
        Suggests the most suitable chart type using a fast, rule-based heuristic.
        Rules based on previous prompt to avoid API call costs.
        """
        q_lower = question.lower()
        
        # Check for pie chart triggers
        if any(w in q_lower for w in ['distribution', 'share', 'percentage', 'breakdown', 'proportion', 'pie']):
            return 'pie'
            
        # Check for line chart triggers
        if any(w in q_lower for w in ['trend', 'over time', 'monthly', 'yearly', 'history', 'daily', 'line']):
            return 'line'
            
        # Check for scatter triggers
        if any(w in q_lower for w in ['relationship', 'vs', 'correlation', 'scatter']):
            return 'scatter'
            
        # Fallback to bar if comparing categories or simply multiple columns
        if len(columns) >= 2:
            return 'bar'
            
        return 'none'
