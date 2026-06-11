import re
import time
import functools
import streamlit as st
from google.api_core.exceptions import ResourceExhausted

def retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0):
    """
    Retry a function with exponential backoff for ResourceExhausted (429) exceptions.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ResourceExhausted as e:
                    if i == max_retries - 1:
                        raise Exception("Gemini API quota exceeded (429 Too Many Requests). Please try again later.") from e
                    st.warning(f"API Rate limit hit. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= backoff_factor
                except Exception as e:
                    # Reraise other exceptions immediately
                    raise e
        return wrapper
    return decorator

def clean_sql(sql_query: str) -> str:
    """
    Cleans up the generated SQL by removing markdown formatting if the LLM hallucinated it.
    """
    sql_query = sql_query.strip()
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:]
    if sql_query.startswith("```"):
        sql_query = sql_query[3:]
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3]
    return sql_query.strip()

def setup_page_config(st):
    """
    Setup common Streamlit page config for modern SaaS look.
    """
    st.set_page_config(
        page_title="AskQL",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
