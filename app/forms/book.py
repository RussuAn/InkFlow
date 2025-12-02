from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange


class AddBookForm(FlaskForm):
    title = StringField('Назва книги', validators=[
        DataRequired(), 
        Length(max=255)
    ])
    
    author = StringField('Автор', validators=[
        DataRequired(), 
        Length(max=100)
    ])

    publication_year = IntegerField('Рік видання', validators=[
        DataRequired(message="Введіть рік"),
        NumberRange(min=1000, max=2030, message="Введіть коректний рік")
    ], default=2024)

    genre = SelectField('Жанр', choices=[
        ('Художня література', 'Художня література'),
        ('Фантастика', 'Фантастика'),
        ('Фентезі', 'Фентезі'),
        ('Детектив', 'Детектив'),
        ('Наукова література', 'Наукова література'),
        ('Психологія', 'Психологія'),
        ('Бізнес', 'Бізнес'),
        ('Історія', 'Історія'),
        ('Інше', 'Інше')
    ], validators=[DataRequired()])
    
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