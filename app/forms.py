# -*- coding: utf-8 -*-

import re
from flask_wtf import Form, FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, ValidationError, InputRequired
from models import User
from flask_ckeditor import CKEditorField

class RegisterFrom(Form):
    usr_name = StringField('nickname', validators=[DataRequired()])
    usr_email = EmailField('email', validators=[DataRequired()])
    usr_password = PasswordField('password', validators=[DataRequired()])
    conform = PasswordField('conform', validators=[DataRequired()])
    usr_birthday = StringField('birthday')
    usr_gender = StringField('gender')

    def validate_nickname(self, field):
        nickname = field.data.strip()
        if len(nickname) < 3 or len(nickname) > 20:
            raise ValidationError('nickname must be 3 letter at least')
        if not re.search('^\w+$', nickname):
            raise ValidationError('User names can contain only alphanumeric characters and underscores.')
        else: # 验证是否已经注册
            u = User.query.filter_by(usr_name=nickname).first()
            if u:
                raise ValidationError('The nickname already exists')

    def validate_email(self, field):
        email = field.data.strip()
        email = User.query.filter_by(usr_email=email).first()
        if email:
            raise ValidationError('The email already exists')

    def validate_password(self, field):
        password = field.data.strip()
        if len(password) < 6:
            raise ValidationError('password must be 3 letter at least')

    def validate_conform(self, field):
        conform = field.data.strip()
        if self.data['usr_password'] != conform:
            raise ValidationError('the password and conform are different')

class LoginForm(Form):
    usr_name = StringField('nickname', validators=[DataRequired()])
    usr_password = PasswordField('password', validators=[DataRequired()])
    #remember_me = BooleanField('remember_me', default=False)

    def validate_nickname(self, field):
        nickname = field.data.strip()
        if len(nickname) < 3 or len(nickname) > 20:
            raise ValidationError('nickname must be 3 letter at least')
        elif not re.search(r'^\w+$', nickname):
            raise ValidationError('User names can contain only alphanumeric characters and underscores.')
        else:
            return nickname

class PostForm(FlaskForm):
    p_title = StringField('p_title')
    p_content = CKEditorField('p_content', validators=[DataRequired()])
    submit = SubmitField('Submit')
    p_board = StringField('p_board')

class ReplyForm(FlaskForm):
    r_title = StringField('r_title')
    r_content = CKEditorField('r_content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CompeteForm(Form):
    board1 = StringField('board1')
    board2 = StringField('board2')

class SearchForm(Form):
    usrname = StringField('usrname')

class ChangeForm(Form):
    b_name = StringField('b_name')