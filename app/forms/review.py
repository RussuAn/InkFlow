from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ReviewForm(FlaskForm):
    rating = SelectField('Оцінка', choices=[
        ('5', '⭐⭐⭐⭐⭐ - Відмінно'),
        ('4', '⭐⭐⭐⭐ - Добре'),
        ('3', '⭐⭐⭐ - Нормально'),
        ('2', '⭐⭐ - Погано'),
        ('1', '⭐ - Жахливо')
    ], validators=[DataRequired()])
    
    comment = TextAreaField('Ваш відгук', validators=[
        DataRequired(message="Напишіть хоч пару слів!"),
        Length(max=1000)
    ])
    
    submit = SubmitField('Опублікувати')