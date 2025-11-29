import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app.forms.book import AddBookForm
from app.models.book import create_book, get_book_by_id

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

@bp.route('/<int:book_id>')
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if not book:
        abort(404) # Якщо книги немає - помилка 404
        
    return render_template('books/detail.html', book=book)