# -*- coding: utf-8 -*-

from app import db
from datetime import datetime
from flask_login import UserMixin

ROLE_USER = 0
ROLE_BOARDER = 1
ROLE_ADMIN = 2


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    usr_password = db.Column(db.String(255), index=True)
    usr_name = db.Column(db.String(255), primary_key=True, index=True)
    usr_birthday = db.Column(db.String(255))
    usr_gender = db.Column(db.String(255))
    #usr_age = db.Column(db.SmallInteger)
    usr_email = db.Column(db.String(255), index=True, unique=True)
    usr_level = db.Column(db.Integer, default=0)
    usr_regdate = db.Column(db.DateTime, default=datetime.now)
    usr_role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def get_id(self):
        return unicode(self.usr_name)


class Board(db.Model):
    __tablename__ = 'board'
    b_id = db.Column(db.Integer, autoincrement=True)
    b_name = db.Column(db.String(255), primary_key=True, index=True)
    b_master = db.Column(db.String(255), db.ForeignKey('user.usr_name'))
    b_postcnt = db.Column(db.Integer, autoincrement=True)


class Post(db.Model):
    __tablename__ = 'post'
    p_id = db.Column(db.Integer, primary_key=True, default=1)
    p_board = db.Column(db.String(255), db.ForeignKey('board.b_name'))
    p_usrid = db.Column(db.String(255), db.ForeignKey('user.usr_name'))
    p_title = db.Column(db.String(255))
    p_time = db.Column(db.DateTime, default=datetime.now)
    p_clickcnt = db.Column(db.Integer, default=0)
    p_replycnt = db.Column(db.Integer, default=0)
    p_content = db.Column(db.Text)


class Reply(db.Model):
    __tablename__ = 'reply'
    r_id = db.Column(db.Integer, primary_key=True, default=1)
    r_layer = db.Column(db.Integer, default=1)
    r_name = db.Column(db.Integer, db.ForeignKey('user.usr_name'))
    r_title = db.Column(db.Integer, db.ForeignKey('post.p_id'))  # 哪个帖下面的回复
    r_time = db.Column(db.DateTime, default=datetime.now)
    r_agreecnt = db.Column(db.Integer, default=0)
    r_content = db.Column(db.Text, nullable=False)
