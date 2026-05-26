# AskQL

AI-Powered Text-to-SQL & Data Visualization Platform. AskQL allows you to interact with databases using natural language instead of writing SQL manually. 

## Features
- Connect to PostgreSQL or SQLite databases.
- Chat with your database using natural language queries.
- Automatically generates and executes safe SELECT queries.
- Results visualization with data tables and smart interactive charts (Plotly).
- Get AI-driven insights describing the trends in the data.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and configure your API keys:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY`.
3. Run the application:
   ```bash
   streamlit run app.py
   ```
