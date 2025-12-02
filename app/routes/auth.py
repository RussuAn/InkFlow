from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user

from app.forms.auth import RegistrationForm, LoginForm
from app.models.user import create_user, get_user_by_email, update_user_streak, get_user_by_username


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        if create_user(form.username.data, form.email.data, form.password.data, form.display_name.data):
            user = get_user_by_username(form.username.data)
            
            if user:
                login_user(user)
                update_user_streak(user.id)
                current_app.logger.info(f"Новий користувач зареєстрований та автоматично увійшов: {user.username}")
                flash(f'Ласкаво просимо, {user.display_name}! Ваш акаунт створено.', 'success')

                return redirect(url_for('index'))
            
        else:
            current_app.logger.error(f"Помилка при створенні акаунту: {form.username.data}")
            flash('Сталася помилка при створенні акаунту. Спробуйте ще раз.', 'error')

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        login_id = form.email_or_username.data
        
        user = get_user_by_email(login_id)
        if not user:
            user = get_user_by_username(login_id)

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            
            new_streak = update_user_streak(user.id)
            current_app.logger.info(f"Користувач увійшов: {user.username} (ID: {user.id})")

            if new_streak and new_streak > 1:
                flash(f'З поверненням! Ваш стрік: {new_streak} 🔥', 'success')
            else:
                flash('З поверненням!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            current_app.logger.warning(f"Невдала спроба входу: {login_id}")
            flash('Невірний email або пароль.', 'error')
            
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        current_app.logger.info(f"Користувач вийшов: {current_user.username}")
        
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))