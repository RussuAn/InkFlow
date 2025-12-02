from flask import Flask, render_template, request
from flask_login import LoginManager

from .core.config import Config
from .core import db, logger

from app.routes import auth
from app.routes import user
from app.routes import books
from app.routes import library
from app.routes import reader

from app.models.user import get_user_by_id
from app.models.book import get_all_books


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Будь ласка, увійдіть, щоб отримати доступ."
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')

    app.config.from_object(Config)

    logger.setup_logger(app)
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(library.bp)
    app.register_blueprint(reader.bp)

    @app.route('/')
    def index():
        genre = request.args.get('genre')
        only_free = request.args.get('free') == '1'

        books = get_all_books(genre=genre, only_free=only_free)

        app.logger.info(f"Головна сторінка: перегляд {len(books)} книг. Фільтри: жанр={genre}, безкоштовні={only_free}")

        return render_template('index.html', books=books, current_genre=genre, current_free=only_free)
    
    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/faq')
    def faq():
        return render_template('faq.html')

    def handle_404(e):
        app.logger.warning(f"404 Error: {request.url}")
        return render_template('errors/404.html'), 404

    def handle_500(e):
        app.logger.error(f"500 Error: {e}")
        return render_template('errors/500.html'), 500

    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)

    return app


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)