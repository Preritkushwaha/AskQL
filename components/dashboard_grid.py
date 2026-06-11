import streamlit as st
import pandas as pd
from components.charts import render_chart
from services.visualization_service import VisualizationService

def render_dashboard_grid(results: list):
    """
    Renders multiple queries in a dashboard layout.
    results: list of dicts with 'title' (str), 'df' (DataFrame)
    """
    if not results:
        return
        
    st.markdown("Generated Dashboard")
    st.markdown("---")
    
    # We can layout metrics first, then charts/tables in 2 columns
    metrics = [r for r in results if r['df'] is not None and not r['df'].empty and len(r['df']) == 1]
    others = [r for r in results if r not in metrics and r['df'] is not None and not r['df'].empty]
    
    # Render metrics in columns
    if metrics:
        st.markdown("Key Metrics")
        cols = st.columns(len(metrics))
        for i, m in enumerate(metrics):
            with cols[i]:
                df = m['df']
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    val = df.iloc[0][numeric_cols[0]]
                    if pd.isna(val):
                        val_str = "N/A"
                    elif isinstance(val, float):
                        val_str = f"{val:,.2f}"
                    else:
                        val_str = str(val)
                    st.metric(label=m['title'], value=val_str)
                    
    st.markdown("---")
    
    # Render others in a grid (2 columns)
    cols = st.columns(2)
    for i, r in enumerate(others):
        col = cols[i % 2]
        with col:
            st.markdown(f"### {r['title']}")
            df = r['df']
            
            # Try chart first
            chart_type_hint = r.get('chart_type', 'none')
            # If the LLM didn't provide a valid chart type or we need a fallback, we could still use heuristic
            if chart_type_hint not in ['bar', 'pie', 'line', 'scatter', 'none']:
                chart_type_hint = st.session_state['gemini_service'].suggest_chart_type(r['title'], list(df.columns)) if 'gemini_service' in st.session_state else r['title']
                
            fig = VisualizationService.generate_chart(df, chart_type_hint)
            if fig:
                # Update layout for smaller container
                fig.update_layout(margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback to table
                st.dataframe(df, use_container_width=True, hide_index=True)
