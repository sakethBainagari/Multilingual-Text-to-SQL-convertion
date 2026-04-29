"""SQL generation via Gemini / Ollama with fallback heuristics."""

import logging
import os
import re
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Optional Gemini import
try:
    import google.generativeai as genai

    HAS_GENAI = True
except ImportError:
    genai = None  # type: ignore[assignment]
    HAS_GENAI = False


class SQLGeneratorService:
    """Generate SQL from natural language using Gemini or Ollama."""

    def __init__(self):
        load_dotenv()

        # Ollama config
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "mistral:latest")

        ollama_ok = False
        if self.use_ollama:
            if self._test_ollama_connection():
                logger.info("Ollama model '%s' configured (OFFLINE)", self.ollama_model)
                ollama_ok = True
            else:
                logger.warning("Ollama not available, will use Gemini")
                self.use_ollama = False

        # Gemini config
        self.gemini_model = None
        if HAS_GENAI:
            try:
                api_key = os.getenv("GEMINI_API_KEY")
                if api_key and api_key != "your_gemini_api_key_here":
                    genai.configure(api_key=api_key)
                    try:
                        self.gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")
                        logger.info("Gemini configured: models/gemini-2.0-flash")
                    except Exception:
                        self.gemini_model = genai.GenerativeModel("models/gemini-flash-latest")
                        logger.info("Gemini configured: models/gemini-flash-latest")
                else:
                    if not ollama_ok:
                        logger.warning("No AI model configured (no Gemini key, no Ollama)")
            except Exception as exc:
                logger.error("Gemini setup error: %s", exc)

        # Lightweight health-check
        self._startup_gemini_healthcheck()

    # ------------------------------------------------------------------
    # Ollama helpers
    # ------------------------------------------------------------------

    def _test_ollama_connection(self) -> bool:
        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                names = [m.get("name", "") for m in resp.json().get("models", [])]
                if self.ollama_model in names:
                    return True
                logger.error("Ollama model '%s' not found. Available: %s", self.ollama_model, names)
            return False
        except Exception as exc:
            logger.error("Ollama connection test failed: %s", exc)
            return False

    def get_available_ollama_models(self):
        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                return [m.get("name", "") for m in resp.json().get("models", [])]
        except Exception as exc:
            logger.error("Failed to get Ollama models: %s", exc)
        return []

    def get_model_status(self) -> Dict[str, Any]:
        status: Dict[str, Any] = {
            "similarity_model": {
                "name": "paraphrase-multilingual-MiniLM-L12-v2",
                "type": "offline",
                "purpose": "Query similarity matching",
                "status": "active",
            }
        }
        if self.use_ollama:
            status["llm_model"] = {
                "name": self.ollama_model,
                "type": "offline (Ollama)",
                "purpose": "NL to SQL",
                "status": "active" if self._test_ollama_connection() else "error",
                "base_url": self.ollama_base_url,
            }
        elif self.gemini_model:
            status["llm_model"] = {
                "name": "models/gemini-2.0-flash",
                "type": "online (Google AI)",
                "purpose": "NL to SQL",
                "status": "active",
            }
        else:
            status["llm_model"] = {
                "name": "None",
                "type": "not configured",
                "purpose": "NL to SQL",
                "status": "error",
            }
        return status

    # ------------------------------------------------------------------
    # Health-check
    # ------------------------------------------------------------------

    def _startup_gemini_healthcheck(self):
        if self.use_ollama or not self.gemini_model:
            return
        try:
            prompt = "Return the single token: OK"
            try:
                resp = self.gemini_model.generate_content(prompt, max_output_tokens=1)
            except TypeError:
                resp = self.gemini_model.generate_content(prompt)
            txt = getattr(resp, "text", None) or str(resp)
            logger.info("Gemini health-check OK: %s", repr(txt)[:80])
        except Exception as exc:
            msg = str(exc).lower()
            if "quota" in msg or "429" in msg:
                logger.warning("Gemini health-check: quota/rate-limit detected")
            elif "api key" in msg or "invalid" in msg or "unauthorized" in msg:
                logger.warning("Gemini health-check: API key invalid")
            else:
                logger.warning("Gemini health-check failed: %s", exc)

    # ------------------------------------------------------------------
    # Public generation API
    # ------------------------------------------------------------------

    def generate_sql(self, natural_query: str, schema: Dict) -> Optional[str]:
        """Generate SQL from *natural_query* using whichever model is configured."""
        if self.use_ollama:
            sql = self._generate_with_ollama(natural_query, schema)
            if sql:
                return sql
            logger.warning("Ollama failed, falling back to Gemini")

        if self.gemini_model:
            return self._generate_with_gemini(natural_query, schema)

        logger.error("No AI model available")
        return None

    # ------------------------------------------------------------------
    # Ollama generation
    # ------------------------------------------------------------------

    def _generate_with_ollama(self, query: str, schema: Dict) -> Optional[str]:
        try:
            schema_info = self._format_schema(schema)
            prompt = self._build_ollama_prompt(query, schema_info)
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.9, "num_predict": 300},
            }
            resp = requests.post(
                f"{self.ollama_base_url}/api/generate", json=payload, timeout=120
            )
            if resp.status_code == 200:
                sql = self._clean_sql(resp.json().get("response", "").strip())
                logger.info("[OK] Ollama SQL: %s", sql)
                return sql
            logger.error("Ollama API error: %s", resp.status_code)
        except requests.exceptions.Timeout:
            logger.error("Ollama timeout (120s)")
        except Exception as exc:
            logger.error("Ollama error: %s", exc)
        return None

    # ------------------------------------------------------------------
    # Gemini generation (with retries)
    # ------------------------------------------------------------------

    def _generate_with_gemini(self, query: str, schema: Dict) -> Optional[str]:
        max_attempts = 3
        backoff_base = 1.5
        schema_info = self._format_schema(schema)
        prompt = self._build_gemini_prompt(query, schema_info)

        for attempt in range(1, max_attempts + 1):
            try:
                cfg = genai.types.GenerationConfig(
                    temperature=0.1, top_p=0.95, top_k=40, max_output_tokens=512
                )
                resp = self.gemini_model.generate_content(prompt, generation_config=cfg)
                sql = self._clean_sql(resp.text.strip())

                if self._validate_intent(query, sql, schema):
                    logger.info("Gemini SQL: %s", sql)
                    return sql

                logger.warning("Gemini SQL doesn't match intent: %s", sql)
                # Retry with clarification
                sql2 = self._clarify_gemini(prompt, query, cfg)
                if sql2:
                    return sql2

            except Exception as exc:
                logger.error("Gemini attempt %d error: %s", attempt, exc)
                wait = self._parse_retry_delay(str(exc)) or backoff_base ** attempt
                if attempt < max_attempts:
                    logger.info("Retrying in %.1fs", wait)
                    time.sleep(wait)

        logger.warning("Gemini failed after retries – using rule-based fallback")
        return self._fallback_sql(query, schema)

    def _clarify_gemini(self, base_prompt: str, query: str, cfg) -> Optional[str]:
        extra = f"""

Your previous response was incorrect. User asked: "{query}"

You MUST include WHERE clauses for filters, aggregation functions if asked,
GROUP BY when aggregating. NEVER return generic SELECT * LIMIT 100.
Return ONLY the SQL statement.

SQL Query:"""
        for _ in range(2):
            try:
                resp = self.gemini_model.generate_content(base_prompt + extra, generation_config=cfg)
                sql = self._clean_sql(getattr(resp, "text", "").strip())
                if sql and "NO_SQL_POSSIBLE" not in sql.upper():
                    return sql
            except Exception:
                break
        return None

    @staticmethod
    def _parse_retry_delay(msg: str) -> Optional[float]:
        m = re.search(r"retry in (\d+(?:\.\d+)?)s", msg)
        if m:
            return float(m.group(1))
        m2 = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", msg)
        if m2:
            return float(m2.group(1))
        return None

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    @staticmethod
    def _format_schema(schema: Dict) -> str:
        lines = []
        for tbl, info in schema.items():
            lines.append(f"\nTable: {tbl} (rows: {info['row_count']})")
            lines.append("Columns:")
            for col, ci in info["columns"].items():
                parts = [ci["type"]]
                if ci["primary_key"]:
                    parts.append("PRIMARY KEY")
                if ci["not_null"]:
                    parts.append("NOT NULL")
                lines.append(f"  - {col} ({', '.join(parts)})")
        return "\n".join(lines)

    @staticmethod
    def _build_ollama_prompt(query: str, schema_info: str) -> str:
        return f"""You are a SQL code generator. Generate ONLY SQL code, no explanations.

DATABASE TABLES:
{schema_info}

USER REQUEST: {query}

IMPORTANT INSTRUCTIONS:
1. If user says "show", "list", "find", "get" -> Use SELECT
2. If user says "create table" -> Use CREATE TABLE
3. If user says "add", "insert" -> Use INSERT INTO
4. If user mentions number comparison -> Use WHERE clause
5. If user says "average"/"avg" -> SELECT AVG()
6. If user says "count" -> SELECT COUNT()

SQL:"""

    @staticmethod
    def _build_gemini_prompt(query: str, schema_info: str) -> str:
        return f"""You are an expert SQL query generator. Convert natural language to precise SQLite queries.

Database Schema:
{schema_info}

Natural Language Query: "{query}"

Requirements:
1. Return ONLY valid SQLite SQL – no markdown, no explanations
2. Use exact table/column names from the schema
3. Implement ALL filters, conditions, aggregations mentioned
4. String comparisons: WHERE UPPER(column) = UPPER('value')
5. Numeric comparisons: >, <, >=, <=
6. Aggregations: AVG(), COUNT(), SUM(), MAX(), MIN()
7. NEVER return generic "SELECT * FROM table LIMIT 100"

SQL Query:"""

    # ------------------------------------------------------------------
    # Cleaning & validation
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_sql(sql: str) -> str:
        sql = re.sub(r"```sql\n?", "", sql)
        sql = re.sub(r"```\n?", "", sql)
        sql = " ".join(sql.split())

        m = re.search(
            r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b.*?;",
            sql,
            re.IGNORECASE,
        )
        if m:
            stmt = m.group(0).strip()
        else:
            m2 = re.search(
                r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b.*",
                sql,
                re.IGNORECASE,
            )
            stmt = m2.group(0).strip() if m2 else sql.strip()

        if not stmt.endswith(";"):
            stmt += ";"
        return stmt

    @staticmethod
    def _validate_intent(query: str, sql: str, schema: Dict) -> bool:
        nq, sq = query.lower(), sql.lower()

        if sq.strip().startswith(("create table", "create index", "insert into", "update ", "delete from")):
            return True
        if re.match(r"select\s+\*\s+from\s+\w+\s+limit\s+\d+;?", sq.strip()):
            return False

        agg_words = ("average", "avg", "count", "sum", "maximum", "minimum", "max", "min")
        if any(w in nq for w in agg_words):
            if not any(fn in sq for fn in ("avg(", "count(", "sum(", "max(", "min(")):
                return False

        nums = re.findall(r"\b(\d{2,})\b", nq)
        if nums and not any(n in sq for n in nums) and not any(op in sq for op in (">", "<", ">=", "<=")):
            return False

        mentioned = set()
        for info in schema.values():
            for col in info.get("columns", {}):
                if col.lower() in nq:
                    mentioned.add(col.lower())
        if mentioned and not any(c in sq for c in mentioned):
            return False

        return True

    # ------------------------------------------------------------------
    # Rule-based fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _fallback_sql(query: str, schema: Dict) -> str:
        q = query.lower()
        tbl_m = re.search(r"(employees|departments|projects|products|students)", q)
        tbl = tbl_m.group(1) if tbl_m else "employees"
        logger.info("Using fallback SELECT from '%s'", tbl)
        return f"SELECT * FROM {tbl} LIMIT 100;"
