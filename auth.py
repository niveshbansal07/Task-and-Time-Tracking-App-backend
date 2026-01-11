import jwt
from datetime import datetime
from flask import current_app
from functools import wraps
from flask import request, jsonify

def create_access_token(user_id):
    payload = {
        "user_id":user_id,
        "exp":datetime.utcnow() + current_app.config["JWT_ACCESS_EXPIRES"]
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")

def create_refresh_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + current_app.config["JWT_REFRESH_EXPIRES"],
        "type": "refresh"
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def verify_token(token):
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"]
    )

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Missing Authorization header"}), 401
        

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            return jsonify({"message": "Invalid Authorization format"}), 401

        token = parts[1]

        try:
            decoded = verify_token(token)

            request.user_id = decoded["user_id"]
        
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        
        return fn(*args, **kwargs)
    return wrapper