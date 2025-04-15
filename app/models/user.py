from app import db
from datetime import datetime, UTC
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))
    password = db.Column(db.String(200), nullable=False)

    roles = db.relationship("UserRole", back_populates="user")

    @property
    def is_admin(self):
        return any(role.role.name == "admin" for role in self.roles)