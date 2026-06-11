import streamlit as st
from sqlalchemy import inspect
from services.database_service import DatabaseService

class SchemaService:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def get_schema_summary(self) -> str:
        """
        Automatically fetch table names and columns to generate a compact schema context.
        """
        if not self.db_service.is_connected():
            return "No database connected."

        # Use cached schema if available
        if 'schema_summary' in st.session_state and st.session_state['schema_summary']:
            return st.session_state['schema_summary']

        try:
            inspector = inspect(self.db_service.engine)
            schema_lines = []
            
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                column_details = []
                for col in columns:
                    col_name = col['name']
                    col_type = str(col['type'])
                    column_details.append(f"{col_name} ({col_type})")
                
                table_schema = f"Table '{table_name}': " + ", ".join(column_details)
                schema_lines.append(table_schema)
                
            summary = "\n".join(schema_lines)
            st.session_state['schema_summary'] = summary
            return summary
            
        except Exception as e:
            return f"Failed to extract schema: {str(e)}"
