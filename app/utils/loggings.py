#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import event
from sqlalchemy.engine import Engine
import os
import time
import logging
import logging.handlers


# 根目录
rootdir = os.path.join(
    os.path.abspath(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(__file__)
            )
        )
    )
)


# log 日志
def create_logging(app):
    logs_dir = os.path.join(rootdir, 'logs')
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)

    # 日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    )

    # debug 日志
    debug_file = os.path.join(logs_dir, 'log.debug')
    log_debug_handler = logging.handlers.RotatingFileHandler(
        debug_file,
        maxBytes=10000000,   # 10M
        backupCount=5
    )

    log_debug_handler.setLevel(logging.DEBUG)
    log_debug_handler.setFormatter(formatter)
    app.logger.addHandler(log_debug_handler)

    # error 日志
    error_file = os.path.join(logs_dir, 'log.error')
    log_error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=10000000,   # 10M
        backupCount=5
    )

    log_error_handler.setLevel(logging.ERROR)
    log_error_handler.setFormatter(formatter)
    app.logger.addHandler(log_error_handler)

    if app.config['SQLALCHEMY_ECHO'] or app.config['RECORD_LOGGING']:
        @event.listens_for(Engine, 'before_cursor_execute')
        def before_cursor_execute(conn, cursor, statement,
                                  parameters, context, executemany):
            context.query_start_time = time.time()
            print "-----"
            print context.query_start_time
            print "-----"
            app.logger.debug(u'开始记录SQL:\n%s' % statement)
            app.logger.debug(u'SQL语句:\n%r' % (parameters,))

        @event.listens_for(Engine, 'after_cursor_execute')
        def after_cursor_execute(conn, cursor, statement,
                                 parameters, context, executemany):
            total = time.time() - context.query_start_time
            app.logger.debug(u'记录结束')
            app.logger.debug(u'总时间:%.2fms' % (total * 1000))
            app.logger.debug('-' * 50)
