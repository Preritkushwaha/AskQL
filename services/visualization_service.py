import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class VisualizationService:
    @staticmethod
    def generate_chart(df: pd.DataFrame, query: str = "") -> go.Figure:
        """
        Automatically detect best chart type based on dataframe structure,
        or use explicit user request from the query.
        """
        if df is None or df.empty:
            return None

        # Determine column types
        datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category', 'string', 'bool']).columns.tolist()

        # If strings look like dates, convert them (simple heuristic)
        if not datetime_cols and categorical_cols:
            for col in categorical_cols[:]:
                try:
                    df[col] = pd.to_datetime(df[col])
                    datetime_cols.append(col)
                    categorical_cols.remove(col)
                except (ValueError, TypeError):
                    pass

        query_lower = query.lower()

        # Explicit user requests
        if "pie" in query_lower:
            # For pie chart, we need a categorical/datetime column and a numeric column
            # If no categorical, we can just use the first column as labels
            label_col = categorical_cols[0] if categorical_cols else (datetime_cols[0] if datetime_cols else df.columns[0])
            val_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)
            
            if val_col in numeric_cols:
                # Pie charts don't support negative values
                df_pie = df[df[val_col] >= 0]
                if not df_pie.empty:
                    return px.pie(df_pie, names=label_col, values=val_col, title=f"Pie Chart of {val_col} by {label_col}")

        if "bar" in query_lower:
            x_col = categorical_cols[0] if categorical_cols else (datetime_cols[0] if datetime_cols else df.columns[0])
            y_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)
            if y_col in numeric_cols:
                return px.bar(df, x=x_col, y=y_col, title=f"Bar Chart of {y_col} by {x_col}")

        if "line" in query_lower:
            x_col = datetime_cols[0] if datetime_cols else (categorical_cols[0] if categorical_cols else df.columns[0])
            y_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)
            if y_col in numeric_cols:
                return px.line(df, x=x_col, y=y_col, title=f"Line Chart of {y_col} over {x_col}")

        if "scatter" in query_lower:
            if len(numeric_cols) >= 2:
                return px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"Scatter Plot of {numeric_cols[1]} vs {numeric_cols[0]}")
            else:
                x_col = categorical_cols[0] if categorical_cols else (datetime_cols[0] if datetime_cols else df.columns[0])
                y_col = numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else None)
                if y_col in numeric_cols:
                    return px.scatter(df, x=x_col, y=y_col, title=f"Scatter Plot of {y_col} vs {x_col}")

        # Default rule 1: If dataframe contains datetime column and numeric column use line chart
        if datetime_cols and numeric_cols:
            x_col = datetime_cols[0]
            y_col = numeric_cols[0]
            fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}")
            return fig

        # Default rule 2: If dataframe contains categorical column and numeric column use bar chart
        if categorical_cols and numeric_cols:
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
            
            # Sub-rule: If it looks like a distribution/percentage
            # or if the user asks for 'distribution' in the query hint, or if the x_col has very few unique values (e.g., gender)
            total = df[y_col].sum()
            num_categories = df[x_col].nunique()
            
            is_percentage = 0 < total <= 100.1 and df[y_col].min() >= 0
            is_distribution_query = "distribution" in query_lower or "share" in query_lower or "proportion" in query_lower
            is_few_categories = num_categories <= 5 and df[y_col].min() >= 0
            
            if is_percentage or is_distribution_query or is_few_categories:
                # use pie
                fig = px.pie(df, names=x_col, values=y_col, title=f"Distribution of {y_col} by {x_col}")
            else:
                # Default to Bar chart
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            return fig

        # Default rule 3: If dataframe contains two numeric columns use scatter plot
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            fig = px.scatter(df, x=x_col, y=y_col, title=f"Scatter of {y_col} vs {x_col}")
            return fig

        # Fallback
        return None
