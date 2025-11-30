import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app.forms.book import AddBookForm
from app.models.book import create_book, get_book_by_id
from app.models.library import get_user_book_status
from app.forms.review import ReviewForm
from app.models.review import add_review, get_book_reviews

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
        flash('У вас немає прав для перегляду цієї сторінки.', 'error')
        return redirect(url_for('index'))
    
    form = AddBookForm()
    
    if form.validate_on_submit():
        cover_filename = save_file(form.cover.data, 'covers')
        book_filename = save_file(form.book_file.data, 'books')
        
        if create_book(
            title=form.title.data,
            author=form.author.data,
            description=form.description.data,
            cover_image=cover_filename,
            file_path=book_filename,
            price_coins=form.price_coins.data
        ):
            flash(f'Книгу "{form.title.data}" успішно додано!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Помилка при збереженні в базу даних.', 'error')
            
    return render_template('books/add_book.html', form=form)

@bp.route('/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404)

    current_status = None
    if current_user.is_authenticated:
        current_status = get_user_book_status(current_user.id, book.id)

    reviews = get_book_reviews(book.id)
    form = ReviewForm()
    
    if form.validate_on_submit() and current_user.is_authenticated:
        if add_review(current_user.id, book.id, int(form.rating.data), form.comment.data):
            flash('Дякуємо за ваш відгук!', 'success')
            return redirect(url_for('books.book_detail', book_id=book.id))
        else:
            flash('Помилка при додаванні відгуку.', 'error')
        
    return render_template('books/detail.html', book=book, current_status=current_status, reviews=reviews, form=form)
    
