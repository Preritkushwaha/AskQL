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
                
            return "\n".join(schema_lines)
            
        except Exception as e:
            return f"Failed to extract schema: {str(e)}"
