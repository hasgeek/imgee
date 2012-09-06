# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from imgee import app

db = SQLAlchemy(app)

from imgee.models.user import *
from imgee.models.stored_file import *
from imgee.models.thumbnail import *
from imgee.models.profile import *
