"""
Auth Blueprint — /api/auth/register, /api/auth/login, /api/auth/me
"""
import datetime
from functools import wraps

from bson import ObjectId
from flask import Blueprint, jsonify, request, g

from backend.db.mongo import users_col
from backend.auth.auth_utils import (
    hash_password,
    check_password,
    generate_token,
    verify_token,
)

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# JWT Middleware helper
# ---------------------------------------------------------------------------
def require_auth(f):
    """Decorator that validates Bearer JWT and sets g.user_id / g.user_name."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
        elif request.args.get("token"):
            token = request.args.get("token")

        if not token:
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        payload = verify_token(token)
        if payload is None:
            return jsonify({"error": "Token expired or invalid. Please log in again."}), 401
        g.user_id = payload["sub"]
        g.user_name = payload.get("name", "")
        g.user_email = payload.get("email", "")
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Basic validation
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email address."}), 400

    col = users_col()

    # Check duplicate email
    if col.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists."}), 409

    # Create user
    now = datetime.datetime.utcnow()
    user_doc = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": now,
        "last_login": now,
    }
    result = col.insert_one(user_doc)
    user_id = result.inserted_id

    token = generate_token(str(user_id), name, email)
    return jsonify({
        "token": token,
        "user": {"id": str(user_id), "name": name, "displayName": name, "email": email}
    }), 201


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    col = users_col()
    user = col.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401

    if not check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password."}), 401

    # Update last_login timestamp
    col.update_one({"_id": user["_id"]}, {"$set": {"last_login": datetime.datetime.utcnow()}})

    token = generate_token(str(user["_id"]), user["name"], user["email"])
    return jsonify({
        "token": token,
        "user": {"id": str(user["_id"]), "name": user["name"], "displayName": user["name"], "email": user["email"]}
    }), 200


# ---------------------------------------------------------------------------
# GET /api/auth/me  (protected)
# ---------------------------------------------------------------------------
@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    col = users_col()
    user = col.find_one({"_id": ObjectId(g.user_id)}, {"password_hash": 0})
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify({
        "id": str(user["_id"]),
        "name": user["name"],
        "displayName": user["name"],
        "email": user["email"],
        "created_at": user.get("created_at", "").isoformat() if user.get("created_at") else None,
        "last_login": user.get("last_login", "").isoformat() if user.get("last_login") else None,
    }), 200
