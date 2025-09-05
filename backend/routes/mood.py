from flask import Blueprint, request, jsonify
from datetime import datetime
from core.db import supabase, exec_data, MOOD_TABLE
import re

bp = Blueprint("mood", __name__)

# ---------- helpers ----------
def as_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    return str(v).strip().lower() in ("1","true","t","yes","y","on")

def as_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def as_int(v):
    f = as_float(v)
    return int(f) if f is not None else None

def now_iso():
    # Seconds precision; DB usually casts to timestamptz
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ---------- endpoints ----------
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
            resp = (
                supabase.table(MOOD_TABLE)
                .select("*")
                .eq("id", q_id)
                .limit(1)
                .execute()
            )
            data = exec_data(resp)
            if not data:
                return jsonify({"error": "Row not found"}), 404
            return jsonify({"row": data[0]}), 200

        query = supabase.table(MOOD_TABLE).select("*")
        if user_id is not None:
            query = query.eq("userId", user_id)

        # Order newest first (by created_timestamp if present, else by id)
        try:
            resp = query.order("created_timestamp", desc=True).execute()
        except Exception:
            resp = query.order("id", desc=True).execute()

        rows = exec_data(resp) or []
        return jsonify({"rows": rows}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/moodMetric", methods=["POST"])
def create_mood_metric():
    """
    Create a mood metric entry (finalMoodScores computed from scoringWeights)
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("userId")
    if user_id is None:
        return jsonify({"error": "Missing userId"}), 400

    # backward compat for "excerciseHours"
    exercise_hours = data.get("exerciseHours", data.get("excerciseHours"))

    # Build typed raw_values for scoring
    raw_values = {
        "userId": as_int(user_id),
        "sleepHours": as_float(data.get("sleepHours")),
        "exerciseHours": as_float(exercise_hours),   # hours; score uses minutes internally
        "workingHrs": as_float(data.get("workingHrs")),
        "sleepQuality": as_int(data.get("sleepQuality")),  # 1-10
        "mood": as_int(data.get("mood")),                  # 1-10
        "energy": as_int(data.get("energy")),              # 1-10
        "stress": as_int(data.get("stress")),              # 1-10
        "timeOutsideMin": as_int(data.get("timeOutsideMin")),
        "connectwithfamily": as_bool(data.get("connectwithfamily")),
        "notes": data.get("notes"),
    }

    # Compute final score (0–10); ignore any client-provided value
    computed_score = compute_final_score_from_weights(raw_values)

    payload = {
        "userId": raw_values["userId"],
        "sleepHours": raw_values["sleepHours"],
        "exerciseHours": raw_values["exerciseHours"],
        "workingHrs": raw_values["workingHrs"],
        "sleepQuality": raw_values["sleepQuality"],
        "mood": raw_values["mood"],
        "energy": raw_values["energy"],
        "stress": raw_values["stress"],
        "timeOutsideMin": raw_values["timeOutsideMin"],
        "connectwithfamily": raw_values["connectwithfamily"],
        "notes": raw_values["notes"],
        "finalMoodScores": computed_score,
        "created_timestamp": data.get("created_timestamp") or now_iso(),
    }
    # Drop Nones so we don't overwrite with NULLs
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
            sleepHours: {type: number, example: 7.0}
            exerciseHours: {type: number, example: 0.5}
            workingHrs: {type: number, example: 9.0}
            sleepQuality: {type: integer, example: 5}
            mood: {type: integer, example: 6}
            energy: {type: integer, example: 6}
            stress: {type: integer, example: 4}
            timeOutsideMin: {type: integer, example: 30}
            connectwithfamily: {type: boolean, example: false}
            notes: {type: string, example: "Felt rushed"}
            finalMoodScores: {type: number, example: 6.3}
            created_timestamp: {type: string, example: "2025-09-02 22:00:00"}
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
        "userId": as_int(data.get("userId")),
        "sleepHours": as_float(data.get("sleepHours")),
        "exerciseHours": as_float(exercise_hours),
        "workingHrs": as_float(data.get("workingHrs")),
        "mood": as_int(data.get("mood")),
        "sleepQuality": as_int(data.get("sleepQuality")),
        "energy": as_int(data.get("energy")),
        "stress": as_int(data.get("stress")),
        "timeOutsideMin": as_int(data.get("timeOutsideMin")),
        "connectwithfamily": as_bool(data.get("connectwithfamily")),
        "notes": data.get("notes"),
        "finalMoodScores": as_float(data.get("finalMoodScores")),
        "created_timestamp": data.get("created_timestamp"),
    }
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    try:
        resp = supabase.table(MOOD_TABLE).update(fields).eq("id", as_int(row_id)).execute()
        updated = exec_data(resp)
        if not updated:
            return jsonify({"error": "Row not found"}), 404
        return jsonify({"message": "Updated", "row": updated[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- add near top of the file (helpers) --------------------------------------


def as_bool(v):
    if isinstance(v, bool): return v
    if v is None: return None
    return str(v).strip().lower() in ("1", "true", "t", "yes", "y", "on")

def as_float(v):
    if v is None or v == "": return None
    try: return float(v)
    except (TypeError, ValueError): return None

def as_int(v):
    f = as_float(v)
    return int(f) if f is not None else None

def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def _clamp01(x):
    return max(0.0, min(1.0, float(x)))

def _nums_in(text):
    """Extract numbers found in a free-text notes field ('peak at 8h; width=4' -> [8,4])"""
    if not text:
        return []
    return [float(n) for n in re.findall(r"[-+]?\d*\.?\d+", str(text))]

def _normalize_component(component_key, transform, direction, notes, raw_values):
    """
    Return normalized value in [0..1] for the given component or None if not applicable.
    raw_values is a dict with typed inputs pulled from the request payload.
    """
    # Map component -> input value
    # (Use minutes for exercise; others as given)
    if component_key == "mood":
        val = as_int(raw_values.get("mood"))
        if val is None: return None
        x = _clamp01(val / 10.0)
        if transform == "inverse_scale10" or direction == "negative":
            x = 1.0 - x
        return _clamp01(x)

    if component_key == "energy":
        val = as_int(raw_values.get("energy"))
        if val is None: return None
        x = _clamp01(val / 10.0)
        return _clamp01(x)

    if component_key == "stress":
        val = as_int(raw_values.get("stress"))
        if val is None: return None
        x = _clamp01(val / 10.0)
        # lower is better
        if transform in ("inverse_scale10",) or direction == "negative":
            x = 1.0 - x
        else:
            # safety: treat as negative even if transform not set correctly
            x = 1.0 - x
        return _clamp01(x)

    if component_key == "sleep_quality":
        val = as_int(raw_values.get("sleepQuality"))
        if val is None: return None
        return _clamp01(val / 10.0)

    if component_key == "sleep_hours":
        h = as_float(raw_values.get("sleepHours"))
        if h is None: return None
        nums = _nums_in(notes)
        center = nums[0] if len(nums) >= 1 else 8.0
        width  = nums[1] if len(nums) >= 2 else 4.0
        if width <= 0: width = 4.0
        return _clamp01(1.0 - abs(h - center) / width)

    if component_key == "exercise":
        # Expect minutes for scoring; convert from hours if provided
        hours = as_float(raw_values.get("exerciseHours"))
        mins = hours * 60.0 if hours is not None else None
        if mins is None: return None
        nums = _nums_in(notes)
        cap = nums[0] if len(nums) >= 1 else 45.0
        if cap <= 0: cap = 45.0
        return _clamp01(mins / cap)

    if component_key == "outside":
        mins = as_int(raw_values.get("timeOutsideMin"))
        if mins is None: return None
        nums = _nums_in(notes)
        cap = nums[0] if len(nums) >= 1 else 30.0
        if cap <= 0: cap = 30.0
        return _clamp01(mins / cap)

    if component_key == "work_balance":
        h = as_float(raw_values.get("workingHrs"))
        if h is None: return None
        nums = _nums_in(notes)
        center = nums[0] if len(nums) >= 1 else 8.0
        width  = nums[1] if len(nums) >= 2 else 4.0
        if width <= 0: width = 4.0
        return _clamp01(1.0 - abs(h - center) / width)

    if component_key == "connect":
        b = as_bool(raw_values.get("connectwithfamily"))
        if b is None: return None
        return 1.0 if b else 0.0

    # Unknown component -> ignore
    return None

def compute_final_score_from_weights(raw_values):
    """
    Pull weights from 'scoringWeights' and compute a 0–10 score (rounded to 1 dp).
    raw_values are the request fields (typed).
    """
    # Fetch weights
    try:
        resp = (
            supabase.table("scoringWeights")
            .select("component_key,weight,direction,transform,notes")
            .execute()
        )
        weight_rows = exec_data(resp) or []
    except Exception as e:
        weight_rows = []

    # Fallback defaults if table empty
    if not weight_rows:
        weight_rows = [
            {"component_key":"mood","weight":0.25,"direction":"positive","transform":"scale10","notes":"1-10"},
            {"component_key":"energy","weight":0.15,"direction":"positive","transform":"scale10","notes":"1-10"},
            {"component_key":"stress","weight":0.15,"direction":"negative","transform":"inverse_scale10","notes":"1-10"},
            {"component_key":"sleep_quality","weight":0.10,"direction":"positive","transform":"scale10","notes":"1-10"},
            {"component_key":"sleep_hours","weight":0.10,"direction":"positive","transform":"peak","notes":"peak at 8h; width=4"},
            {"component_key":"exercise","weight":0.10,"direction":"positive","transform":"saturate","notes":"45"},
            {"component_key":"outside","weight":0.05,"direction":"positive","transform":"saturate","notes":"30"},
            {"component_key":"work_balance","weight":0.07,"direction":"positive","transform":"peak","notes":"peak at 8h; width=4"},
            {"component_key":"connect","weight":0.03,"direction":"positive","transform":"boolean","notes":"1 if connected else 0"},
        ]

    num = 0.0
    den = 0.0

    for row in weight_rows:
        key = (row.get("component_key") or "").strip()
        if not key:
            continue
        try:
            w = float(row.get("weight"))
        except (TypeError, ValueError):
            continue
        if w <= 0:
            continue

        direction = (row.get("direction") or "positive").strip().lower()
        transform = (row.get("transform") or "").strip().lower()
        notes = row.get("notes")

        v = _normalize_component(key, transform, direction, notes, raw_values)
        if v is None:
            continue
        num += w * v
        den += w

    if den <= 0:
        return None

    score_0_1 = num / den
    score_0_10 = round(score_0_1 * 10.0, 1)
    return score_0_10
# --- end helpers -------------------------------------------------------------
