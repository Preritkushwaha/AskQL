import os
import pandas as pd
import google.generativeai as genai
from utils.constants import INSIGHT_PROMPT_TEMPLATE

class InsightService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def generate_insight(self, question: str, df: pd.DataFrame) -> str:
        """
        Generate short AI summary from returned data to explain trends in simple English.
        """
        if not self.model:
            return "AI Insights unavailable: Gemini API key missing."
            
        if df is None or df.empty:
            return "No data available to generate insights."

        # Create a compact string representation of the dataframe for the prompt
        # We limit the rows to avoid token overflow
        sample_df = df.head(10).to_markdown()
        stats = df.describe(include='all').to_markdown()

        data_summary = f"Sample Data:\n{sample_df}\n\nStatistics:\n{stats}"

        prompt = INSIGHT_PROMPT_TEMPLATE.format(
            question=question,
            data_summary=data_summary
        )

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Failed to generate insight: {str(e)}"
