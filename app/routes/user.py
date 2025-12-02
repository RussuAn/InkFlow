import os
import secrets
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user, logout_user

from app.forms.profile import EditProfileForm
from app.forms.settings import ChangePasswordForm, DeleteAccountForm
from app.forms.support import ContactForm

from app.models.user import update_user_profile, update_password, delete_user
from app.models.library import get_books_by_shelf, get_gifted_books
from app.models.commerce import top_up_balance
from app.models.support import create_message

bp = Blueprint('user', __name__, url_prefix='/user')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    
    picture_path = os.path.join(
        current_app.root_path, 
        'frontend', 
        'static', 
        'uploads', 
        'avatars', 
        picture_fn
    )

    form_picture.save(picture_path)
    return picture_fn


@bp.route('/profile')
@login_required
def profile():
    if current_user.avatar_url:
        avatar_file = url_for('static', filename='uploads/avatars/' + current_user.avatar_url)
    else:
        avatar_file = f"https://ui-avatars.com/api/?name={current_user.username}&background=random&size=128"

    books_reading = get_books_by_shelf(current_user.id, 'reading')
    books_completed = get_books_by_shelf(current_user.id, 'completed')
    books_planned = get_books_by_shelf(current_user.id, 'planned')
    books_gifted = get_gifted_books(current_user.id)

    return render_template(
        'user/profile.html', 
        user=current_user,
        avatar_file=avatar_file,
        books_reading=books_reading,
        books_completed=books_completed,
        books_planned=books_planned,
        books_gifted=books_gifted
    )


@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    
    if form.validate_on_submit():
        picture_file = None
        if form.avatar.data:
            picture_file = save_picture(form.avatar.data)

        avatar_to_save = picture_file if picture_file else None

        if update_user_profile(
            current_user.id, 
            form.username.data, 
            form.display_name.data,
            form.bio.data, 
            avatar_to_save
        ):
            current_app.logger.info(f"Користувач {current_user.username} (ID: {current_user.id}) оновив профіль.")
            flash('Профіль оновлено!', 'success')
            return redirect(url_for('user.profile'))
        else:
            current_app.logger.error(f"Помилка оновлення профілю для користувача {current_user.id}.")
            flash('Помилка при оновленні.', 'error')

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name
        form.bio.data = current_user.bio

    return render_template('user/edit_profile.html', form=form)


@bp.route('/wallet/topup', methods=['GET', 'POST'])
@login_required
def topup():
    if request.method == 'POST':
        amount = int(request.form.get('amount'))
        
        if top_up_balance(current_user.id, amount):
            current_app.logger.info(f"Користувач {current_user.id} поповнив баланс на {amount} монет.")
            flash(f'Оплата пройшла успішно! Баланс поповнено на {amount} 🪙.', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('user.profile'))
        else:
            current_app.logger.error(f"Помилка транзакції поповнення для користувача {current_user.id}.")
            flash('Помилка транзакції.', 'error')
            
    return render_template('user/payment.html')


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    pass_form = ChangePasswordForm()
    del_form = DeleteAccountForm()

    if pass_form.validate_on_submit() and 'new_password' in request.form:
        if current_user.check_password(pass_form.old_password.data):
            if update_password(current_user.id, pass_form.new_password.data):
                current_app.logger.info(f"Користувач {current_user.id} змінив пароль.")
                flash('Пароль успішно змінено!', 'success')
                return redirect(url_for('user.settings'))
            else:
                current_app.logger.error(f"Помилка БД при зміні пароля користувача {current_user.id}.")
                flash('Помилка бази даних.', 'error')
        else:
            current_app.logger.warning(f"Невдала спроба зміни пароля користувача {current_user.id} (невірний старий пароль).")
            flash('Старий пароль введено невірно.', 'error')

    if del_form.validate_on_submit() and 'Видалити' in del_form.submit.label.text:
        user_id = current_user.id
        username = current_user.username
        
        delete_user(user_id)
        logout_user()
        
        current_app.logger.info(f"Акаунт користувача {username} (ID: {user_id}) було видалено.")
        flash('Ваш акаунт видалено. Нам шкода, що ви йдете.', 'info')
        return redirect(url_for('index'))

    return render_template('user/settings.html', pass_form=pass_form, del_form=del_form)


@bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        if create_message(current_user.id, form.subject.data, form.message.data):
            current_app.logger.info(f"Користувач {current_user.id} надіслав повідомлення у підтримку.")
            flash('Ваше повідомлення надіслано адміністрації!', 'success')
            return redirect(url_for('user.profile'))
        else:
            current_app.logger.error(f"Помилка відправки повідомлення від користувача {current_user.id}.")
            flash('Сталася помилка при відправленні.', 'error')
            
    return render_template('support/contact.html', form=form)