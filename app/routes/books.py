import os
import secrets
import PyPDF2
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort, request, jsonify
from flask_login import login_required, current_user

from app.forms.book import AddBookForm
from app.forms.review import ReviewForm

from app.models.book import create_book, get_book_by_id, search_books, delete_book
from app.models.library import get_user_book_status
from app.models.commerce import purchase_book, is_book_purchased
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
        current_app.logger.warning(f"Спроба несанкціонованого доступу до додавання книги: {current_user.username}")
        flash('У вас немає прав.', 'error')
        return redirect(url_for('index'))
    
    form = AddBookForm()
    if form.validate_on_submit():
        try:
            cover_filename = save_file(form.cover.data, 'covers')
            book_filename = save_file(form.book_file.data, 'books')

            page_count = 0
            try:
                book_path = os.path.join(current_app.root_path, 'frontend', 'static', 'uploads', 'books', book_filename)
                with open(book_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    page_count = len(pdf_reader.pages)
            except Exception as e:
                current_app.logger.error(f"Помилка при читанні PDF: {e}")

            if create_book(
                title=form.title.data, 
                author=form.author.data, 
                publication_year=form.publication_year.data,
                description=form.description.data, 
                cover_image=cover_filename, 
                file_path=book_filename, 
                price_coins=form.price_coins.data, 
                page_count=page_count, 
                genre=form.genre.data
            ):
                current_app.logger.info(f"Книгу додано: {form.title.data} (Адмін: {current_user.username})")
                flash(f'Книгу "{form.title.data}" додано! (Сторінок: {page_count})', 'success')
                return redirect(url_for('index'))
            else:
                flash('Помилка бази даних при збереженні книги.', 'error')
                
        except Exception as e:
            current_app.logger.error(f"Критична помилка при додаванні книги: {e}")
            flash('Сталася помилка при завантаженні файлів.', 'error')
            
    return render_template('books/add_book.html', form=form)


@bp.route('/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
    
    current_status = None
    is_owned = False
    is_reading = False
    
    if current_user.is_authenticated:
        current_status = get_user_book_status(current_user.id, book.id)
        is_reading = (current_status == 'reading')
        
        is_purchased_check = is_book_purchased(current_user.id, book.id)
        if book.price_coins == 0 or is_purchased_check:
             is_owned = True

    reviews = get_book_reviews(book.id)
    average_rating = 0
    if reviews:
        total_rating = sum(r['rating'] for r in reviews)
        average_rating = total_rating / len(reviews)

    review_form = ReviewForm()
    if review_form.validate_on_submit() and current_user.is_authenticated:
        if add_review(current_user.id, book.id, int(review_form.rating.data), review_form.comment.data):
            current_app.logger.info(f"Новий відгук від {current_user.username} на книгу ID {book.id}")
            flash('Відгук додано!', 'success')
            return redirect(url_for('books.book_detail', book_id=book.id))

    return render_template('books/detail.html', 
                           book=book, 
                           current_status=current_status, 
                           is_owned=is_owned,
                           is_reading=is_reading,
                           reviews=reviews,
                           average_rating=average_rating,
                           review_form=review_form)


@bp.route('/buy/<int:book_id>')
@login_required
def buy_book_route(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
        
    success, message = purchase_book(current_user.id, book.id, book.price_coins)
    
    if success:
        current_app.logger.info(f"Покупка книги: {current_user.username} купив '{book.title}' за {book.price_coins}")
        flash(f'Придбано: "{book.title}"!', 'success')
    else:
        flash(message, 'error')
        if "Недостатньо" in message:
             return redirect(url_for('user.topup', next=url_for('books.book_detail', book_id=book.id)))
             
    return redirect(url_for('books.book_detail', book_id=book.id))


@bp.route('/gift/<int:book_id>', methods=['POST'])
@login_required
def gift_book_route(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
        
    recipient_username = request.form.get('recipient_username')
    friend = get_user_by_username(recipient_username)
    
    if not friend or friend.id == current_user.id:
        flash('Користувача не знайдено або це ви.', 'error')
        return redirect(url_for('books.book_detail', book_id=book.id))

    success, message = purchase_book(current_user.id, book.id, book.price_coins, receiver_id=friend.id)
    
    if success:
        current_app.logger.info(f"Подарунок: {current_user.username} подарувал '{book.title}' користувачу {friend.username}")
        flash(f'Подарунок надіслано @{friend.username}!', 'success')
    else:
        flash(message, 'error')
        if "Недостатньо" in message:
             return redirect(url_for('user.topup', next=url_for('books.book_detail', book_id=book.id)))
             
    return redirect(url_for('books.book_detail', book_id=book.id))


@bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book_route(book_id):
    if current_user.role != 'admin':
        flash('У вас немає прав.', 'error')
        return redirect(url_for('books.book_detail', book_id=book.id))
    
    book = get_book_by_id(book_id)
    if not book:
        abort(404)
        
    if delete_book(book.id):
        try:
            upload_folder = os.path.join(current_app.root_path, 'frontend', 'static', 'uploads')
            
            cover_path = os.path.join(upload_folder, 'covers', book.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)
                
            book_path = os.path.join(upload_folder, 'books', book.file_path)
            if os.path.exists(book_path):
                os.remove(book_path)
                
            current_app.logger.info(f"Книгу видалено: {book.title} (Адмін: {current_user.username})")
            flash(f'Книгу "{book.title}" видалено!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            current_app.logger.error(f"Помилка при видаленні файлів книги: {e}")
            flash('Книгу видалено з БД, але файли могли залишитися.', 'warning')
            return redirect(url_for('index'))
    else:
        flash('Помилка бази даних при видаленні.', 'error')
        return redirect(url_for('books.book_detail', book_id=book.id))


@bp.route('/search')
def search():
    query = request.args.get('q', '')
    books = search_books(query) if query else []
    return render_template('index.html', books=books, search_query=query)


@bp.route('/api/search')
def search_api():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    books = search_books(query)
    results = [
        {
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'cover': url_for('static', filename='uploads/covers/' + b.cover_image),
            'url': url_for('books.book_detail', book_id=b.id)
        } 
        for b in books
    ]
    return jsonify(results)