import os
import google.generativeai as genai
from utils.constants import GEMINI_PROMPT_TEMPLATE
from utils.helpers import clean_sql

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

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
        Uses Gemini API to suggest the most suitable chart type for the given question and data columns.
        """
        if not self.model:
            return "none"
            
        prompt = f"""
        You are an expert data visualization analyst.
        Given the user question: '{question}' and the resulting data columns: {columns}, what is the best visualization technique to use? 
        
        Follow these strict chart selection rules:
        - 'pie': Use when the user asks for 'distribution', 'share', 'percentage', 'breakdown', or 'proportion' of a whole. It is especially suitable for categorical data representing parts of a whole (e.g., gender, status).
        - 'line': Use when tracking changes over time, dates, or continuous periods (e.g., 'trend', 'over time', 'monthly', 'yearly', 'history').
        - 'scatter': Use when comparing two independent numerical variables to find correlation or clusters (e.g., 'relationship', 'vs', 'correlation').
        - 'bar': Use when comparing independent quantities across different categories (e.g., 'by region', 'top 10', 'compare', 'count by department'). This is the default for categorical vs numeric data unless 'distribution' is heavily implied.
        - 'none': Use if the result is a single scalar value (e.g., 'what is the total revenue') or if a chart simply does not make sense for the data.

        Choose exactly one from: [bar, pie, line, scatter, none]. Reply with ONLY the chart type word in lowercase.
        """
        
        try:
            response = self.model.generate_content(prompt)
            chart = response.text.strip().lower()
            
            for valid_chart in ["bar", "pie", "line", "scatter"]:
                if valid_chart in chart:
                    return valid_chart
            print(f"DEBUG LLM Output: {chart}")
            return "none"
        except Exception as e:
            print(f"DEBUG LLM Exception: {e}")
            return "none"
