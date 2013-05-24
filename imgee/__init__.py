# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

import os

from flask import Flask
from flask.ext.lastuser import LastUser
from baseframe import baseframe, assets, Version
import coaster.app
from ._version import __version__

version = Version(__version__)
app = Flask(__name__, instance_relative_config=True)
lastuser = LastUser()

assets['imgee.css'][version] = 'css/app.css'

import imgee.models
import imgee.views
from imgee.models import db


def mkdir_p(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    baseframe.init_app(app, requires=['baseframe', 'imgee'])
    lastuser.init_app(app)
    if app.config.get('MEDIA_DOMAIN') and (
            app.config['MEDIA_DOMAIN'].startswith('http:') or
            app.config['MEDIA_DOMAIN'].startswith('https:')):
        app.config['MEDIA_DOMAIN'] = app.config['MEDIA_DOMAIN'].split(':', 1)[1]
    mkdir_p(app.config['UPLOADED_FILES_DEST'])
