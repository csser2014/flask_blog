#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import book


@book.route('/')
def index():
    return 'Book'
