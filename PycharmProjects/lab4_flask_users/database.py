from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Модель роли пользователя
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    # Связь с пользователями
    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name}>'


# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100))
    first_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с ролью
    role = db.relationship('Role', back_populates='users')

    @property
    def full_name(self):
        """Возвращает ФИО пользователя"""
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        if self.first_name:
            parts.append(self.first_name)
        if self.patronymic:
            parts.append(self.patronymic)
        return ' '.join(parts) if parts else 'Не указано'

    @property
    def short_name(self):
        """Возвращает фамилию с инициалами"""
        if not self.first_name:
            return self.last_name or 'Не указано'

        if self.last_name:
            name = f"{self.last_name} {self.first_name[0]}."
            if self.patronymic:
                name += f"{self.patronymic[0]}."
            return name
        return self.first_name

    def __repr__(self):
        return f'<User {self.username}>'