#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from config import config
from app.utils import filters, loggings, tests
from flask_debugtoolbar import DebugToolbarExtension
from app.extensions import (db, login_manager, cache, bootstrap, md, mail)
import flask_whooshalchemyplus


def create_app(config_name):
    app = Flask(__name__)

    # 获取配置信息
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 配置蓝图
    configure_blueprint(app)

    # 配置常用扩展组件
    configure_extensions(app)

    # 配置各种过滤器
    configure_template_filters(app)

    # 配置各种测试器
    configure_template_tests(app)

    # 配置各种日志文件
    loggings.create_logging(app)

    return app


def configure_blueprint(app):
    # 前台
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 用户相关
    from .auth import auth as auth_blueprint
    app.register_blueprint(
        auth_blueprint,
        url_prefix=app.config['AUTH_URL_PREFIX']
    )

    # 后台
    from .admin import admin as admin_blueprint
    app.register_blueprint(
        admin_blueprint,
        url_prefix=app.config['ADMIN_URL_PREFIX']
    )


def configure_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    flask_whooshalchemyplus.init_app(app)
    DebugToolbarExtension(app)
    cache.init_app(app)
    bootstrap.init_app(app)
    md.init_app(app)
    mail.init_app(app)


def configure_template_filters(app):
    app.jinja_env.filters['datetimeformat'] = filters.datetimeformat


def configure_template_tests(app):
    app.jinja_env.tests['is_select_menu'] = tests.is_select_menu
