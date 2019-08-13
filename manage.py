#!/usr/bin/env python
import os

from coaster.manage import manager, init_manager

from imgee.models import db
from imgee import app


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


@manager.command
def init():
    mkdir_p(app.upload_folder)


if __name__ == "__main__":
    db.init_app(app)
    init_manager(app, db)

    manager.run()
