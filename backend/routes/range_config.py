from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, RANGE_CONFIG_TABLE

bp = Blueprint("range_config", __name__)

@bp.route("/rangeConfig", methods=["GET"])
def get_range_config():
    """
    Get range configuration entries by field_name
    ---
    tags:
      - rangeConfig
    parameters:
      - in: query
        name: field_name
        type: string
        required: true
        description: Return rows that match this field_name
        example: workhours
    responses:
      200: {description: List of matching rows}
      400: {description: Missing field_name}
      404: {description: No rows found}
      500: {description: Server error}
    """
    try:
        cols = ["id", "min_value", "max_value", "step_value", "field_name"]
        field_name = request.args.get("field_name")
        if not field_name:
            return jsonify({"error": "Missing field_name"}), 400

        resp = supabase.table(RANGE_CONFIG_TABLE).select(",".join(cols)).eq("field_name", field_name).execute()
        rows = exec_data(resp) or []
        if not rows:
            return jsonify({"error": "No rows found"}), 404

        return jsonify({"rows": rows, "count": len(rows)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
