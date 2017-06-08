# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import os

from flask import Flask, redirect, url_for
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from baseframe import baseframe, assets, Version
from flask_migrate import Migrate
import coaster.app
from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

assets['imgee.css'][version] = 'css/app.css'

from . import models, views
from .models import db
from .tasks import TaskRegistry


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

registry = TaskRegistry()

# Configure the app
coaster.app.init_app(app)
migrate = Migrate(app, db)
baseframe.init_app(app, requires=['baseframe', 'picturefill', 'imgee'])
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
registry.init_app()


@app.errorhandler(403)
def error403(error):
    return redirect(url_for('login'))

if app.config.get('MEDIA_DOMAIN') and (
        app.config['MEDIA_DOMAIN'].startswith('http:') or
        app.config['MEDIA_DOMAIN'].startswith('https:')):
    app.config['MEDIA_DOMAIN'] = app.config['MEDIA_DOMAIN'].split(':', 1)[1]
mkdir_p(app.config['UPLOADED_FILES_DEST'])
