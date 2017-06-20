#!/usr/bin/env python
import os

from coaster.manage import init_manager

from imgee.models import db
from imgee import app


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

if __name__ == "__main__":
    db.init_app(app)
    manager = init_manager(app, db)

    @manager.command
    def init():
        print("$"*40)
        print(app.config['UPLOADED_FILES_DEST'])
        print(os.environ.get('FLASK_ENV'))
        mkdir_p(app.config['UPLOADED_FILES_DEST'])

    manager.run()
