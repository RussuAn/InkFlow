from flask import Blueprint, render_template, request, jsonify, url_for
from flask_login import login_required, current_user
from app.models.book import get_book_by_id
from app.core.db import get_db
from app.models.library import add_to_shelf, get_user_book_status

bp = Blueprint('reader', __name__)

@bp.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return "Книгу не знайдено", 404

    if current_user.is_authenticated:
        status = get_user_book_status(current_user.id, book_id)
        if status != 'completed':
            add_to_shelf(current_user.id, book_id, 'reading')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT current_page FROM reading_progress WHERE user_id = %s AND book_id = %s",
        (current_user.id, book_id)
    )
    result = cursor.fetchone()
    cursor.close()
    
    start_page = result['current_page'] if result else 1
    
    return render_template('reader/read.html', 
                           book=book, 
                           start_page=start_page)

@bp.route('/api/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    book_id = data.get('book_id')
    page = data.get('page')
    total_pages = data.get('total_pages')
    try:
        page = int(page)
        total_pages = int(total_pages)
    except (ValueError, TypeError):
        return jsonify({'status': 'error'}), 400

    db = get_db()
    cursor = db.cursor()

    query = """
        INSERT INTO reading_progress (user_id, book_id, chapter_id, current_page, total_pages)
        VALUES (%s, %s, 0, %s, %s)
        ON DUPLICATE KEY UPDATE current_page = %s, total_pages = %s
    """
    cursor.execute(query, (current_user.id, book_id, page, total_pages, page, total_pages))
    
    db.commit()
    cursor.close()
        
    return jsonify({'status': 'success'})

@bp.route('/api/finish_book', methods=['POST'])
@login_required
def finish_book():
    data = request.get_json()
    book_id = data.get('book_id')
    
    if add_to_shelf(current_user.id, book_id, 'completed'):
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 500