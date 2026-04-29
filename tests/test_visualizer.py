"""Tests for VisualizationEngine."""

import pytest
import pandas as pd
from backend.services.visualizer import VisualizationEngine


class TestVisualizationEngine:
    @pytest.fixture
    def viz(self, tmp_path):
        return VisualizationEngine(output_dir=str(tmp_path))

    def test_detect_bar_chart(self, viz):
        df = pd.DataFrame({"department": ["Eng", "HR", "Mkt"], "count": [10, 5, 8]})
        chart = viz.detect_chart_type(df)
        assert chart in viz.SUPPORTED_CHART_TYPES

    def test_detect_pie_chart(self, viz):
        df = pd.DataFrame({"category": ["A", "B", "C"], "value": [30, 50, 20]})
        chart = viz.detect_chart_type(df)
        assert chart in viz.SUPPORTED_CHART_TYPES

    def test_detect_single_column(self, viz):
        df = pd.DataFrame({"salary": [50000, 60000, 70000, 80000]})
        chart = viz.detect_chart_type(df)
        assert chart == "histogram"
