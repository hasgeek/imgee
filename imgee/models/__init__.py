# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

from imgee import app

db = SQLAlchemy(app)

from imgee.models.user import *  # NOQA  # isort:skip
from imgee.models.stored_file import *  # NOQA  # isort:skip
from imgee.models.thumbnail import *  # NOQA  # isort:skip
from imgee.models.profile import *  # NOQA  # isort:skip
