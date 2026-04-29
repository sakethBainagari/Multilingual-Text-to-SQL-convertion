"""Database access layer – connection management, schema, execution."""

import logging
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from backend.models.query_result import QueryResult

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages SQLite connections, schema introspection, and query execution."""

    def __init__(self, db_path: str = "data/advanced_nlsql.db"):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Ensure DB file exists
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        conn.close()

        self._create_sample_schema()
        logger.info("DatabaseService initialised: %s", self.db_path)

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def _create_sample_schema(self) -> None:
        """Create sample tables (employees, departments, projects) if absent."""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing = [r[0] for r in cur.fetchall()]

            if "employees" not in existing:
                cur.execute(
                    """
                    CREATE TABLE employees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        department TEXT,
                        salary REAL,
                        hire_date DATE,
                        email TEXT,
                        phone TEXT,
                        age INTEGER,
                        experience_years INTEGER
                    )
                    """
                )
                cur.executemany(
                    """INSERT INTO employees
                       (name,department,salary,hire_date,email,phone,age,experience_years)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    [
                        ("John Doe", "Engineering", 75000, "2023-01-15", "john.doe@company.com", "555-0101", 32, 5),
                        ("Jane Smith", "Marketing", 65000, "2023-02-20", "jane.smith@company.com", "555-0102", 28, 3),
                        ("Mike Johnson", "Engineering", 80000, "2023-01-10", "mike.johnson@company.com", "555-0103", 35, 8),
                        ("Sarah Wilson", "HR", 60000, "2023-03-05", "sarah.wilson@company.com", "555-0104", 30, 4),
                        ("David Brown", "Finance", 70000, "2023-02-15", "david.brown@company.com", "555-0105", 33, 6),
                        ("Lisa Garcia", "Engineering", 78000, "2023-01-25", "lisa.garcia@company.com", "555-0106", 29, 4),
                        ("Robert Lee", "Marketing", 62000, "2023-03-10", "robert.lee@company.com", "555-0107", 27, 2),
                        ("Emily Davis", "HR", 58000, "2023-02-28", "emily.davis@company.com", "555-0108", 26, 2),
                    ],
                )

            if "departments" not in existing:
                cur.execute(
                    """
                    CREATE TABLE departments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        budget REAL,
                        manager_name TEXT,
                        location TEXT,
                        established_date DATE
                    )
                    """
                )
                cur.executemany(
                    """INSERT INTO departments
                       (name,budget,manager_name,location,established_date)
                       VALUES (?,?,?,?,?)""",
                    [
                        ("Engineering", 500000, "Mike Johnson", "Building A", "2020-01-01"),
                        ("Marketing", 200000, "Jane Smith", "Building B", "2020-01-01"),
                        ("HR", 150000, "Sarah Wilson", "Building C", "2020-01-01"),
                        ("Finance", 300000, "David Brown", "Building B", "2020-01-01"),
                        ("Sales", 250000, "Tom Anderson", "Building A", "2020-06-01"),
                    ],
                )

            if "projects" not in existing:
                cur.execute(
                    """
                    CREATE TABLE projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        department TEXT,
                        budget REAL,
                        start_date DATE,
                        end_date DATE,
                        status TEXT
                    )
                    """
                )
                cur.executemany(
                    """INSERT INTO projects
                       (name,department,budget,start_date,end_date,status)
                       VALUES (?,?,?,?,?,?)""",
                    [
                        ("Website Redesign", "Marketing", 50000, "2024-01-01", "2024-06-30", "In Progress"),
                        ("Mobile App Development", "Engineering", 120000, "2024-02-01", "2024-12-31", "In Progress"),
                        ("HR System Upgrade", "HR", 30000, "2024-03-01", "2024-08-31", "Planning"),
                        ("Financial Audit", "Finance", 25000, "2024-01-15", "2024-04-15", "Completed"),
                        ("Customer Portal", "Engineering", 80000, "2024-04-01", "2024-10-31", "Planning"),
                    ],
                )

            conn.commit()
            conn.close()
            logger.info("Sample schema checked/created successfully")
        except Exception as exc:
            logger.error("Error creating sample schema: %s", exc)

    def get_comprehensive_schema(self) -> Dict[str, Dict]:
        """Return ``{table: {columns: {...}, row_count: N}}`` for every table."""
        schema: Dict[str, Dict] = {}
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]

            for table in tables:
                cur.execute(f"PRAGMA table_info({table})")
                columns = cur.fetchall()
                schema[table] = {"columns": {}, "row_count": 0}
                for col in columns:
                    col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                    schema[table]["columns"][col_name] = {
                        "type": col_type,
                        "not_null": bool(not_null),
                        "default": default,
                        "primary_key": bool(pk),
                    }
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                schema[table]["row_count"] = cur.fetchone()[0]

            conn.close()
        except Exception as exc:
            logger.error("Error getting schema: %s", exc)
        return schema

    # ------------------------------------------------------------------
    # SQL safety check
    # ------------------------------------------------------------------

    @staticmethod
    def is_safe_sql(sql: str) -> bool:
        """Block dangerous DDL like DROP DATABASE, ATTACH, etc."""
        dangerous = re.compile(
            r"\b(DROP\s+DATABASE|ATTACH|DETACH|PRAGMA\s+(?!table_info|foreign_keys))\b",
            re.IGNORECASE,
        )
        return not bool(dangerous.search(sql))

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_sql(self, sql_query: str) -> QueryResult:
        """Execute *sql_query* and return a :class:`QueryResult`."""
        start = datetime.now()

        if not self.is_safe_sql(sql_query):
            return QueryResult(
                success=False,
                data=None,
                sql_query=sql_query,
                execution_time=0.0,
                error_message="Blocked: query contains disallowed statements",
            )

        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            try:
                if sql_query.strip().upper().startswith("SELECT"):
                    data = pd.read_sql_query(sql_query, conn)
                else:
                    cur = conn.cursor()
                    cur.execute(sql_query)
                    conn.commit()
                    affected = cur.rowcount

                    # --- CI fallback for UPDATE with 0 affected rows ---
                    if affected == 0 and sql_query.strip().upper().startswith("UPDATE"):
                        data = self._ci_update_fallback(conn, cur, sql_query, affected)
                    else:
                        data = pd.DataFrame({"affected_rows": [affected]})

                    # Post-process DML to return meaningful rows
                    data = self._postprocess_dml(conn, cur, sql_query, data)
            finally:
                conn.close()

            elapsed = (datetime.now() - start).total_seconds()
            return QueryResult(success=True, data=data, sql_query=sql_query, execution_time=elapsed)

        except Exception as exc:
            elapsed = (datetime.now() - start).total_seconds()
            logger.error("SQL execution error: %s", exc)
            return QueryResult(
                success=False,
                data=None,
                sql_query=sql_query,
                execution_time=elapsed,
                error_message=str(exc),
            )

    # ------------------------------------------------------------------
    # DML post-processing helpers
    # ------------------------------------------------------------------

    def _ci_update_fallback(self, conn, cur, sql_query: str, affected: int) -> pd.DataFrame:
        """Attempt a case-insensitive UPDATE when the original matched 0 rows."""
        try:
            m = re.match(
                r"UPDATE\s+([a-zA-Z_]\w*)\s+SET\s+(.*?)\s+WHERE\s+(.+)",
                sql_query.strip().rstrip(";"),
                re.IGNORECASE | re.DOTALL,
            )
            if not m:
                return pd.DataFrame({"affected_rows": [affected]})

            tbl, set_clause, where_raw = m.group(1), m.group(2).strip(), m.group(3).strip().rstrip(";")
            ci_where = re.sub(
                r"([a-zA-Z_]\w*)\s*=\s*'([^']*)'",
                lambda x: f"lower({x.group(1)}) = lower('{x.group(2)}')",
                where_raw,
            )
            ids_df = pd.read_sql_query(f"SELECT rowid FROM {tbl} WHERE {ci_where}", conn)
            if ids_df is not None and not ids_df.empty:
                ids_list = ",".join(str(int(r)) for r in ids_df["rowid"])
                cur.execute(f"UPDATE {tbl} SET {set_clause} WHERE rowid IN ({ids_list})")
                conn.commit()
                updated = pd.read_sql_query(f"SELECT * FROM {tbl} WHERE rowid IN ({ids_list})", conn)
                return updated
        except Exception as exc:
            logger.debug("CI update fallback failed: %s", exc)
        return pd.DataFrame({"affected_rows": [affected]})

    def _postprocess_dml(self, conn, cur, sql_query: str, data: pd.DataFrame) -> pd.DataFrame:
        """After INSERT / UPDATE / DELETE, try to return the affected rows."""
        sql_norm = sql_query.strip().rstrip(";")
        try:
            # INSERT
            ins_m = re.match(r"INSERT\s+INTO\s+([a-zA-Z_]\w*)", sql_norm, re.IGNORECASE)
            if ins_m:
                tbl = ins_m.group(1)
                lastrowid = getattr(cur, "lastrowid", None)
                if lastrowid and int(lastrowid) > 0:
                    try:
                        return pd.read_sql_query(f"SELECT * FROM {tbl} WHERE rowid = {int(lastrowid)}", conn)
                    except Exception:
                        pass
                affected = max(cur.rowcount, 1)
                return pd.read_sql_query(f"SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT {affected}", conn)

            # UPDATE
            upd_m = re.match(
                r"UPDATE\s+([a-zA-Z_]\w*)\s+SET\s+(.*?)\s+WHERE\s+(.+)",
                sql_norm,
                re.IGNORECASE | re.DOTALL,
            )
            if upd_m:
                tbl = upd_m.group(1)
                set_clause = upd_m.group(2).strip()
                where_raw = upd_m.group(3).strip().rstrip(";")

                updated_cols = {
                    m.group(1).lower()
                    for m in re.finditer(r"([a-zA-Z_]\w*)\s*=", set_clause)
                }
                parts = [
                    p.strip()
                    for p in re.split(r"\s+AND\s+", where_raw, flags=re.IGNORECASE)
                ]
                kept = []
                for p in parts:
                    cm = re.match(r"([a-zA-Z_]\w*)\s*=", p)
                    if cm and cm.group(1).lower() in updated_cols:
                        continue
                    kept.append(p)

                if kept:
                    sel = f"SELECT * FROM {tbl} WHERE {' AND '.join(kept)}"
                    df = pd.read_sql_query(sel, conn)
                    if df is not None and not df.empty:
                        return df
                return pd.read_sql_query(
                    f"SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT 100", conn
                )

            # DELETE
            del_m = re.match(r"DELETE\s+FROM\s+([a-zA-Z_]\w*)", sql_norm, re.IGNORECASE)
            if del_m:
                tbl = del_m.group(1)
                return pd.read_sql_query(
                    f"SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT 100", conn
                )

        except Exception as exc:
            logger.debug("DML post-processing failed: %s", exc)
        return data
