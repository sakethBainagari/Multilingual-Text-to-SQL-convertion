"""Visualisation engine – Plotly (interactive) + Matplotlib (static)."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import plotly.utils
import seaborn as sns

logger = logging.getLogger(__name__)


class VisualizationEngine:
    """Create dynamic visualisations with Plotly and Matplotlib."""

    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        try:
            plt.style.use("seaborn-v0_8")
        except OSError:
            plt.style.use("ggplot")

    # ------------------------------------------------------------------
    # Chart-type detection
    # ------------------------------------------------------------------

    @staticmethod
    def detect_chart_type(df: pd.DataFrame) -> str:
        if df.empty:
            return "none"
        num_cols = df.select_dtypes(include=[np.number]).columns
        cat_cols = df.select_dtypes(exclude=[np.number]).columns

        if len(num_cols) >= 2:
            return "scatter"
        if len(num_cols) == 1 and len(cat_cols) == 1:
            return "bar" if df[cat_cols[0]].nunique() <= 10 else "histogram"
        if len(cat_cols) == 1:
            return "pie"
        if len(num_cols) == 1:
            return "histogram"
        return "bar"

    SUPPORTED_CHART_TYPES = ["bar", "line", "pie", "histogram", "scatter"]

    # ------------------------------------------------------------------
    # Plotly (interactive)
    # ------------------------------------------------------------------

    def create_plotly_visualization(
        self, df: pd.DataFrame, chart_type: Optional[str] = None, title: Optional[str] = None
    ) -> Optional[Dict]:
        if df.empty:
            return None
        chart_type = chart_type or self.detect_chart_type(df)
        if chart_type == "none":
            return None

        builders = {
            "bar": self._plotly_bar,
            "line": self._plotly_line,
            "pie": self._plotly_pie,
            "histogram": self._plotly_histogram,
            "scatter": self._plotly_scatter,
        }
        try:
            fig_data = builders.get(chart_type, self._plotly_bar)(df)
            layout = go.Layout(
                title=title or f"Data Visualization ({chart_type.title()} Chart)",
                xaxis=dict(title=df.columns[0] if len(df.columns) > 0 else "X-axis"),
                yaxis=dict(title=df.columns[1] if len(df.columns) > 1 else "Y-axis"),
                hovermode="closest",
                template="plotly_white",
            )
            fig_obj = {"data": fig_data, "layout": layout}
            try:
                return json.loads(pio.to_json(fig_obj))
            except Exception:
                return json.loads(json.dumps(fig_obj, cls=plotly.utils.PlotlyJSONEncoder))
        except Exception as exc:
            logger.error("Plotly visualisation error: %s", exc)
            return None

    # --- Plotly chart builders ---

    @staticmethod
    def _plotly_bar(df):
        if len(df.columns) >= 2:
            return [go.Bar(x=df[df.columns[0]], y=df[df.columns[1]], name=df.columns[1])]
        vals = df.iloc[:, 0].value_counts()
        return [go.Bar(x=vals.index, y=vals.values, name=df.columns[0])]

    @staticmethod
    def _plotly_line(df):
        if len(df.columns) >= 2:
            return [go.Scatter(x=df[df.columns[0]], y=df[df.columns[1]], mode="lines+markers", name=df.columns[1])]
        return [go.Scatter(y=df.iloc[:, 0], mode="lines+markers", name=df.columns[0])]

    @staticmethod
    def _plotly_pie(df):
        if len(df.columns) >= 2:
            return [go.Pie(labels=df[df.columns[0]], values=df[df.columns[1]])]
        vals = df.iloc[:, 0].value_counts()
        return [go.Pie(labels=vals.index, values=vals.values)]

    @staticmethod
    def _plotly_histogram(df):
        num = df.select_dtypes(include=[np.number]).columns
        col = num[0] if len(num) > 0 else df.columns[0]
        return [go.Histogram(x=df[col], name=col)]

    @staticmethod
    def _plotly_scatter(df):
        num = df.select_dtypes(include=[np.number]).columns
        if len(num) >= 2:
            return [go.Scatter(x=df[num[0]], y=df[num[1]], mode="markers", name=f"{num[1]} vs {num[0]}")]
        return [go.Scatter(y=df.iloc[:, 0], mode="markers", name=df.columns[0])]

    # ------------------------------------------------------------------
    # Matplotlib (static export)
    # ------------------------------------------------------------------

    def create_visualization(
        self, df: pd.DataFrame, chart_type: Optional[str] = None, title: Optional[str] = None
    ) -> Optional[str]:
        if df.empty:
            return None
        chart_type = chart_type or self.detect_chart_type(df)
        if chart_type == "none":
            return None

        plt.figure(figsize=(12, 8))
        builders = {
            "bar": self._mpl_bar,
            "line": self._mpl_line,
            "pie": self._mpl_pie,
            "histogram": self._mpl_histogram,
            "scatter": self._mpl_scatter,
        }
        try:
            builders.get(chart_type, self._mpl_bar)(df)
            if title:
                plt.title(title, fontsize=16, fontweight="bold")
            plt.tight_layout()

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.output_dir / f"{chart_type}_chart_{ts}.png"
            plt.savefig(filepath, dpi=300, bbox_inches="tight")
            plt.close()
            logger.info("Visualisation saved: %s", filepath)
            return str(filepath)
        except Exception as exc:
            logger.error("Matplotlib visualisation error: %s", exc)
            plt.close()
            return None

    # --- Matplotlib builders ---

    @staticmethod
    def _mpl_bar(df):
        if len(df.columns) >= 2:
            df.plot(x=df.columns[0], y=df.columns[1], kind="bar", color="skyblue")
            plt.xticks(rotation=45)
        else:
            df.plot(kind="bar", color="skyblue")

    @staticmethod
    def _mpl_line(df):
        if len(df.columns) >= 2:
            df.plot(x=df.columns[0], y=df.columns[1], kind="line", marker="o")
        else:
            df.plot(kind="line", marker="o")

    @staticmethod
    def _mpl_pie(df):
        if len(df.columns) >= 2:
            plt.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct="%1.1f%%")
        else:
            df.iloc[:, 0].value_counts().plot(kind="pie", autopct="%1.1f%%")

    @staticmethod
    def _mpl_histogram(df):
        num = df.select_dtypes(include=[np.number]).columns
        if len(num) > 0:
            df[num[0]].hist(bins=20, color="skyblue", alpha=0.7)
            plt.xlabel(num[0])
            plt.ylabel("Frequency")

    @staticmethod
    def _mpl_scatter(df):
        num = df.select_dtypes(include=[np.number]).columns
        if len(num) >= 2:
            plt.scatter(df[num[0]], df[num[1]], alpha=0.6, color="skyblue")
            plt.xlabel(num[0])
            plt.ylabel(num[1])
