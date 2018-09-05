#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


# 判断是否是选中菜单
def is_select_menu(cur_menu, path):
    return re.match(cur_menu, path)
