from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.auth import RegistrationForm, LoginForm
from app.models.user import create_user, get_user_by_email

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        if create_user(form.username.data, form.email.data, form.password.data):
            flash('Акаунт успішно створено! Тепер ви можете увійти.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Сталася помилка при створенні акаунту. Спробуйте ще раз.', 'error')

    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('З поверненням!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Невірний email або пароль.', 'error')
            
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Ви вийшли з системи.', 'info')
    return redirect(url_for('index'))