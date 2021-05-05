#!/usr/bin/env python
import os

from coaster.manage import init_manager, manager
from imgee import app
from imgee.models import db


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
