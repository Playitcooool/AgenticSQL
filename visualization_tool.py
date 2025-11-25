"""
Data visualization tool
"""
import os
from datetime import datetime
from langchain_core.tools import tool
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from database_tools import execute_sql_for_viz


@tool
def visualize_data(db_path: str, sql_query: str, chart_type: str = "auto") -> str:
    """
    Execute SQL query and create a visualization of the results.

    Args:
        db_path: Path to the SQLite database file
        sql_query: The SQL query to execute
        chart_type: Type of chart (auto, bar, line, pie, scatter, heatmap)

    Returns:
        Path to the saved visualization image
    """
    try:
        # Execute query and get DataFrame
        df = execute_sql_for_viz(db_path, sql_query)

        if df.empty:
            return "Cannot visualize: Query returned no results."

        # Set style
        sns.set_style("whitegrid")
        plt.figure(figsize=(10, 6))

        # Determine chart type automatically if needed
        if chart_type == "auto":
            chart_type = _determine_chart_type(df)

        # Create visualization based on type
        if chart_type == "bar":
            _create_bar_chart(df)
        elif chart_type == "line":
            _create_line_chart(df)
        elif chart_type == "pie":
            _create_pie_chart(df)
        elif chart_type == "scatter":
            _create_scatter_plot(df)
        elif chart_type == "heatmap":
            _create_heatmap(df)
        else:
            _create_bar_chart(df)  # Default to bar chart

        # Save figure
        output_dir = "visualizations"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"viz_{timestamp}.png")

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        return f"Visualization saved to: {output_path}"

    except Exception as e:
        return f"Error creating visualization: {str(e)}"


def _determine_chart_type(df: pd.DataFrame) -> str:
    """Determine the best chart type based on data structure."""
    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(df) == 1 and len(num_cols) > 1:
        return "bar"  # Single row with multiple numeric columns
    elif len(cat_cols) == 1 and len(num_cols) == 1:
        if len(df) <= 10:
            return "pie" if df[num_cols[0]].sum() > 0 else "bar"
        else:
            return "bar"
    elif len(num_cols) >= 2:
        return "scatter"
    else:
        return "bar"


def _create_bar_chart(df: pd.DataFrame):
    """Create a bar chart."""
    if len(df.columns) == 2:
        x_col, y_col = df.columns[0], df.columns[1]
        plt.bar(df[x_col].astype(str), df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.xticks(rotation=45, ha='right')
    else:
        # Multiple columns - plot all numeric ones
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df[numeric_cols].plot(kind='bar', ax=plt.gca())
            plt.legend(loc='best')
            plt.xticks(rotation=45, ha='right')

    plt.title('Bar Chart')


def _create_line_chart(df: pd.DataFrame):
    """Create a line chart."""
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(df.columns) == 2 and len(numeric_cols) == 1:
        x_col, y_col = df.columns[0], df.columns[1]
        plt.plot(df[x_col], df[y_col], marker='o')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
    else:
        for col in numeric_cols:
            plt.plot(df.index, df[col], marker='o', label=col)
        plt.legend()

    plt.title('Line Chart')
    plt.xticks(rotation=45, ha='right')


def _create_pie_chart(df: pd.DataFrame):
    """Create a pie chart."""
    if len(df.columns) >= 2:
        labels_col = df.columns[0]
        values_col = df.columns[1]

        plt.pie(df[values_col], labels=df[labels_col], autopct='%1.1f%%')
        plt.title('Pie Chart')
        plt.axis('equal')


def _create_scatter_plot(df: pd.DataFrame):
    """Create a scatter plot."""
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        plt.scatter(df[x_col], df[y_col], alpha=0.6)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title('Scatter Plot')


def _create_heatmap(df: pd.DataFrame):
    """Create a heatmap of numeric data."""
    numeric_df = df.select_dtypes(include=['number'])

    if not numeric_df.empty:
        sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', center=0)
        plt.title('Correlation Heatmap')
