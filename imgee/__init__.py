# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import os
from celery import Celery

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
celery = Celery()

assets['imgee.css'][version] = 'css/app.css'

from . import models, views
from .models import db
from .api import api
from .async import TaskRegistry

registry = TaskRegistry()

def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def error403(error):
    return redirect(url_for('login'))


# Configure the app

coaster.app.init_app(app)
migrate = Migrate(app, db)
baseframe.init_app(app, requires=['baseframe', 'picturefill', 'imgee'])
app.error_handlers[403] = error403
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))

if app.config.get('MEDIA_DOMAIN') and (
        app.config['MEDIA_DOMAIN'].startswith('http:') or
        app.config['MEDIA_DOMAIN'].startswith('https:')):
    app.config['MEDIA_DOMAIN'] = app.config['MEDIA_DOMAIN'].split(':', 1)[1]
mkdir_p(app.config['UPLOADED_FILES_DEST'])

celery.conf.add_defaults(app.config)
registry.set_connection()
app.register_blueprint(api, url_prefix='/api/1')
