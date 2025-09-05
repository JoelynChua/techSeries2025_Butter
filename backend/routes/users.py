from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, USERS_TABLE
from core.users_repo import get_user_by_id, update_user_fields_by_id, row_to_public_user

bp = Blueprint("users", __name__)

@bp.route("/userProfile", methods=["GET"])
def get_user_profile():
    """
    Get user profile by userId
    ---
    tags:
      - users
    parameters:
      - in: query
        name: userId
        required: true
        type: integer
        example: 12345
    responses:
      200: {description: User profile}
      400: {description: Missing userId}
      404: {description: User not found}
    """
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(row_to_public_user(user)), 200


@bp.route("/userProfile", methods=["PUT"])
def update_user_profile():
    """
    Update user profile (by userId)
    ---
    tags:
      - users
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
            userId: {type: integer, example: 12345}
            email: {type: string}
            password: {type: string}
            username: {type: string}
            mobile: {type: string}
    responses:
      200: {description: Updated user}
      400: {description: Missing userId or no fields to update}
      404: {description: User not found}
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    fields = {
        "email": data.get("email"),
        "password": data.get("password"),  # TODO: hash in production
        "username": data.get("username"),
        "mobile": data.get("mobile"),
    }
    updated = update_user_fields_by_id(user_id, fields)
    if not updated:
        return jsonify({"error": "No fields to update"}), 400

    return jsonify(row_to_public_user(updated)), 200


@bp.route("/users", methods=["GET"])
def get_all_users():
    """
    Get all users (public info only)
    ---
    tags:
      - users
    responses:
      200: {description: List of all users}
      500: {description: Server error}
    """
    try:
        resp = supabase.table(USERS_TABLE).select("*").order("userId", desc=True).execute()
        rows = exec_data(resp) or []
        public_rows = [row_to_public_user(r) for r in rows if r]
        return jsonify({"rows": public_rows, "count": len(public_rows)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
