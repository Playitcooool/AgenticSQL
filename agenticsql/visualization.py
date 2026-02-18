"""Visualization utilities for query results."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def should_visualize(question: str, dataframe: pd.DataFrame) -> bool:
    if dataframe.empty or len(dataframe.columns) < 2:
        return False
    keywords = ("图", "趋势", "分布", "占比", "chart", "plot", "visual", "可视化")
    lowered = question.lower()
    return any(k in lowered for k in keywords)


def save_auto_chart(dataframe: pd.DataFrame, output_dir: str) -> Path | None:
    import matplotlib.pyplot as plt

    numeric_cols = dataframe.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

    plt.figure(figsize=(10, 6))
    if len(dataframe.columns) >= 2 and len(numeric_cols) >= 1:
        x_col = dataframe.columns[0]
        y_col = numeric_cols[0]
        plt.bar(dataframe[x_col].astype(str), dataframe[y_col])
        plt.xticks(rotation=35, ha="right")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{y_col} by {x_col}")
    else:
        dataframe[numeric_cols].plot(ax=plt.gca())
        plt.title("Query Result")

    plt.tight_layout()
    plt.savefig(file_path, dpi=180)
    plt.close()
    return file_path
