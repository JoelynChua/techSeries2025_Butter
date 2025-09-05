from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, QUIZQN_TABLE

bp = Blueprint("quiz", __name__)

@bp.route("/quizqn", methods=["GET"])
def get_quizqn():
    """
    Get quizqn entries
    ---
    tags:
      - quizqn
    parameters:
      - in: query
        name: id
        type: integer
        required: false
        description: Return a single row by id
        example: 123
    responses:
      200: {description: Row or list of rows}
      404: {description: Row not found (when id provided)}
      500: {description: Server error}
    """
    try:
        cols = ["id", "sleephours", "workhours", "exercisehours", "sleepquality", "mood", "connectwithfamily"]

        q_id = request.args.get("id", type=int)
        if q_id is not None:
            resp = supabase.table(QUIZQN_TABLE).select(",".join(cols)).eq("id", q_id).limit(1).execute()
            data = exec_data(resp)
            if not data:
                return jsonify({"error": "Row not found"}), 404
            return jsonify({"row": data[0]}), 200

        resp = supabase.table(QUIZQN_TABLE).select(",".join(cols)).order("id", desc=True).execute()
        rows = exec_data(resp) or []
        return jsonify({"rows": rows, "count": len(rows)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
