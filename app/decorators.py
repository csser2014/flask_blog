#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from functools import wraps
from flask_login import current_user
from .models import Permission
from . import cache


# 权限判断
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorator_function
    return decorator


# 是否是管理员
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)


# 清除所有缓存
def clear_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cache.clear()
        return f(*args, **kwargs)
    return decorated_function
