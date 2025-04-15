import secrets
import string
from flask import abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app import db


class UserService:
    @staticmethod
    def change_password(user_id: int, new_password: str) -> bool:
        user = User.query.get_or_404(user_id)

        # Проверка новый пароль совпадает со старым
        if check_password_hash(user.password, new_password):
            raise ValueError(f"Current password match with previous password")

        user.password = generate_password_hash(new_password)
        db.session.commit()
        return True

    @staticmethod
    def delete_user(user_id: int) -> bool:
        user = User.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def add_user(username: str, email: str, password: str = None) -> str:
        # Проверка на такой же username
        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username:
            raise ValueError(f"User {username}: already exists ({user_by_username.id})")

        # Проверка на такой же email
        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            raise ValueError(f"User {email}: already exists ({user_by_email.id})")

        # Если пароль не задан, генерируем
        if password is None:
            password = UserService.generate_secure_password()

        hashed_password = generate_password_hash(password)
        try:
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
            )
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(400, description="Error while adding user to the database.")
        return password

    @staticmethod
    def generate_secure_password(length: int = 12):
        """Генерирует безопасный случайный пароль"""
        # Символы для пароля
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password