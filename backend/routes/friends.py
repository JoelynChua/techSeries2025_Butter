from flask import Blueprint, request, jsonify
from core.db import supabase, exec_data, FRIENDS_TABLE
from core.users_repo import get_user_by_username

bp = Blueprint("friends", __name__)

FRIEND_FIELDS = {
    "friendofuid", "username", "email", "phone",
    "relationship", "tags", "emergencycontact"
}

def _filter_friend_fields(data: dict) -> dict:
    out = {k: v for k, v in data.items() if k in FRIEND_FIELDS and v is not None}
    if "email" in out and isinstance(out["email"], str):
        out["email"] = out["email"].strip().lower()
    if "tags" in out and isinstance(out["tags"], str):
        out["tags"] = [t.strip() for t in out["tags"].split(",") if t.strip()]
    return out


@bp.route("/friends", methods=["GET"])
def getFriendsByfriendofuid():
    """
    Get friends by owner (friendofuid)
    ---
    tags:
      - friends
    parameters:
      - in: query
        name: friendofuid
        type: integer
        required: true
        example: 42
    responses:
      200: {description: List of friends}
      400: {description: Missing friendofuid}
      500: {description: Server error}
    """
    try:
        owner_id = request.args.get("friendofuid", type=int)
        if owner_id is None:
            return jsonify({"error": "Missing friendofuid"}), 400

        resp = (
            supabase.table(FRIENDS_TABLE)
            .select("*")
            .eq("friendofuid", owner_id)
            .order("id", desc=True)
            .execute()
        )
        rows = exec_data(resp) or []
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/friends", methods=["DELETE"])
def deleteFriendById():
    """
    Delete a friend by id (optionally guard by friendofuid)
    ---
    tags:
      - friends
    parameters:
      - in: query
        name: id
        type: integer
        required: true
        description: Friend row id to delete
        example: 123
      - in: query
        name: friendofuid
        type: integer
        required: false
        description: (Optional) Ensure the row belongs to this owner
        example: 42
    responses:
      200: {description: Deleted}
      400: {description: Missing id}
      404: {description: Row not found or owner mismatch}
      500: {description: Server error}
    """
    try:
        row_id = request.args.get("id", type=int)
        owner  = request.args.get("friendofuid", type=int)

        if row_id is None:
            return jsonify({"error": "Missing id"}), 400

        q = supabase.table(FRIENDS_TABLE).select("id, friendofuid").eq("id", row_id).limit(1)
        if owner is not None:
            q = q.eq("friendofuid", owner)

        exists_resp = q.execute()
        exists_rows = exec_data(exists_resp) or []
        if not exists_rows:
            return jsonify({"error": "Row not found"}), 404

        del_q = supabase.table(FRIENDS_TABLE).delete().eq("id", row_id)
        if owner is not None:
            del_q = del_q.eq("friendofuid", owner)

        del_resp = del_q.execute()
        _ = exec_data(del_resp)

        return jsonify({"message": "Deleted", "id": row_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/friends", methods=["POST"])
def addFriend():
    """
    Add a new friend (username must already exist in users table)
    ---
    tags:
      - friends
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [friendofuid, username]
          properties:
            friendofuid: {type: integer, example: 42}
            username: {type: string, example: "Maria Tan"}
            email: {type: string, example: "maria@example.com"}
            phone: {type: string, example: "+65 8123 4567"}
            relationship: {type: string, example: "classmate"}
            tags:
              type: array
              items: {type: string}
              description: text[]; pass array or comma-separated string
              example: ["gym", "study"]
            emergencycontact: {type: boolean, example: false}
    responses:
      201: {description: Created}
      400: {description: Validation error}
      404: {description: Username not found in users}
      500: {description: Server error}
    """
    try:
        body = request.get_json(silent=True) or {}
        if body.get("friendofuid") is None:
            return jsonify({"error": "friendofuid is required"}), 400
        if not body.get("username"):
            return jsonify({"error": "username is required"}), 400

        # Ensure the username exists in the users table
        user_row = get_user_by_username(body["username"])
        if not user_row:
            return jsonify({"error": "username not found in users"}), 404

        payload = _filter_friend_fields(body)
        resp = supabase.table(FRIENDS_TABLE).insert(payload).execute()
        created = exec_data(resp)
        return jsonify({"message": "Created", "row": created[0] if created else None}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/friends", methods=["PUT"])
def updateFriendDetailsByid():
    """
    Update friend details by id
    ---
    tags:
      - friends
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
            friendofuid: {type: integer, example: 42}
            username: {type: string, example: "Maria T."}
            email: {type: string}
            phone: {type: string}
            relationship: {type: string}
            tags:
              type: array
              items: {type: string}
              description: text[]; array or comma-separated string accepted
            emergencycontact: {type: boolean}
    responses:
      200: {description: Updated}
      400: {description: Missing id or no fields to update}
      404: {description: Row not found}
      500: {description: Server error}
    """
    try:
        body = request.get_json(silent=True) or {}
        row_id = body.get("id")
        if row_id is None:
            return jsonify({"error": "Missing id"}), 400

        fields = _filter_friend_fields(body)
        if not fields:
            return jsonify({"error": "No fields to update"}), 400

        resp = supabase.table(FRIENDS_TABLE).update(fields).eq("id", row_id).execute()
        updated = exec_data(resp)
        if not updated:
            return jsonify({"error": "Row not found"}), 404

        return jsonify({"message": "Updated", "row": updated[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
