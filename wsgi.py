#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app import create_app

app = create_app(os.environ.get('CONFIG', 'production'))

if __name__ == '__main__':
    app.run()
