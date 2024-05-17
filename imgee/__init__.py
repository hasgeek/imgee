# The imports in this file are order-sensitive

import os.path

from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

import coaster.app
from baseframe import Bundle, Version, assets, baseframe
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager

from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

assets['imgee.css'][version] = 'css/app.css'

from . import cli, models, views  # NOQA # isort:skip
from .models import db  # isort:skip
from .tasks import TaskRegistry  # isort:skip

registry = TaskRegistry()

# Configure the application
coaster.app.init_app(app, ['py', 'env'], env_prefix=['FLASK', 'APP_IMGEE'])
db.init_app(app)
db.app = app  # type: ignore[attr-defined]
migrate = Migrate(app, db)
baseframe.init_app(
    app,
    requires=[
        'baseframe-mui',
        'picturefill',
        'imgee',
        'jquery_jeditable',
        'jquery.appear',
    ],
    theme='mui',
)
lastuser.init_app(app)
lastuser.init_usermanager(UserManager(db, models.User))
registry.init_app(app)

app.assets.register(
    'js_dropzone',
    Bundle(
        assets.require('!jquery.js', 'dropzone.js==5.5.0'),
        output='js/dropzone.packed.js',
        filters='rjsmin',
    ),
)
app.assets.register(
    'css_dropzone',
    Bundle(
        assets.require('dropzone.css==5.5.0'),
        output='css/dropzone.packed.css',
        filters='cssmin',
    ),
)


@app.errorhandler(403)
def error403(error):
    return redirect(url_for('login'))


if app.config.get('AWS_S3_DOMAIN', '').lower().startswith(('http://', 'https://')):
    app.config['AWS_S3_DOMAIN'] = app.config['AWS_S3_DOMAIN'].split(':', 1)[1][2:]

app.upload_folder = os.path.join(
    app.static_folder, secure_filename(app.config.get('UPLOADED_FILES_DIR', 'uploads'))
)
app.config.setdefault('THUMBNAIL_SIZE', '75x75')
