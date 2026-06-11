import streamlit as st

def render_sidebar():
    """
    Renders the sidebar navigation and database connection form.
    """
    with st.sidebar:
        st.header("🔌 Database Connection")
        
        db_type = st.selectbox("Database Type", ["PostgreSQL", "SQLite"])
        
        if db_type == "PostgreSQL":
            host = st.text_input("Host", value="localhost")
            port = st.text_input("Port", value="5432")
            dbname = st.text_input("Database Name")
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Connect", use_container_width=True):
                if not all([host, port, dbname, user, password]):
                    st.error("Please fill in all connection details.")
                else:
                    import urllib.parse
                    enc_user = urllib.parse.quote(user)
                    enc_password = urllib.parse.quote(password)
                    enc_host = urllib.parse.quote(host)
                    enc_dbname = urllib.parse.quote(dbname)
                    db_url = f"postgresql://{enc_user}:{enc_password}@{enc_host}:{port}/{enc_dbname}"
                    st.session_state['db_url'] = db_url
                    st.session_state['connect_trigger'] = True

        elif db_type == "SQLite":
            db_path = st.text_input("Local Database Path (e.g., ./data.db)")
            
            if st.button("Connect", use_container_width=True):
                if not db_path:
                    st.error("Please provide a path to your SQLite database.")
                else:
                    db_url = f"sqlite:///{db_path}"
                    st.session_state['db_url'] = db_url
                    st.session_state['connect_trigger'] = True

        st.markdown("---")
        st.markdown("About")
        st.markdown(
            "**AskQL** lets you query your database using natural language. "
            "Simply connect and start asking questions!"
        )
