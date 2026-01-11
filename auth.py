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
