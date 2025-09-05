from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, LABEL_OPTIONS_TABLE

bp = Blueprint("label_options", __name__)

@bp.route("/labelOptions", methods=["GET"])
def get_fields():
    """
    Get label options by field_name
    ---
    tags:
      - labelOptions
    parameters:
      - in: query
        name: field_name
        type: string
        required: true
        description: Return rows that match this field_name
        example: sleepquality
    responses:
      200: {description: List of matching rows}
      400: {description: Missing field_name}
      404: {description: No rows found}
      500: {description: Server error}
    """
    try:
        cols = ["id", "field_name", "labelvalue"]
        field_name = request.args.get("field_name")
        if not field_name:
            return jsonify({"error": "Missing field_name"}), 400

        resp = supabase.table(LABEL_OPTIONS_TABLE).select(",".join(cols)).eq("field_name", field_name).execute()
        rows = exec_data(resp) or []
        if not rows:
            return jsonify({"error": "No rows found"}), 404

        return jsonify({"rows": rows, "count": len(rows)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
