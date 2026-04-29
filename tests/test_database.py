"""Tests for DatabaseService."""

import sqlite3
import pytest
from backend.services.database import DatabaseService


class TestDatabaseService:
    def test_init_creates_sample_if_empty(self, tmp_path):
        db_path = str(tmp_path / "brand_new.db")
        svc = DatabaseService(db_path)
        schema = svc.get_comprehensive_schema()
        # Should have auto-created sample tables
        assert "employees" in schema.lower()

    def test_execute_select(self, sample_db):
        svc = DatabaseService(sample_db)
        result = svc.execute_sql("SELECT name FROM employees WHERE department='Engineering'")
        assert result["success"] is True
        names = [r["name"] for r in result["data"]]
        assert "Alice" in names
        assert "Charlie" in names

    def test_execute_count(self, sample_db):
        svc = DatabaseService(sample_db)
        result = svc.execute_sql("SELECT COUNT(*) as cnt FROM employees")
        assert result["success"] is True
        assert result["data"][0]["cnt"] == 5

    def test_is_safe_sql_blocks_dangerous(self, sample_db):
        svc = DatabaseService(sample_db)
        assert svc.is_safe_sql("SELECT * FROM employees") is True
        assert svc.is_safe_sql("DROP DATABASE test") is False
        assert svc.is_safe_sql("ATTACH DATABASE 'x' AS y") is False

    def test_execute_insert(self, sample_db):
        svc = DatabaseService(sample_db)
        result = svc.execute_sql(
            "INSERT INTO employees (id, name, department, salary) VALUES (6, 'Frank', 'HR', 60000)"
        )
        assert result["success"] is True
        # Verify insertion
        check = svc.execute_sql("SELECT * FROM employees WHERE name='Frank'")
        assert len(check["data"]) == 1

    def test_schema_contains_tables(self, sample_db):
        svc = DatabaseService(sample_db)
        schema = svc.get_comprehensive_schema()
        for table in ["employees", "departments", "projects"]:
            assert table in schema.lower()
