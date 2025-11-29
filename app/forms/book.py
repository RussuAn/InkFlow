from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class AddBookForm(FlaskForm):
    title = StringField('Назва книги', validators=[DataRequired(), Length(max=255)])
    
    author = StringField('Автор', validators=[DataRequired(), Length(max=100)])
    
    description = TextAreaField('Опис / Анотація', validators=[DataRequired()])
    
    price_coins = IntegerField('Ціна (монети)', validators=[
        NumberRange(min=0, message="Ціна не може бути від'ємною")
    ], default=0)
    
    cover = FileField('Обкладинка (JPG, PNG)', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Тільки зображення!')
    ])
    
    book_file = FileField('Файл книги (PDF, EPUB)', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'epub'], 'Тільки PDF або EPUB!')
    ])
    
    submit = SubmitField('Додати книгу')