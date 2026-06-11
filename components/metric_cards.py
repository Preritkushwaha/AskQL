import streamlit as st
import pandas as pd

def render_metric_cards(df: pd.DataFrame):
    """
    If the result is a single row with aggregate metrics, render them as cards.
    """
    if df is not None and not df.empty and len(df) == 1:
        st.markdown("Key Metrics")
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) > 0:
            cols = st.columns(len(numeric_cols))
            for i, col_name in enumerate(numeric_cols):
                val = df.iloc[0][col_name]
                # Format smartly
                if pd.isna(val):
                    val_str = "N/A"
                elif isinstance(val, float):
                    val_str = f"{val:,.2f}"
                else:
                    val_str = str(val)
                    
                with cols[i]:
                    st.metric(label=col_name, value=val_str)
