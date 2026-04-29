"""Tests for ExportService."""

import json
import pytest
import pandas as pd
from backend.services.export_service import ExportService


class TestExportService:
    @pytest.fixture
    def svc(self):
        return ExportService()

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({
            "name": ["Alice", "Bob"],
            "salary": [95000, 72000],
        })

    def test_export_csv(self, svc, sample_df, tmp_path):
        resp = svc.export(sample_df, "csv", "test", str(tmp_path))
        assert resp is not None
        content = resp.get_data(as_text=True)
        assert "Alice" in content
        assert "Bob" in content

    def test_export_json(self, svc, sample_df, tmp_path):
        resp = svc.export(sample_df, "json", "test", str(tmp_path))
        data = json.loads(resp.get_data(as_text=True))
        assert len(data) == 2

    def test_export_excel(self, svc, sample_df, tmp_path):
        resp = svc.export(sample_df, "excel", "test", str(tmp_path))
        assert resp is not None
        # Check content type
        assert "spreadsheet" in resp.content_type or "excel" in resp.content_type

    def test_sanitize_filename(self, svc):
        assert svc.sanitize_filename("my file!@#.csv") == "my_file.csv"
        assert svc.sanitize_filename("") == "export"
