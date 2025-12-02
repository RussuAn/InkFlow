from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import get_user_by_email, get_user_by_username


class RegistrationForm(FlaskForm):
    display_name = StringField('Ім\'я для відображення', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Length(min=2, max=100, message="Ім'я має бути від 2 до 100 символів")
    ])
    
    username = StringField('Нікнейм', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Length(min=2, max=50, message="Нікнейм має бути від 2 до 50 символів")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Email(message="Введіть коректну email адресу")
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Це поле обов'язкове"),
        Length(min=6, message="Пароль має бути не менше 6 символів")
    ])
    
    confirm_password = PasswordField('Підтвердіть пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Паролі повинні співпадати')
    ])
    
    submit = SubmitField('Зареєструватися')

    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user:
            raise ValidationError('Цей нікнейм вже зайнятий.')

    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if user:
            raise ValidationError('Цей email вже зареєстрований.')


class LoginForm(FlaskForm):
    email_or_username = StringField('Нікнейм або Email', validators=[
        DataRequired(message="Введіть нікнейм або email")
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Введіть пароль")
    ])
    
    remember = BooleanField('Запам\'ятати мене')
    
    submit = SubmitField('Увійти')