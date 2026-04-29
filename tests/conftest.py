"""Shared fixtures for all tests."""

import os
import sys
import pytest
import sqlite3
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_db(tmp_path):
    """Create a temporary SQLite DB with sample tables."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL,
            hire_date TEXT
        );
        INSERT INTO employees VALUES (1, 'Alice', 'Engineering', 95000, '2020-01-15');
        INSERT INTO employees VALUES (2, 'Bob', 'Marketing', 72000, '2019-06-01');
        INSERT INTO employees VALUES (3, 'Charlie', 'Engineering', 88000, '2021-03-10');
        INSERT INTO employees VALUES (4, 'Diana', 'HR', 65000, '2018-11-20');
        INSERT INTO employees VALUES (5, 'Eve', 'Marketing', 70000, '2022-02-28');

        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            budget REAL
        );
        INSERT INTO departments VALUES (1, 'Engineering', 500000);
        INSERT INTO departments VALUES (2, 'Marketing', 200000);
        INSERT INTO departments VALUES (3, 'HR', 150000);

        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            status TEXT,
            budget REAL
        );
        INSERT INTO projects VALUES (1, 'Website Redesign', 'Engineering', 'In Progress', 80000);
        INSERT INTO projects VALUES (2, 'Brand Campaign', 'Marketing', 'Completed', 45000);
        INSERT INTO projects VALUES (3, 'Hiring Portal', 'HR', 'In Progress', 30000);
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def app(sample_db):
    """Create a Flask test app backed by the sample DB."""
    from backend import create_app
    test_app = create_app(db_path=sample_db)
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
