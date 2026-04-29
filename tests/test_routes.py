"""Integration tests hitting Flask routes via the test client."""

import json
import pytest


class TestQueryRoutes:
    def test_get_schema(self, client):
        resp = client.get("/api/schema")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "schema" in data

    def test_get_models(self, client):
        resp = client.get("/api/models")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "models" in data

    def test_execute_sql_select(self, client):
        resp = client.post("/api/execute-sql", json={
            "sql_query": "SELECT * FROM employees",
            "natural_query": "show all employees",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert len(data["data"]) == 5


class TestDatabaseRoutes:
    def test_current_db(self, client):
        resp = client.get("/api/db/current")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "current_db" in data

    def test_connect_path_traversal_blocked(self, client):
        resp = client.post("/api/db/connect-path", json={"path": "../../etc/passwd"})
        data = resp.get_json()
        assert data["success"] is False


class TestSimilarityRoutes:
    def test_similarity_check_empty(self, client):
        resp = client.post("/api/similarity-check", json={"query": "random unknown query"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True


class TestExportRoutes:
    def test_export_csv(self, client):
        resp = client.post("/api/export", json={
            "data": [{"name": "Alice", "salary": 95000}],
            "format": "csv",
            "filename": "test",
        })
        assert resp.status_code == 200
