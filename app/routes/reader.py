# InkFlow/app/routes/reader.py

from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from app.models.book import get_book_by_id
from app.models.library import add_to_shelf, get_user_book_status

bp = Blueprint('reader', __name__)

@bp.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = get_book_by_id(book_id)
    if not book: return "Книгу не знайдено", 404

    # При відкритті ставимо "Читаю" (якщо ще не прочитано)
    if current_user.is_authenticated:
        status = get_user_book_status(current_user.id, book_id)
        if status != 'completed':
            add_to_shelf(current_user.id, book_id, 'reading')
    
    return render_template('reader/read.html', book=book)

# Новий простий маршрут для кнопки "Завершити"
@bp.route('/api/finish_book', methods=['POST'])
@login_required
def finish_book():
    data = request.get_json()
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'status': 'error', 'message': 'No ID'}), 400
        
    # Просто ставимо статус completed
    if add_to_shelf(current_user.id, book_id, 'completed'):
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'}), 500