from app import app
from database import db, User, Role
from werkzeug.security import generate_password_hash

with app.app_context():
    # Создание тестового пользователя
    admin_role = Role.query.filter_by(name='Администратор').first()

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('Admin123!'),
            last_name='Администраторов',
            first_name='Админ',
            patronymic='Админович',
            role_id=admin_role.id if admin_role else None
        )
        db.session.add(admin)
        db.session.commit()
        print('Тестовый пользователь admin создан!')
        print('Логин: admin')
        print('Пароль: Admin123!')

    # Создание тестового пользователя
    user_role = Role.query.filter_by(name='Пользователь').first()

    if not User.query.filter_by(username='user').first():
        user = User(
            username='user',
            password_hash=generate_password_hash('User123!'),
            last_name='Пользователей',
            first_name='Обычный',
            patronymic='Пользователевич',
            role_id=user_role.id if user_role else None
        )
        db.session.add(user)
        db.session.commit()
        print('Тестовый пользователь user создан!')
        print('Логин: user')
        print('Пароль: User123!')