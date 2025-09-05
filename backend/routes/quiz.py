from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, QUIZQN_TABLE  # make QUIZQN_TABLE = "questions"

bp = Blueprint("quiz", __name__)

@bp.route("/quizqn", methods=["GET"])
def get_quizqn():
    """
    Get question catalog entries (from the CSV-backed table)
    ---
    tags:
      - questions
    parameters:
      - in: query
        name: id
        type: integer
        required: false
        description: Return a single question by numeric id
        example: 3
      - in: query
        name: key
        type: string
        required: false
        description: Return a single question by key (e.g., 'sleep_hours')
        example: sleep_hours
      - in: query
        name: section
        type: string
        required: false
        description: Filter by section (e.g., 'daily', 'weekly')
        example: daily
      - in: query
        name: include_inactive
        type: boolean
        required: false
        description: Include inactive questions (default false)
        example: false
    responses:
      200: {description: Row or list of rows}
      404: {description: Row not found (when id/key provided)}
      500: {description: Server error}
    """
    try:
        # Columns that exist in your CSV/table
        cols = [
            "id",
            "key",
            "prompt",
            "input_type",
            "unit",
            "min_value",
            "max_value",
            "step",
            "scale_positive_high",
            "required",
            "section",
            "display_order",
            "active",
        ]

        q_id = request.args.get("id", type=int)
        q_key = request.args.get("key", type=str)
        section = request.args.get("section", default="daily", type=str)
        include_inactive = request.args.get("include_inactive", default="false").lower() in ("1", "true", "yes")

        # Fetch a single row by id or key
        if q_id is not None or q_key:
            query = supabase.table(QUIZQN_TABLE).select(",".join(cols))
            if q_id is not None:
                query = query.eq("id", q_id)
            if q_key:
                query = query.eq("key", q_key)

            # If caller didn't ask for inactive, enforce active==true
            if not include_inactive:
                query = query.eq("active", True)

            resp = query.limit(1).execute()
            data = exec_data(resp)
            if not data:
                return jsonify({"error": "Row not found"}), 404
            return jsonify({"row": data[0]}), 200

        # List query: filter by section and active, order by display_order ASC
        query = supabase.table(QUIZQN_TABLE).select(",".join(cols))
        if section:
            query = query.eq("section", section)
        if not include_inactive:
            query = query.eq("active", True)

        resp = query.order("display_order", desc=False).execute()
        rows = exec_data(resp) or []
        return jsonify({"rows": rows, "count": len(rows)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
