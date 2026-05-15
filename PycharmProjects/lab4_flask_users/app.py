from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from database import db, User, Role
from models import UserLogin
from forms import UserValidator

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация БД
db.init_app(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо авторизоваться.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin.get(int(user_id))


# Контекстный процессор для передачи текущего пользователя в шаблоны
@app.context_processor
def inject_user():
    return dict(current_user=current_user)


# Создание таблиц БД
with app.app_context():
    db.create_all()

    # Создание начальных ролей, если их нет
    if not Role.query.first():
        roles = [
            Role(name='Администратор', description='Полный доступ к системе'),
            Role(name='Пользователь', description='Обычный пользователь'),
            Role(name='Гость', description='Ограниченный доступ')
        ]
        for role in roles:
            db.session.add(role)
        db.session.commit()


@app.route('/')
def index():
    """Главная страница со списком пользователей"""
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(UserLogin(user), remember=remember)
            flash('Вы успешно вошли в систему!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль!', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


@app.route('/user/<int:user_id>')
def user_view(user_id):
    """Просмотр пользователя (доступен всем)"""
    user = User.query.get_or_404(user_id)
    return render_template('user_view.html', user=user)


@app.route('/user/create', methods=['GET', 'POST'])
@login_required
def user_create():
    """Создание нового пользователя (только для авторизованных)"""
    roles = Role.query.all()
    errors = {}
    form_data = {}

    if request.method == 'POST':
        form_data = {
            'username': request.form.get('username', ''),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
            'last_name': request.form.get('last_name', ''),
            'first_name': request.form.get('first_name', ''),
            'patronymic': request.form.get('patronymic', ''),
            'role_id': request.form.get('role_id')
        }

        # Валидация
        errors = {}

        # Проверка обязательных полей
        required_errors = UserValidator.validate_required_fields(
            form_data, ['username', 'password', 'confirm_password', 'first_name']
        )
        errors.update(required_errors)

        # Проверка логина
        if 'username' not in errors:
            is_valid, username_errors = UserValidator.validate_username(form_data['username'])
            if not is_valid:
                errors['username'] = username_errors[0]
            elif User.query.filter_by(username=form_data['username']).first():
                errors['username'] = 'Пользователь с таким логином уже существует'

        # Проверка пароля
        if 'password' not in errors and 'confirm_password' not in errors:
            is_valid, password_errors = UserValidator.validate_password(
                form_data['password'], form_data['confirm_password']
            )
            if not is_valid:
                errors['password'] = password_errors[0] if password_errors else 'Неверный формат пароля'

        if not errors:
            try:
                # Создание пользователя
                user = User(
                    username=form_data['username'],
                    password_hash=generate_password_hash(form_data['password']),
                    last_name=form_data['last_name'],
                    first_name=form_data['first_name'],
                    patronymic=form_data['patronymic'],
                    role_id=form_data['role_id'] if form_data['role_id'] else None
                )
                db.session.add(user)
                db.session.commit()

                flash(f'Пользователь {user.full_name} успешно создан!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')

    return render_template('user_form.html',
                           roles=roles,
                           errors=errors,
                           form_data=form_data,
                           action='create')


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    """Редактирование пользователя (только для авторизованных)"""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    errors = {}
    form_data = {}

    if request.method == 'POST':
        form_data = {
            'last_name': request.form.get('last_name', ''),
            'first_name': request.form.get('first_name', ''),
            'patronymic': request.form.get('patronymic', ''),
            'role_id': request.form.get('role_id')
        }

        # Проверка обязательных полей
        required_errors = UserValidator.validate_required_fields(
            form_data, ['first_name']
        )
        errors.update(required_errors)

        if not errors:
            try:
                user.last_name = form_data['last_name']
                user.first_name = form_data['first_name']
                user.patronymic = form_data['patronymic']
                user.role_id = form_data['role_id'] if form_data['role_id'] else None

                db.session.commit()

                flash(f'Данные пользователя {user.full_name} обновлены!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Ошибка при обновлении пользователя: {str(e)}', 'danger')
    else:
        form_data = {
            'last_name': user.last_name or '',
            'first_name': user.first_name or '',
            'patronymic': user.patronymic or '',
            'role_id': str(user.role_id) if user.role_id else ''
        }

    return render_template('user_form.html',
                           user=user,
                           roles=roles,
                           errors=errors,
                           form_data=form_data,
                           action='edit')


@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def user_delete(user_id):
    """Удаление пользователя (только для авторизованных)"""
    user = User.query.get_or_404(user_id)

    try:
        full_name = user.full_name
        db.session.delete(user)
        db.session.commit()
        flash(f'Пользователь {full_name} успешно удален!', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')

    return redirect(url_for('index'))


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Смена пароля текущего пользователя"""
    errors = {}

    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Проверка старого пароля
        user = User.query.get(current_user.id)
        if not check_password_hash(user.password_hash, old_password):
            errors['old_password'] = 'Неверный текущий пароль'

        # Проверка нового пароля
        if 'old_password' not in errors:
            is_valid, password_errors = UserValidator.validate_password(new_password, confirm_password)
            if not is_valid:
                errors['new_password'] = password_errors[0] if password_errors else 'Неверный формат пароля'

        if not errors:
            try:
                user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Пароль успешно изменен!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash(f'Ошибка при смене пароля: {str(e)}', 'danger')

    return render_template('change_password.html', errors=errors)


if __name__ == '__main__':
    app.run(debug=True)