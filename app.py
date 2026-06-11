import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.helpers import setup_page_config
from components.sidebar import render_sidebar
from components.chatbot import render_chat_input
from components.dashboard_grid import render_dashboard_grid
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
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'query_cache' not in st.session_state:
    st.session_state['query_cache'] = {}

def main():
    st.title("AskQL")
    st.markdown("The AI-Powered Text-to-SQL Platform")
    
    # Sidebar
    render_sidebar()
    
    # Handle DB connection
    if st.session_state['connect_trigger']:
        try:
            with st.spinner("Connecting to database..."):
                st.session_state['db_service'].connect(st.session_state['db_url'])
                st.session_state['connected'] = True
                st.session_state.pop('schema_summary', None)
            st.toast("Successfully connected to the database!")
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.session_state['connected'] = False
        st.session_state['connect_trigger'] = False

    # Main Application Area
    if not st.session_state['connected']:
        st.info("Please connect to a database using the sidebar to get started.")
        return

    # Once connected
    schema_service = SchemaService(st.session_state['db_service'])
    
    with st.expander("View Database Schema"):
        schema_summary = schema_service.get_schema_summary()
        st.code(schema_summary, language="text")

    tab1, tab2 = st.tabs(["Chatbot", "Dashboard Builder"])

    with tab1:
        # Render chat history
        for i, item in enumerate(st.session_state['chat_history']):
            with st.chat_message(item['role']):
                if item['role'] == 'user':
                    st.markdown(item['content'])
                else:
                    st.markdown(f"Generated SQL\n```sql\n{item.get('sql', '')}\n```")
                    if item.get('df') is not None:
                        render_metric_cards(item['df'])
                        render_result_table(item['df'], key=f"hist_table_{i}")
                    if item.get('fig') is not None:
                        render_chart(item['fig'])
                    if item.get('insight'):
                        st.info(f"**AI Insights:** {item['insight']}", icon="🤖")
                    elif item.get('df') is not None and not item['df'].empty:
                        if st.button("Generate Insights", key=f"insight_btn_{i}"):
                            with st.spinner("Analyzing data trends..."):
                                prev_q = st.session_state['chat_history'][i-1]['content'] if i > 0 else ""
                                insight = st.session_state['insight_service'].generate_insight(prev_q, item['df'])
                                st.session_state['chat_history'][i]['insight'] = insight
                                st.rerun()

        # Chat Input
        user_question = render_chat_input()

        if user_question:
            # Append and render user message
            st.session_state['chat_history'].append({'role': 'user', 'content': user_question})
            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Generating SQL..."):
                    try:
                        # 1. Generate SQL
                        schema_context = schema_service.get_schema_summary()
                        
                        # Prepare history for Gemini: only text parts
                        if user_question in st.session_state['query_cache']:
                            generated_sql = st.session_state['query_cache'][user_question]
                            st.toast("Using cached SQL query!")
                        else:
                            gemini_history = [{"role": m["role"], "content": m["content"] if m["role"] == "user" else m["sql"]} for m in st.session_state['chat_history'][:-1]]
                            
                            generated_sql = st.session_state['gemini_service'].generate_sql(
                                question=user_question, 
                                schema_context=schema_context,
                                history=gemini_history
                            )
                            st.session_state['query_cache'][user_question] = generated_sql
                        
                        st.markdown("Generated SQL")
                        st.code(generated_sql, language="sql")
                        
                        # 2. Validate SQL
                        SQLValidator.validate(generated_sql)
                        
                        # 3. Execute SQL
                        with st.spinner("Executing Query..."):
                            df = st.session_state['db_service'].execute_query(generated_sql)
                        
                        # 4. Render UI components for Results
                        st.markdown("---")
                        
                        # Metric Cards for scalar aggregations
                        render_metric_cards(df)
                        
                        # Render Data Table
                        render_result_table(df, key=f"curr_table_{len(st.session_state['chat_history'])}")
                        
                        # Render Charts
                        chart_type_hint = st.session_state['gemini_service'].suggest_chart_type(user_question, list(df.columns))
                        fig = VisualizationService.generate_chart(df, chart_type_hint)
                        if fig:
                            render_chart(fig)
                        
                        # Save to history
                        st.session_state['chat_history'].append({
                            'role': 'assistant',
                            'sql': generated_sql,
                            'df': df,
                            'fig': fig,
                            'insight': None
                        })
                        
                        # Rerun to cleanly render the state
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error processing your request: {str(e)}")

    with tab2:
        st.markdown("Build an Auto-Dashboard")
        dashboard_prompt = st.text_area("Describe the dashboard you want:", placeholder="e.g., Generate a comprehensive sales dashboard with monthly trends and region breakdown.")
        
        if st.button("Generate Dashboard", type="primary"):
            if dashboard_prompt:
                with st.spinner("Designing dashboard layout and generating SQL queries..."):
                    try:
                        schema_context = schema_service.get_schema_summary()
                        queries = st.session_state['gemini_service'].generate_dashboard_sqls(
                            request=dashboard_prompt, 
                            schema_context=schema_context
                        )
                        
                        results = []
                        st.success(f"Generated {len(queries)} widgets!")
                        
                        # Execute each query
                        for idx, q in enumerate(queries):
                            title = q.get("title", f"Widget {idx+1}")
                            sql = q.get("sql", "")
                            chart_type = q.get("chart_type", "none")
                            try:
                                SQLValidator.validate(sql)
                                df = st.session_state['db_service'].execute_query(sql)
                                results.append({"title": title, "df": df, "chart_type": chart_type})
                            except Exception as e:
                                st.warning(f"Failed to load '{title}': {str(e)}")
                                
                        if results:
                            render_dashboard_grid(results)
                            
                    except Exception as e:
                        st.error(f"Error generating dashboard: {str(e)}")
            else:
                st.warning("Please enter a description for the dashboard.")

if __name__ == "__main__":
    main()
