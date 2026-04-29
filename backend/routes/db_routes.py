"""Routes for database management (upload, switch, connect-by-path, delete)."""

import logging
import os
import sqlite3
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger(__name__)

db_bp = Blueprint("db", __name__)


def _services():
    return current_app.config["SERVICES"]


def _get_uploaded_databases():
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "data/uploads")
    dbs = []
    if os.path.exists(upload_dir):
        for f in os.listdir(upload_dir):
            if f.endswith((".db", ".sqlite", ".sqlite3")):
                path = os.path.join(upload_dir, f)
                dbs.append({
                    "name": f,
                    "path": path,
                    "size": os.path.getsize(path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                })
    return dbs


# ------------------------------------------------------------------
# Current DB info
# ------------------------------------------------------------------

@db_bp.route("/api/db/current", methods=["GET"])
def api_db_current():
    s = _services()
    try:
        db_path = s["db"].db_path
        db_name = current_app.config.get("CURRENT_DB_NAME", "Default Database")
        tables = []
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [r[0] for r in cur.fetchall()]
            conn.close()
        except Exception as exc:
            logger.warning("Could not read tables: %s", exc)

        return jsonify({
            "success": True,
            "current_db": {
                "name": db_name,
                "path": db_path,
                "tables": tables,
                "table_count": len(tables),
            },
            "uploaded_databases": _get_uploaded_databases(),
        })
    except Exception as exc:
        logger.error("api/db/current error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Connect by path (with basic path-traversal guard)
# ------------------------------------------------------------------

@db_bp.route("/api/db/connect-path", methods=["POST"])
def api_db_connect_path():
    s = _services()
    try:
        data = request.get_json(force=True)
        db_path = (data.get("path") or "").strip()
        if not db_path:
            return jsonify({"success": False, "error": "Path not provided"}), 400

        db_path = os.path.normpath(db_path)

        # Basic path-traversal guard: reject obvious traversal sequences
        if ".." in db_path:
            return jsonify({"success": False, "error": "Path traversal not allowed"}), 403

        if not os.path.exists(db_path):
            return jsonify({"success": False, "error": f"File not found: {db_path}"}), 404

        # Validate SQLite
        try:
            test_conn = sqlite3.connect(db_path)
            cur = test_conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            test_conn.close()
            if not tables:
                return jsonify({"success": False, "error": "Database contains no tables"}), 400
        except sqlite3.DatabaseError as exc:
            return jsonify({"success": False, "error": f"Invalid SQLite file: {exc}"}), 400

        s["db"].db_path = db_path
        current_app.config["CURRENT_DB_NAME"] = os.path.basename(db_path) + " (Direct)"
        schema = s["db"].get_comprehensive_schema()

        logger.info("Connected directly to: %s", db_path)
        return jsonify({
            "success": True,
            "message": f'Connected to "{os.path.basename(db_path)}"',
            "database": {
                "name": current_app.config["CURRENT_DB_NAME"],
                "path": db_path,
                "tables": list(schema.keys()),
                "table_count": len(schema),
            },
        })
    except Exception as exc:
        logger.error("api/db/connect-path error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Upload
# ------------------------------------------------------------------

@db_bp.route("/api/db/upload", methods=["POST"])
def api_db_upload():
    s = _services()
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "data/uploads")
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        f = request.files["file"]
        if f.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in (".db", ".sqlite", ".sqlite3"):
            return jsonify({"success": False, "error": f"Invalid type. Allowed: .db, .sqlite, .sqlite3"}), 400

        filename = f.filename.replace(" ", "_")
        filepath = os.path.join(upload_dir, filename)
        f.save(filepath)

        # Validate
        try:
            tc = sqlite3.connect(filepath)
            cur = tc.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            tc.close()
            if not tables:
                os.remove(filepath)
                return jsonify({"success": False, "error": "Uploaded file has no tables"}), 400
        except sqlite3.DatabaseError as exc:
            os.remove(filepath)
            return jsonify({"success": False, "error": f"Invalid SQLite file: {exc}"}), 400

        s["db"].db_path = filepath
        current_app.config["CURRENT_DB_NAME"] = filename
        schema = s["db"].get_comprehensive_schema()

        logger.info("Switched to uploaded DB: %s", filename)
        return jsonify({
            "success": True,
            "message": f'Database "{filename}" uploaded and activated',
            "database": {
                "name": filename,
                "path": filepath,
                "tables": list(schema.keys()),
                "table_count": len(schema),
            },
        })
    except Exception as exc:
        logger.error("api/db/upload error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Switch
# ------------------------------------------------------------------

@db_bp.route("/api/db/switch", methods=["POST"])
def api_db_switch():
    s = _services()
    default_path = current_app.config.get("DEFAULT_DB_PATH", "data/advanced_nlsql.db")
    try:
        data = request.get_json(force=True)
        db_path = data.get("path", "")
        if not db_path:
            return jsonify({"success": False, "error": "Path not provided"}), 400

        if db_path == "default":
            db_path = default_path
            db_name = "Default Database"
        else:
            if not os.path.exists(db_path):
                return jsonify({"success": False, "error": "File not found"}), 404
            db_name = os.path.basename(db_path)

        s["db"].db_path = db_path
        current_app.config["CURRENT_DB_NAME"] = db_name
        schema = s["db"].get_comprehensive_schema()

        logger.info("Switched to: %s", db_name)
        return jsonify({
            "success": True,
            "message": f'Switched to "{db_name}"',
            "database": {
                "name": db_name,
                "path": db_path,
                "tables": list(schema.keys()),
                "table_count": len(schema),
            },
        })
    except Exception as exc:
        logger.error("api/db/switch error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Delete
# ------------------------------------------------------------------

@db_bp.route("/api/db/delete", methods=["POST"])
def api_db_delete():
    s = _services()
    default_path = current_app.config.get("DEFAULT_DB_PATH", "data/advanced_nlsql.db")
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "data/uploads")
    try:
        data = request.get_json(force=True)
        db_path = data.get("path", "")
        if not db_path:
            return jsonify({"success": False, "error": "Path not provided"}), 400
        if db_path == default_path:
            return jsonify({"success": False, "error": "Cannot delete the default database"}), 403
        if not db_path.startswith(upload_dir):
            return jsonify({"success": False, "error": "Can only delete uploaded databases"}), 403
        if not os.path.exists(db_path):
            return jsonify({"success": False, "error": "File not found"}), 404

        # If deleting the active DB, switch to default
        if db_path == s["db"].db_path:
            s["db"].db_path = default_path
            current_app.config["CURRENT_DB_NAME"] = "Default Database"

        os.remove(db_path)
        logger.info("Deleted database: %s", db_path)
        return jsonify({"success": True, "message": "Database deleted"})
    except Exception as exc:
        logger.error("api/db/delete error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


# ------------------------------------------------------------------
# Schema viewer
# ------------------------------------------------------------------

@db_bp.route("/api/db/schema", methods=["GET"])
def api_db_schema():
    """Return full schema of the current database for the floating viewer."""
    s = _services()
    try:
        db_path = s["db"].db_path
        db_name = current_app.config.get("CURRENT_DB_NAME", "Default Database")
        schema = s["db"].get_comprehensive_schema()

        # Build a clean response
        tables_info = []
        for table_name, table_data in schema.items():
            columns = []
            for col_name, col_info in table_data.get("columns", {}).items():
                columns.append({
                    "name": col_name,
                    "type": col_info.get("type", "TEXT"),
                    "primary_key": col_info.get("primary_key", False),
                    "not_null": col_info.get("not_null", False),
                    "default": col_info.get("default"),
                })
            tables_info.append({
                "name": table_name,
                "row_count": table_data.get("row_count", 0),
                "columns": columns,
            })

        return jsonify({
            "success": True,
            "database": db_name,
            "path": db_path,
            "table_count": len(tables_info),
            "tables": tables_info,
        })
    except Exception as exc:
        logger.error("api/db/schema error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
