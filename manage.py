#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask_script import Manager
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ.get('CONFIG', 'default'))

manager = Manager(app)

# 数据库迁移
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
