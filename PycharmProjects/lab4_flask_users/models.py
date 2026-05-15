from flask_login import UserMixin
from database import db


class UserLogin(UserMixin):
    """Класс для Flask-Login"""

    def __init__(self, user):
        self.id = user.id
        self.user = user

    @staticmethod
    def get(user_id):
        """Получает пользователя по ID"""
        user = db.session.get(User, user_id)
        if not user:
            return None
        return UserLogin(user)

    @property
    def username(self):
        return self.user.username

    @property
    def full_name(self):
        return self.user.full_name


# Импортируем модель User из database
from database import User