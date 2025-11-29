from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_login import current_user
from app.models.user import get_user_by_username


class EditProfileForm(FlaskForm):
    display_name = StringField('Ваше ім\'я (відображається в профілі)', validators=[
        Length(max=100)
    ])

    username = StringField('Нікнейм (@username)', validators=[
        DataRequired(), 
        Length(min=2, max=50)
    ])
    
    avatar = FileField('Оновити фото профілю', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Тільки зображення!')
    ])
    
    bio = TextAreaField('Про себе', validators=[
        Length(max=500)
    ])
    
    submit = SubmitField('Зберегти зміни')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = get_user_by_username(username.data)
            if user:
                raise ValidationError('Цей нікнейм вже зайнятий.')