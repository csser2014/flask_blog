#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from flask_bootstrap import Bootstrap
from flask_misaka import Misaka
from flask_mail import Mail


# 数据库实例
db = SQLAlchemy()

# redis 缓存
cache = Cache()

# bootstrap实例
bootstrap = Bootstrap()

# markdown
md = Misaka()

# 发送邮件
mail = Mail()

# 登录配置
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
