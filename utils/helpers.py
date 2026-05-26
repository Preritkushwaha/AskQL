import re

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
