"""Routes for similarity checking and entity swapping."""

import logging

from flask import Blueprint, current_app, jsonify, request

logger = logging.getLogger(__name__)

similarity_bp = Blueprint("similarity", __name__)


def _services():
    return current_app.config["SERVICES"]


@similarity_bp.route("/api/similarity", methods=["POST"])
def api_similarity():
    s = _services()
    sim = s.get("similarity")
    try:
        data = request.get_json(force=True)
        query = (data.get("query") or "").strip()
        if not query:
            return jsonify({"success": False, "error": "Query cannot be empty"}), 400

        if sim is None:
            return jsonify({"success": True, "found_similar": False, "message": "Similarity disabled"})

        results = sim.find_similar(query)
        if results:
            best = results[0]
            return jsonify({
                "success": True,
                "found_similar": True,
                "similarity_score": best["similarity"],
                "similar_query": best["query"]["natural_query"],
                "cached_sql": best["query"]["sql_query"],
                "use_cached": best["similarity"] > 0.95,
            })
        return jsonify({"success": True, "found_similar": False, "message": "No similar queries found"})

    except Exception as exc:
        logger.error("api/similarity error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@similarity_bp.route("/api/similarity-check", methods=["POST"])
def api_similarity_check():
    s = _services()
    sim = s.get("similarity")
    try:
        data = request.get_json(force=True)
        query = (data.get("query") or "").strip()
        if not query:
            return jsonify({"success": False, "error": "Query cannot be empty"}), 400

        if sim is None:
            return jsonify({"success": True, "similar_queries": [], "count": 0, "message": "Similarity disabled"})

        results = sim.find_similar(query, threshold=0.85)
        logger.info("Similarity check for '%s' – %d matches", query, len(results))
        return jsonify({"success": True, "similar_queries": results, "count": len(results)})

    except Exception as exc:
        logger.error("api/similarity-check error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500


@similarity_bp.route("/api/swap-entities", methods=["POST"])
def api_swap_entities():
    s = _services()
    sim = s.get("similarity")
    try:
        data = request.get_json(force=True)
        orig_q = (data.get("original_query") or "").strip()
        new_q = (data.get("new_query") or "").strip()
        orig_sql = (data.get("original_sql") or "").strip()

        if not all([orig_q, new_q, orig_sql]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        if sim is None:
            return jsonify({
                "success": True,
                "adapted_sql": orig_sql,
                "swapped": False,
                "structural_change": False,
                "message": "Similarity disabled – returning original SQL",
            })

        result = sim.swap_entities(orig_q, new_q, orig_sql)
        return jsonify({
            "success": True,
            "adapted_sql": result["adapted_sql"],
            "original_sql": orig_sql,
            "swapped": result["swapped"],
            "structural_change": result["structural_change"],
            "message": result["message"],
        })

    except Exception as exc:
        logger.error("api/swap-entities error: %s", exc)
        return jsonify({"success": False, "error": str(exc)}), 500
