#!/usr/bin/env python

from coaster.manage import init_manager

from imgee.models import db
from imgee import app


if __name__ == "__main__":
    db.init_app(app)
    manager = init_manager(app, db)
    manager.run()
