import streamlit as st
import pandas as pd

def render_result_table(df: pd.DataFrame):
    """
    Renders the DataFrame cleanly using Streamlit data editor/table.
    Provides export option.
    """
    if df is None or df.empty:
        st.warning("No results returned for this query.")
        return

    st.markdown("### 📋 Results Table")
    
    # Render table nicely
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export options
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='query_results.csv',
        mime='text/csv',
    )
