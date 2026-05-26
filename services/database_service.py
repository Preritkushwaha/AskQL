from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

class DatabaseService:
    def __init__(self):
        self.engine: Engine = None
    
    def connect(self, db_url: str) -> bool:
        """
        Connect to the database using the provided SQLAlchemy URL.
        """
        try:
            self.engine = create_engine(db_url)
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            self.engine = None
            raise Exception(f"Database connection failed: {str(e)}")

    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a Pandas DataFrame.
        """
        if not self.engine:
            raise Exception("No active database connection.")
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql_query(sql_query, conn)
                return df
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
            
    def is_connected(self) -> bool:
        return self.engine is not None
