# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


from flask_ckeditor import CKEditor

app = Flask(__name__)
app.config.from_object('config') # 载入配置文件
app.config['CKEDITOR_SERVE_LOCAL'] = True
app.config['CKEDITOR_HEIGHT'] = 280
app.config['CKEDITOR_WIDTH'] = 700
app.config['CKEDITOR_LANGUAGE'] = 'zh'
ckeditor = CKEditor(app)
db = SQLAlchemy(app) # 初始化 db 对象
login_manager = LoginManager() # 初始化登录管理对象
login_manager.init_app(app)
login_manager.login_view = 'signin' # 登录跳转视图
login_manager.login_message = u'登录跳转' # 登录跳转视图前的输出消息
from app import views, models # 引用视图和模型