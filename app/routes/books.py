import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort, request, jsonify
from flask_login import login_required, current_user
from app.forms.book import AddBookForm
from app.models.book import create_book, get_book_by_id, search_books
from app.models.library import get_user_book_status
from app.models.commerce import purchase_book, is_book_purchased
from app.forms.review import ReviewForm
from app.models.review import add_review, get_book_reviews
from app.models.user import get_user_by_username

bp = Blueprint('books', __name__, url_prefix='/books')

def save_file(form_file, folder):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    filename = random_hex + f_ext
    file_path = os.path.join(current_app.root_path, 'frontend', 'static', 'uploads', folder, filename)
    form_file.save(file_path)
    return filename

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role != 'admin':
        flash('У вас немає прав.', 'error')
        return redirect(url_for('index'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        cover_filename = save_file(form.cover.data, 'covers')
        book_filename = save_file(form.book_file.data, 'books')
        
        if create_book(form.title.data, form.author.data, form.description.data, cover_filename, book_filename, form.price_coins.data, form.genre.data):
            flash(f'Книгу "{form.title.data}" додано!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Помилка БД.', 'error')
            
    return render_template('books/add_book.html', form=form)

@bp.route('/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if not book: abort(404)
    
    current_status = None
    is_purchased = False
    
    if current_user.is_authenticated:
        current_status = get_user_book_status(current_user.id, book.id)
        is_purchased = is_book_purchased(current_user.id, book.id)
        if book.price_coins == 0: is_purchased = True
    
    # Відгуки
    reviews = get_book_reviews(book.id)
    form = ReviewForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        if add_review(current_user.id, book.id, int(form.rating.data), form.comment.data):
            flash('Відгук додано!', 'success')
            return redirect(url_for('books.book_detail', book_id=book.id))
        else:
            flash('Помилка.', 'error')

    return render_template('books/detail.html', 
                           book=book, 
                           current_status=current_status, 
                           is_purchased=is_purchased,
                           reviews=reviews,
                           form=form)

@bp.route('/buy/<int:book_id>')
@login_required
def buy_book_route(book_id):
    book = get_book_by_id(book_id)
    if not book: abort(404)
    success, message = purchase_book(current_user.id, book.id, book.price_coins)
    if success:
        flash(f'Придбано: "{book.title}"!', 'success')
        return redirect(url_for('books.book_detail', book_id=book.id))
    else:
        flash(message, 'error')
        if "Недостатньо" in message:
             return redirect(url_for('user.topup', next=url_for('books.book_detail', book_id=book.id)))
        return redirect(url_for('books.book_detail', book_id=book.id))

@bp.route('/gift/<int:book_id>', methods=['POST'])
@login_required
def gift_book_route(book_id):
    book = get_book_by_id(book_id)
    if not book: abort(404)
    recipient = request.form.get('recipient_username')
    friend = get_user_by_username(recipient)
    
    if not friend or friend.id == current_user.id:
        flash('Користувача не знайдено або це ви.', 'error')
        return redirect(url_for('books.book_detail', book_id=book.id))

    success, message = purchase_book(current_user.id, book.id, book.price_coins, receiver_id=friend.id)
    if success:
        flash(f'Подарунок надіслано @{friend.username}!', 'success')
    else:
        flash(message, 'error')
        if "Недостатньо" in message:
             return redirect(url_for('user.topup', next=url_for('books.book_detail', book_id=book.id)))

    return redirect(url_for('books.book_detail', book_id=book.id))

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    books = search_books(query) if query else []
    return render_template('index.html', books=books, search_query=query)

@bp.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if len(query) < 2: return jsonify([])
    books = search_books(query)
    results = [{'id': b.id, 'title': b.title, 'author': b.author, 'cover': url_for('static', filename='uploads/covers/' + b.cover_image), 'url': url_for('books.book_detail', book_id=b.id)} for b in books]
    return jsonify(results)