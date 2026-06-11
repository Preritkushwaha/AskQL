import streamlit as st

def render_chat_input() -> str:
    """
    Renders the chat input box and suggestions if history is empty.
    Returns the user's question.
    """
    if not st.session_state.get('chat_history', []):
        st.markdown("**Sample Questions:**")
        cols = st.columns(3)
        sample_queries = [
            "Show top 5 customers by revenue",
            "Show monthly sales trend for 2025",
            "Compare region-wise sales"
        ]
        for i, col in enumerate(cols):
            with col:
                st.caption(f"💡 *{sample_queries[i]}*")

    question = st.chat_input("Enter your question in plain English (e.g., Show top 5 customers by revenue)")
    
    if question:
        return question.strip()
    return None
