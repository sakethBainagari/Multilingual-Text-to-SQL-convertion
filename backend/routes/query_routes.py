"""Routes for SQL generation, execution, schema, and model status."""

import logging
from datetime import datetime

import pandas as pd
from flask import Blueprint, current_app, jsonify, request

from backend.models.query_result import QueryResult

logger = logging.getLogger(__name__)

query_bp = Blueprint("query", __name__)


def _services():
    """Shortcut to reach services attached to the app."""
    return current_app.config["SERVICES"]


# ------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------

@query_bp.route("/api/schema", methods=["GET"])
def api_schema():
    s = _services()
    try:
        return jsonify(s["db"].get_comprehensive_schema())
    except Exception as exc:
        logger.error("api/schema error: %s", exc)
        return jsonify({}), 500


# ------------------------------------------------------------------
# Models
# ------------------------------------------------------------------

@query_bp.route("/api/models", methods=["GET"])
def api_models():
    s = _services()
    try:
        gen = s["generator"]
        import os
        return jsonify({
            "success": True,
            "current_config": gen.get_model_status(),
            "ollama_available": len(gen.get_available_ollama_models()) > 0,
            "ollama_models": gen.get_available_ollama_models() if gen.use_ollama else [],
            "gemini_available": bool(
                os.getenv("GEMINI_API_KEY")
                and os.getenv("GEMINI_API_KEY") != "your_gemini_api_key_here"
            ),
        })
    except Exception as exc:
        logger.error("api/models error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@query_bp.route("/api/ollama-models", methods=["GET"])
def api_ollama_models():
    s = _services()
    try:
        return jsonify(s["generator"].get_available_ollama_models())
    except Exception as exc:
        logger.error("api/ollama-models error: %s", exc)
        return jsonify([])


# ------------------------------------------------------------------
# Generate SQL
# ------------------------------------------------------------------

@query_bp.route("/api/generate-sql", methods=["POST"])
def api_generate_sql():
    s = _services()
    gen = s["generator"]
    try:
        data = request.get_json(force=True)
        natural_query = (data.get("query") or "").strip()
        model = data.get("model", "models/gemini-2.0-flash")
        use_ollama = data.get("use_ollama", False)

        if not natural_query:
            return jsonify({"success": False, "error": "Query cannot be empty"}), 400

        # Temporarily switch model if needed
        orig_ollama = gen.use_ollama
        orig_model = gen.ollama_model
        if use_ollama or "gemini" not in model:
            gen.use_ollama = True
            gen.ollama_model = model
        else:
            gen.use_ollama = False

        schema = s["db"].get_comprehensive_schema()
        try:
            sql_query = gen.generate_sql(natural_query, schema)
        except MemoryError as me:
            gen.use_ollama = orig_ollama
            gen.ollama_model = orig_model
            return jsonify({"success": False, "error": str(me)}), 400

        gen.use_ollama = orig_ollama
        gen.ollama_model = orig_model

        if not sql_query:
            return jsonify({"success": False, "error": "Failed to generate SQL"}), 500

        # Auto-learn: save to FAISS (after generation, before execution)
        sim = s.get("similarity")
        if sim:
            try:
                sim.add_query(
                    natural_query,
                    sql_query,
                    {"source": "llm_generated", "model": model, "generated_at": datetime.now().isoformat()},
                )
                logger.info("[AUTO-LEARN] Saved query to FAISS")
            except Exception as exc:
                logger.warning("Auto-learn failed: %s", exc)

        return jsonify({"success": True, "sql_query": sql_query, "model_used": model})

    except Exception as exc:
        logger.error("api/generate-sql error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Execute SQL
# ------------------------------------------------------------------

@query_bp.route("/api/execute-sql", methods=["POST"])
def api_execute_sql():
    s = _services()
    try:
        data = request.get_json(force=True)
        sql_query = (data.get("sql_query") or "").strip()
        natural_query = data.get("natural_query", "")
        visualize = data.get("visualize", False)
        chart_type = data.get("chart_type") or None

        if not sql_query:
            return jsonify({"success": False, "error": "SQL query cannot be empty"}), 400

        result = s["db"].execute_sql(sql_query)

        # Save to similarity index
        if result.success and natural_query:
            sim = s.get("similarity")
            if sim:
                try:
                    sim.add_query(
                        natural_query,
                        sql_query,
                        {
                            "timestamp": datetime.now().isoformat(),
                            "row_count": result.row_count,
                            "columns": list(result.data.columns) if result.data is not None else [],
                        },
                    )
                except Exception as exc:
                    logger.warning("Similarity add failed: %s", exc)

        # Visualisation
        plotly_data = None
        if visualize and result.success and result.data is not None:
            plotly_data = s["viz"].create_plotly_visualization(result.data, chart_type)

        resp = {
            "success": result.success,
            "sql_query": result.sql_query,
            "execution_time": result.execution_time,
            "data": result.data.to_dict("records") if result.data is not None else None,
            "row_count": result.row_count,
            "visualization_data": plotly_data,
            "database_used": s["db"].db_path,
        }
        if not result.success:
            resp["error"] = result.error_message
        return jsonify(resp)

    except Exception as exc:
        logger.error("api/execute-sql error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
