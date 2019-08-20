# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import os.path

from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager

from baseframe import Version, assets, baseframe
import coaster.app

from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

assets['imgee.css'][version] = 'css/app.css'

from . import models, views  # NOQA # isort:skip
from .models import db  # NOQA # isort:skip
from .tasks import TaskRegistry  # NOQA # isort:skip

registry = TaskRegistry()

# Configure the application
coaster.app.init_app(app)
migrate = Migrate(app, db)
baseframe.init_app(app, requires=['baseframe', 'picturefill', 'imgee'])
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
registry.init_app(app)


@app.errorhandler(403)
def error403(error):
    return redirect(url_for('login'))


if app.config.get('MEDIA_DOMAIN', '').lower().startswith(('http://', 'https://')):
    app.config['MEDIA_DOMAIN'] = app.config['MEDIA_DOMAIN'].split(':', 1)[1]

app.upload_folder = os.path.join(
    app.static_folder, secure_filename(app.config.get('UPLOADED_FILES_DIR'))
)
