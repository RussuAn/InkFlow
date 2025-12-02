from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class ContactForm(FlaskForm):
    subject = StringField('Тема', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Повідомлення', validators=[
        DataRequired(),
        Length(min=10, message="Повідомлення занадто коротке")
    ])
    submit = SubmitField('Надіслати')