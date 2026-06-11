# Prompt templates and constants used across the application

GEMINI_PROMPT_TEMPLATE = """
You are an expert SQL generator. 

Database Schema:
{schema}

Rules:
- Generate ONLY valid SQL queries.
- Only generate SELECT queries.
- Never generate destructive queries (e.g., DROP, DELETE, UPDATE, ALTER, INSERT).
- Use PostgreSQL syntax unless told otherwise.
- Do not explain the SQL, do not include markdown blocks like ```sql ... ```. Return the raw SQL string ONLY.

Question:
{question}
"""

INSIGHT_PROMPT_TEMPLATE = """
You are a data analyst. You are given a user question and a summary of the data returned by a SQL query.
Provide a short, simple, and clear summary of the trends or insights found in the data.
Explain it in simple English without any technical jargon. Be very concise.

User Question: {question}

Data Summary:
{data_summary}
"""

DASHBOARD_PROMPT_TEMPLATE = """
You are an expert data analyst and SQL generator.
Given a broad request (like "Generate a sales dashboard") and a database schema, your task is to generate a JSON array of multiple SQL queries that would power various charts and metrics for this dashboard.

Database Schema:
{schema}

Rules:
- Generate ONLY a valid JSON array of objects.
- Each object must have a "title" (string, short description of the chart/metric), a "chart_type" (string, one of 'bar', 'pie', 'line', 'scatter', 'none' - 'none' for a single scalar value), and a "sql" (string, the SELECT query).
- Only generate SELECT queries. Never generate destructive queries (e.g., DROP, DELETE, UPDATE, ALTER, INSERT).
- Use PostgreSQL syntax unless told otherwise.
- Output ONLY the raw JSON array. Do not wrap in markdown blocks like ```json ... ```.

Request:
{request}
"""

ALLOWED_SQL_PREFIXES = ["select", "with"]
FORBIDDEN_SQL_KEYWORDS = ["drop", "delete", "update", "alter", "insert", "truncate", "grant", "revoke", "commit", "rollback"]
