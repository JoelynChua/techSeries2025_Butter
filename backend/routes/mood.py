from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, MOOD_TABLE

bp = Blueprint("mood", __name__)

@bp.route("/moodMetric", methods=["GET"])
def get_mood_metrics():
    """
    Get mood metric(s)
    ---
    tags:
      - moodMetric
    parameters:
      - in: query
        name: id
        type: integer
        required: false
        description: Get a single row by id
        example: 123
      - in: query
        name: userId
        type: integer
        required: false
        description: Filter by userId
        example: 42
    responses:
      200: {description: List or single mood metric (all fields)}
      404: {description: Row not found (when id is provided)}
      500: {description: Server error}
    """
    try:
        q_id = request.args.get("id", type=int)
        user_id = request.args.get("userId", type=int)

        if q_id is not None:
            resp = supabase.table(MOOD_TABLE).select("*").eq("id", q_id).limit(1).execute()
            data = exec_data(resp)
            if not data:
                return jsonify({"error": "Row not found"}), 404
            return jsonify({"row": data[0]}), 200

        query = supabase.table(MOOD_TABLE).select("*")
        if user_id is not None:
            query = query.eq("userId", user_id)
        resp = query.execute()
        rows = exec_data(resp) or []
        return jsonify({"rows": rows}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/moodMetric", methods=["POST"])
def create_mood_metric():
    """
    Create a mood metric entry
    ---
    tags:
      - moodMetric
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [userId]
          properties:
            userId: {type: integer, example: 42}
            sleepHours: {type: integer, example: 7}
            exerciseHours: {type: integer, example: 1}
            workingHrs: {type: integer, example: 8}
            mood: {type: string, example: "Calm / content"}
            sleepQuality: {type: string, example: "Good"}
            finalMoodScores: {type: string, example: "73"}
            created_timestamp: {type: string, example: "2025-09-02 21:30:00"}
            connectwithfamily: {type: boolean, example: true}
    responses:
      201: {description: Created mood metric}
      400: {description: Missing required fields}
      500: {description: Server error}
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("userId")
    if user_id is None:
        return jsonify({"error": "Missing userId"}), 400

    # backward compat for "excerciseHours"
    exercise_hours = data.get("exerciseHours", data.get("excerciseHours"))

    payload = {
        "userId": user_id,
        "sleepHours": data.get("sleepHours"),
        "exerciseHours": exercise_hours,   # ✅ fixed bug: use parsed value
        "workingHrs": data.get("workingHrs"),
        "mood": data.get("mood"),
        "sleepQuality": data.get("sleepQuality"),
        "finalMoodScores": data.get("finalMoodScores"),
        "created_timestamp": data.get("created_timestamp"),
        "connectwithfamily": data.get("connectwithfamily"),
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        resp = supabase.table(MOOD_TABLE).insert(payload).execute()
        created = exec_data(resp)
        return jsonify({"message": "Created", "row": created[0] if created else None}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/moodMetric", methods=["PUT"])
def update_mood_metric():
    """
    Update a mood metric entry by id
    ---
    tags:
      - moodMetric
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [id]
          properties:
            id: {type: integer, example: 123}
            userId: {type: integer, example: 42}
            sleepHours: {type: integer, example: 7}
            exerciseHours: {type: integer, example: 2}
            workingHrs: {type: integer, example: 9}
            mood: {type: string, example: "Stressed / anxious"}
            sleepQuality: {type: string, example: "Poor"}
            finalMoodScores: {type: string, example: "65"}
            created_timestamp: {type: string, example: "2025-09-02 22:00:00"}
            connectwithfamily: {type: boolean, example: false}
    responses:
      200: {description: Updated mood metric}
      400: {description: Missing id or no fields to update}
      404: {description: Row not found}
      500: {description: Server error}
    """
    data = request.get_json(silent=True) or {}
    row_id = data.get("id")
    if row_id is None:
        return jsonify({"error": "Missing id"}), 400

    exercise_hours = data.get("exerciseHours", data.get("excerciseHours"))

    fields = {
        "userId": data.get("userId"),
        "sleepHours": data.get("sleepHours"),
        "exerciseHours": exercise_hours,
        "workingHrs": data.get("workingHrs"),
        "mood": data.get("mood"),
        "sleepQuality": data.get("sleepQuality"),
        "finalMoodScores": data.get("finalMoodScores"),
        "created_timestamp": data.get("created_timestamp"),
        "connectwithfamily": data.get("connectwithfamily"),
    }
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    try:
        resp = supabase.table(MOOD_TABLE).update(fields).eq("id", row_id).execute()
        updated = exec_data(resp)
        if not updated:
            return jsonify({"error": "Row not found"}), 404
        return jsonify({"message": "Updated", "row": updated[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
