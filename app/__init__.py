from flask import Flask, render_template
from flask_login import LoginManager
from .core.config import Config
from .core import db, logger

from app.routes import auth
from app.routes import user
from app.models.user import get_user_by_id

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Будь ласка, увійдіть, щоб отримати доступ."
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__, 
                template_folder='frontend/templates',
                static_folder='frontend/static')
    
    app.config.from_object(Config)

    logger.setup_logger(app)
    db.init_app(app)

    login_manager.init_app(app)
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/test-db')
    def test_db():
        try:
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE()")
            data = cursor.fetchone()
            return f"Успішне підключення до бази: {data[0]}"
        except Exception as e:
            app.logger.error(f"Помилка БД: {e}")
            return f"Помилка: {e}"

    return app

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)