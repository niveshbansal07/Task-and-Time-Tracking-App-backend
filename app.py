from flask import Flask, request, jsonify, Blueprint
from config import Config
from models import db, User, Task
from flask_cors import CORS
from auth import create_access_token, jwt_required
from datetime import datetime, date
from sqlalchemy import text
import pymysql
pymysql.install_as_MySQLdb()


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "https://task-and-time-tracking-app-frontend.vercel.app"}}, supports_credentials=True)

@app.route("/")
def home():
    return {"Message": "Welcome! Nivesh"}
    
# test route
@app.route("/api/health")
def health():
    return {"status": "ok"}

# db test route
@app.route("/api/db-test")
def db_test():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "db connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

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


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")
@tasks_bp.route("", methods=["GET"])
@jwt_required
def get_tasks():
    user_id = request.user_id
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id.desc()).all()
    return jsonify([t.to_dict() for t in tasks])

@tasks_bp.route("", methods=["POST"])
@jwt_required
def create_task():
    user_id = request.user_id
    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return {"error": "Task name required"}, 400

    task = Task(
        user_id=user_id,
        name=name,
        present_seconds=0,
        today_seconds=0,
        status="pending"
    )

    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    user_id = request.user_id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    data = request.get_json()

    ALLOWED_STATUS = {"pending", "in_progress", "success"}

    new_status = data.get("status")
    if new_status and new_status not in ALLOWED_STATUS:
        return {"error": "Invalid status"}, 400

    if "name" in data:
        task.name = data["name"]

    if new_status:
        task.status = new_status

    if "present_seconds" in data:
        task.present_seconds = int(data["present_seconds"])

    if "today_seconds" in data:
        task.today_seconds = int(data["today_seconds"])
        task.today_date = date.today()

    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id):
    user_id = request.user_id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deleted"}


@tasks_bp.route("/<int:task_id>/start", methods=["POST"])
@jwt_required
def start_task(task_id):
    user_id = request.user_id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()

    if task.running:
        return jsonify(task.to_dict())

    running_task = Task.query.filter_by(
        user_id=user_id,
        running=True
    ).first()

    if running_task:
        return {"message": "Another task is already running"}, 400

    task.running = True 
    task.started_at = datetime.utcnow()

    if task.today_date != date.today():
        task.today_seconds = 0
        task.today_date = date.today()

    task.status = "in_progress"
    db.session.commit()
    return jsonify(task.to_dict())

@tasks_bp.route("/<int:task_id>/stop", methods=["POST"])
@jwt_required
def stop_task(task_id):
    user_id = request.user_id
    task = Task.query.filter_by(id=task_id, user_id=user_id).first_or_404()

    if not task.running or not task.started_at:
        return jsonify(task.to_dict())

    now = datetime.utcnow()
    elapsed = int((now - task.started_at).total_seconds())

    task.present_seconds += elapsed
    # task.today_seconds += elapsed
    if task.today_date == date.today():
        task.today_seconds += elapsed
    else:
        task.today_seconds = elapsed
        task.today_date = date.today()

    task.running = False
    task.started_at = None

    db.session.commit()
    return jsonify(task.to_dict())


app.register_blueprint(tasks_bp)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

  
