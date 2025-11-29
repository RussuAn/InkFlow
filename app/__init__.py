from flask import Flask, render_template
from .core.config import Config
from .core import db, logger

from app.routes import auth

def create_app():
    app = Flask(__name__, 
                template_folder='frontend/templates',
                static_folder='frontend/static')
    
    app.config.from_object(Config)

    logger.setup_logger(app)
    db.init_app(app)
    
    app.register_blueprint(auth.bp)

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