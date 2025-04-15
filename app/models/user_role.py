from app import db
import enum

class AccessLevel(enum.Enum):
    viewer = 1
    editor = 2
    admin = 3

class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete="CASCADE"), nullable=False)
    access_level = db.Column(db.Enum(AccessLevel), nullable=False)

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")