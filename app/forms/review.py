from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class ReviewForm(FlaskForm):
    rating = SelectField('Оцінка', choices=[
        ('5', '5'),
        ('4', '4'),
        ('3', '3'),
        ('2', '2'),
        ('1', '1')
    ], validators=[DataRequired()])
    
    comment = TextAreaField('Ваш відгук', validators=[
        DataRequired(message="Напишіть хоч пару слів!"),
        Length(max=1000)
    ])
    
    submit = SubmitField('Опублікувати')