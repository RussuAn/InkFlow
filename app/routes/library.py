from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.library import add_to_shelf, remove_from_shelf, get_user_book_status

bp = Blueprint('library', __name__, url_prefix='/library')

@bp.route('/add/<int:book_id>/<status>')
@login_required
def update_status(book_id, status):
    allowed_statuses = ['planned', 'reading', 'completed', 'dropped']
    
    if status not in allowed_statuses:
        flash('Невірний статус полиці.', 'error')
        return redirect(url_for('books.book_detail', book_id=book_id))

    current_status = get_user_book_status(current_user.id, book_id)
    
    if current_status == status:
        if remove_from_shelf(current_user.id, book_id):
            flash('Книгу видалено з полиці.', 'info')
    else:
        if add_to_shelf(current_user.id, book_id, status):
            flash(f'Статус оновлено: {status}', 'success')
        else:
            flash('Помилка при оновленні полиці.', 'error')
        
    return redirect(url_for('books.book_detail', book_id=book_id))

@bp.route('/remove/<int:book_id>')
@login_required
def remove_book(book_id):
    if remove_from_shelf(current_user.id, book_id):
        flash('Книгу видалено з полиці.', 'info')
    else:
        flash('Помилка при видаленні.', 'error')
    return redirect(url_for('books.book_detail', book_id=book_id))