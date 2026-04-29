"""Routes for exporting query results."""

import io
import logging

from flask import Blueprint, current_app, jsonify, request, send_file

logger = logging.getLogger(__name__)

export_bp = Blueprint("export", __name__)


def _services():
    return current_app.config["SERVICES"]


@export_bp.route("/api/export", methods=["POST"])
def api_export():
    s = _services()
    try:
        data = request.get_json(force=True)
        export_data = data.get("data", [])
        fmt = data.get("format", "csv")
        filename = data.get("filename", "export")

        if not export_data:
            return jsonify({"success": False, "error": "No data to export"}), 400

        exp = s["export"]
        content = exp.export(export_data, fmt, filename)
        safe_name = exp.sanitize_filename(filename)

        return send_file(
            io.BytesIO(content),
            mimetype=exp.CONTENT_TYPES.get(fmt, "text/plain"),
            as_attachment=True,
            download_name=f"{safe_name}.{exp.EXTENSIONS.get(fmt, 'txt')}",
        )
    except Exception as exc:
        logger.error("api/export error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
