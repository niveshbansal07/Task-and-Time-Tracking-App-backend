from flask import Flask, request, jsonify
from config import Config
from models import db, User
from flask_cors import CORS
from auth import create_access_token


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# test route
@app.route("/api/health")
def health():
    return {"status": "ok"}

# signup
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"message": "All fields required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400
    
    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully"
    }), 201

# login
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(user.id)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True)