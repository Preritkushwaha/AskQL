import streamlit as st
from plotly.graph_objs import Figure

def render_chart(fig: Figure):
    """
    Renders the Plotly chart if available.
    """
    if fig:
        st.markdown("Visualizations")
        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
