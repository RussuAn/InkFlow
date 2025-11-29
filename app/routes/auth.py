from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.forms.auth import RegistrationForm
from app.models.user import create_user

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