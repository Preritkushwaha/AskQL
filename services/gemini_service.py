import os
import google.generativeai as genai
from utils.constants import GEMINI_PROMPT_TEMPLATE
from utils.helpers import clean_sql

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_sql(self, question: str, schema_context: str) -> str:
        """
        Uses Gemini API to generate SQL from natural language question.
        """
        if not self.model:
            raise Exception("Gemini API Key is not configured. Please add it to your .env file.")

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
