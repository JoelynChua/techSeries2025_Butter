from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, MASCOT_TABLE

bp = Blueprint("encouragement", __name__)

@bp.route("/mascotWords", methods=["GET"])
def get_encouragement():
    """
    Get encouragement words by feeling
    ---
    tags:
      - encouragement
    parameters:
      - in: query
        name: feeling
        type: string
        required: true
        description: Return encouragement words that match this feeling
        example: sad
    responses:
      200: {description: Matching encouragement words}
      400: {description: Missing feeling}
      404: {description: No rows found}
      500: {description: Server error}
    """
    try:
        feeling = request.args.get("feeling")
        if not feeling:
            return jsonify({"error": "Missing feeling"}), 400

        resp = supabase.table(MASCOT_TABLE).select("id, feeling, encourageWords").eq("feeling", feeling).execute()
        rows = exec_data(resp) or []
        if not rows:
            return jsonify({"error": "No rows found"}), 404

        words = [row["encourageWords"] for row in rows if row.get("encourageWords")]
        return jsonify({"feeling": feeling, "encourageWords": words}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/encouragementAll", methods=["GET"])
def get_all_encouragement():
    """
    Get all encouragement entries
    ---
    tags:
      - encouragement
    responses:
      200: {description: List of all encouragement rows}
      500: {description: Server error}
    """
    try:
        resp = supabase.table(MASCOT_TABLE).select("id, feeling, encourageWords").order("id", desc=True).execute()
        rows = exec_data(resp) or []
        return jsonify({"rows": rows, "count": len(rows)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
