"""Tests for SimilarityService (FAISS)."""

import pytest
from backend.services.similarity import SimilarityService


class TestSimilarityService:
    @pytest.fixture
    def svc(self, tmp_path):
        return SimilarityService(data_dir=str(tmp_path))

    def test_add_and_find(self, svc):
        svc.add_query("Show all employees", "SELECT * FROM employees")
        results = svc.find_similar("show employees")
        assert len(results) >= 1
        assert results[0]["query"]["sql_query"] == "SELECT * FROM employees"

    def test_find_no_match(self, svc):
        results = svc.find_similar("quantum physics formulas")
        assert results == []

    def test_clear_cache(self, svc):
        svc.add_query("test query", "SELECT 1")
        stats_before = svc.get_cache_stats()
        assert stats_before["total_queries"] >= 1
        svc.clear_cache()
        stats_after = svc.get_cache_stats()
        assert stats_after["total_queries"] == 0

    def test_swap_entities_simple(self, svc):
        svc.add_query("Show employees in Engineering", "SELECT * FROM employees WHERE department='Engineering'")
        adapted = svc.swap_entities(
            original_query="Show employees in Engineering",
            new_query="Show employees in Marketing",
            original_sql="SELECT * FROM employees WHERE department='Engineering'",
        )
        assert "Marketing" in adapted["adapted_sql"]
