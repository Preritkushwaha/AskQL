import re
from utils.constants import ALLOWED_SQL_PREFIXES, FORBIDDEN_SQL_KEYWORDS

class SQLValidator:
    @staticmethod
    def validate(sql_query: str) -> bool:
        """
        Validates the generated SQL before execution.
        Blocks DROP, DELETE, UPDATE, ALTER, INSERT.
        Allows only SELECT queries.
        """
        if not sql_query or not sql_query.strip():
            raise ValueError("Empty SQL query generated.")

        query_lower = sql_query.strip().lower()
        
        # Must start with a permitted prefix (typically SELECT or WITH)
        if not any(query_lower.startswith(prefix) for prefix in ALLOWED_SQL_PREFIXES):
            raise ValueError("Only SELECT or WITH queries are allowed.")
            
        # Check for forbidden keywords (very basic tokenization by regex)
        # We split by non-word characters to check words
        tokens = set(re.findall(r'\b\w+\b', query_lower))
        
        for forbidden in FORBIDDEN_SQL_KEYWORDS:
            if forbidden in tokens:
                raise ValueError(f"Destructive or unauthorized query blocked. Keyword found: {forbidden.upper()}")
                
        return True
