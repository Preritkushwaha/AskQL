import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class VisualizationService:
    @staticmethod
    def generate_chart(df: pd.DataFrame) -> go.Figure:
        """
        Automatically detect best chart type based on dataframe structure.
        """
        if df is None or df.empty:
            return None

        # Determine column types
        datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # If strings look like dates, convert them (simple heuristic)
        if not datetime_cols and categorical_cols:
            for col in categorical_cols:
                try:
                    df[col] = pd.to_datetime(df[col])
                    datetime_cols.append(col)
                    categorical_cols.remove(col)
                except (ValueError, TypeError):
                    pass

        # Rule 1: If dataframe contains datetime column and numeric column use line chart
        if datetime_cols and numeric_cols:
            x_col = datetime_cols[0]
            y_col = numeric_cols[0]
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            return fig

        # Rule 2: If dataframe contains categorical column and numeric column use bar chart
        if categorical_cols and numeric_cols:
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            
            # Sub-rule: If it looks like a percentage distribution (e.g. y values sum to ~100 or values are <= 1 and sum to 1) 
            # Or just if user has a small number of categories, use pie chart optionally.
            # But the requirement explicitly says: "If dataframe contains percentage distribution use pie chart"
            total = df[y_col].sum()
            if 0 < total <= 100.1 and df[y_col].min() >= 0: # heuristic for percentage
                # use pie
                fig = px.pie(df, names=x_col, values=y_col, title=f"Distribution of {y_col} by {x_col}")
            else:
                # Default to Bar chart
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            return fig

        # Rule 3: If dataframe contains two numeric columns use scatter plot
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter of {y_col} vs {x_col}")
            return fig

        # Fallback
        return None
