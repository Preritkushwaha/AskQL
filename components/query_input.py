import streamlit as st

def render_query_input() -> str:
    """
    Renders the natural language query input box.
    Returns the user's question.
    """
    st.markdown("### 💬 Ask your Data")
    
    question = st.text_area(
        "Enter your question in plain English:",
        placeholder="e.g., Show top 5 customers by revenue",
        height=100
    )
    
    # Examples
    st.markdown("**Sample Questions:**")
    cols = st.columns(3)
    sample_queries = [
        "Show top 5 customers by revenue",
        "Show monthly sales trend for 2025",
        "Compare region-wise sales"
    ]
    
    for i, col in enumerate(cols):
        with col:
            # We use markdown as clickable elements or just text hints
            st.caption(f"💡 *{sample_queries[i]}*")

    submit = st.button("Generate & Execute SQL 🚀", type="primary", use_container_width=True)
    
    if submit and question:
        return question.strip()
    return None
