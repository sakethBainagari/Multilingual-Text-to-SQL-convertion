"""Tests for SQLGeneratorService (with mocked LLM calls)."""

import pytest
from unittest.mock import patch, MagicMock
from backend.services.sql_generator import SQLGeneratorService


class TestSQLGenerator:
    @pytest.fixture
    def schema(self, sample_db):
        from backend.services.database import DatabaseService
        svc = DatabaseService(sample_db)
        return svc.get_comprehensive_schema()

    @pytest.fixture
    def generator(self):
        return SQLGeneratorService(gemini_api_key="fake-key")

    def test_clean_sql_removes_markdown(self, generator):
        raw = "```sql\nSELECT * FROM employees;\n```"
        cleaned = generator._clean_sql(raw)
        assert cleaned == "SELECT * FROM employees"
        assert "```" not in cleaned

    def test_clean_sql_strips_trailing_semicolon(self, generator):
        assert generator._clean_sql("SELECT 1;") == "SELECT 1"

    def test_validate_intent_select(self, generator):
        assert generator._validate_intent("Show all employees", "SELECT * FROM employees") is True

    def test_validate_intent_create(self, generator):
        assert generator._validate_intent("Create a new table xyz", "CREATE TABLE xyz (id INT)") is True

    def test_validate_intent_mismatch(self, generator):
        # asking to "show" but got a DROP → should fail
        assert generator._validate_intent("Show all employees", "DROP TABLE employees") is False

    def test_fallback_sql(self, generator):
        sql = generator._fallback_sql("Show all employees", "CREATE TABLE employees ...")
        assert sql.upper().startswith("SELECT")

    @patch("backend.services.sql_generator.requests.post")
    def test_generate_with_ollama(self, mock_post, generator):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"response": "SELECT * FROM employees"}
        mock_post.return_value = mock_resp

        sql = generator._generate_with_ollama(
            "Show all employees", "CREATE TABLE employees (id INT, name TEXT)", "mistral"
        )
        assert "SELECT" in sql.upper()
