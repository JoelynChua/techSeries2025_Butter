from flask import Blueprint, request, jsonify
from core.users_repo import (
    get_user_by_email,
    create_user,
    row_to_public_user,
)

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["POST"])
def login():
    """
    Login (custom users table)
    ---
    tags:
      - auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email: {type: string, example: user@example.com}
            password: {type: string, example: mypassword123}
    responses:
      200: {description: Logged in}
      400: {description: Missing or bad request}
      401: {description: Invalid credentials}
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = get_user_by_email(email)
    if not user or user.get("password") != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": row_to_public_user(user)}), 200


@bp.route("/signup", methods=["POST"])
def signup():
    """
    Sign up (create user)
    ---
    tags:
      - auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email: {type: string, example: newuser@example.com}
            password: {type: string, example: StrongPass123}
            username: {type: string, example: New User}
            mobile: {type: string, example: "+65 9123 4567"}
    responses:
      201: {description: User created}
      400: {description: Missing or bad request}
      409: {description: Email already exists}
    """
    from core.users_repo import get_user_by_email  # local import to avoid circular hints

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    mobile = data.get("mobile")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({"error": "Email already exists"}), 409

    created = create_user(email=email, password=password, username=username, mobile=mobile)
    return jsonify({"message": "User created", "user": row_to_public_user(created)}), 201
