import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.helpers import setup_page_config
from components.sidebar import render_sidebar
from components.query_input import render_query_input
from components.result_table import render_result_table
from components.charts import render_chart
from components.metric_cards import render_metric_cards

from services.database_service import DatabaseService
from services.schema_service import SchemaService
from services.gemini_service import GeminiService
from services.sql_validator import SQLValidator
from services.visualization_service import VisualizationService
from services.insight_service import InsightService

# Initialize app layout and config
setup_page_config(st)

# Initialize Session State
if 'db_service' not in st.session_state:
    st.session_state['db_service'] = DatabaseService()
if 'gemini_service' not in st.session_state:
    st.session_state['gemini_service'] = GeminiService()
if 'insight_service' not in st.session_state:
    st.session_state['insight_service'] = InsightService()
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'db_url' not in st.session_state:
    st.session_state['db_url'] = None
if 'connect_trigger' not in st.session_state:
    st.session_state['connect_trigger'] = False

def main():
    st.title("AskQL 🧠📊")
    st.markdown("### The AI-Powered Text-to-SQL Platform")
    
    # Sidebar
    render_sidebar()
    
    # Handle DB connection
    if st.session_state['connect_trigger']:
        try:
            with st.spinner("Connecting to database..."):
                st.session_state['db_service'].connect(st.session_state['db_url'])
                st.session_state['connected'] = True
            st.toast("Successfully connected to the database!", icon="✅")
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.session_state['connected'] = False
        st.session_state['connect_trigger'] = False

    # Main Application Area
    if not st.session_state['connected']:
        st.info("👈 Please connect to a database using the sidebar to get started.")
        return

    # Once connected
    schema_service = SchemaService(st.session_state['db_service'])
    
    with st.expander("👁️ View Database Schema"):
        schema_summary = schema_service.get_schema_summary()
        st.code(schema_summary, language="text")

    # Query Input
    user_question = render_query_input()

    if user_question:
        with st.spinner("🧠 Generating SQL..."):
            try:
                # 1. Generate SQL
                schema_context = schema_service.get_schema_summary()
                generated_sql = st.session_state['gemini_service'].generate_sql(
                    question=user_question, 
                    schema_context=schema_context
                )
                
                st.markdown("### 📝 Generated SQL")
                st.code(generated_sql, language="sql")
                
                # 2. Validate SQL
                SQLValidator.validate(generated_sql)
                
                # 3. Execute SQL
                with st.spinner("⏳ Executing Query..."):
                    df = st.session_state['db_service'].execute_query(generated_sql)
                
                # 4. Render UI components for Results
                st.markdown("---")
                
                # Metric Cards for scalar aggregations
                render_metric_cards(df)
                
                # Render Data Table
                render_result_table(df)
                
                # Render Charts
                fig = VisualizationService.generate_chart(df)
                if fig:
                    render_chart(fig)
                
                # 5. Generate AI Insights
                with st.spinner("💡 Analyzing data trends..."):
                    insight = st.session_state['insight_service'].generate_insight(user_question, df)
                    st.info(f"**AI Insights:** {insight}", icon="🤖")

            except Exception as e:
                st.error(f"Error processing your request: {str(e)}")

if __name__ == "__main__":
    main()
