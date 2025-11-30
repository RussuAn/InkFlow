from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старий пароль', validators=[DataRequired()])
    
    new_password = PasswordField('Новий пароль', validators=[
        DataRequired(), 
        Length(min=6, message="Мінімум 6 символів")
    ])
    
    confirm_password = PasswordField('Підтвердіть новий пароль', validators=[
        DataRequired(),
        EqualTo('new_password', message='Паролі повинні співпадати')
    ])
    
    submit = SubmitField('Змінити пароль')

class DeleteAccountForm(FlaskForm):
    submit = SubmitField('Видалити акаунт назавжди')