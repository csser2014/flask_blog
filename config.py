#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))        # 根目录


class Config:
    from whoosh.analysis import StemmingAnalyzer
    # 私有密钥，用于加密
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        '[4\xfd[\xf7\x22\xcf\x13\adb\1BAC\xcf\x1a\x8att\10da\xc4\x87\xe05\xa1L'

    # 数据库配置
    SQLALCHEMY_COMMIT_ON_TEARDWN = True                     # 自动提交
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 邮箱服务器地址
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.163.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USE_TLS = True
    # 改为发邮箱地址
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'send@126.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'admin')
    # 改为收邮箱地址
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN', 'admin@163.com')

    # 蓝图的前缀
    AUTH_URL_PREFIX = '/auth'
    ADMIN_URL_PREFIX = '/admin'

    FLASK_ADMIN = 'admin@163.com'

    # 全文搜索
    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    WHOOSH_ANALYZER = StemmingAnalyzer()
    MAX_SEARCH_RESULTS = 200

    # redis
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = '6379'
    CACHE_REDIS_DB = '0'

    RECORD_LOGGING = True

    # 上传图片配置
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    UPLOAD_URL = 'uploads'

    # redis 前缀
    CACHE_KEY_PREFIX = 'redis_'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    # 是否中断debugtool工具的302跳转
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # sqlite 数据库, sqlite:///database.db
    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    '''

    # mysql 数据库, mysql://user:password@ip:port/db_name
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (
        os.environ.get('DATABASE_USERNAME', 'root'),
        os.environ.get('DATABASE_PASSWORD', 'root'),
        os.environ.get('DATABASE_HOST', 'localhost'),
        os.environ.get('DATABASE_DB', 'blog')
    )

    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    # sqlite 数据库, sqlite:///database.db
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    """

    # mysql 数据库, mysql://user:password@ip:port/db_name
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (
        os.environ.get('DATABASE_USERNAME', 'root'),
        os.environ.get('DATABASE_PASSWORD', 'root'),
        os.environ.get('DATABASE_HOST', 'localhost'),
        os.environ.get('DATABASE_DB', 'blog')
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
