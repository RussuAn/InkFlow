from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.library import add_to_shelf

bp = Blueprint('library', __name__, url_prefix='/library')

@bp.route('/add/<int:book_id>/<status>')
@login_required
def update_status(book_id, status):
    allowed_statuses = ['planned', 'reading', 'completed', 'dropped']
    
    if status not in allowed_statuses:
        flash('Невірний статус полиці.', 'error')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
    if add_to_shelf(current_user.id, book_id, status):
        pass
    else:
        flash('Помилка при оновленні полиці.', 'error')
        
    return redirect(url_for('books.book_detail', book_id=book_id))