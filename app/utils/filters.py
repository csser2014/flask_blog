#!/usr/bin/env python
# -*- coding: utf-8 -*-


# 时间和日期过滤器
def datetimeformat(value, format="%Y-%m-%d"):
    return value.strftime(format)
