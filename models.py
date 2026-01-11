from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    # relation
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(255), nullable=False)

    # time tracking (seconds)
    present_seconds = db.Column(db.Integer, default=0)
    today_seconds = db.Column(db.Integer, default=0)
    today_date = db.Column(db.Date, nullable=True)

    status = db.Column(
        db.Enum("pending", "in_progress", "success", name="task_status"),
        default="pending"
    )

    running = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "present_seconds": self.present_seconds,
            "today_seconds": self.today_seconds,
            "status": self.status,
            "running": self.running,
            "started_at": self.started_at.isoformat() if self.started_at else None
        }
