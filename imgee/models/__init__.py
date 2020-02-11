# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

from imgee import app

db = SQLAlchemy(app)

from .user import *  # NOQA  # isort:skip
from .stored_file import *  # NOQA  # isort:skip
from .thumbnail import *  # NOQA  # isort:skip
from .profile import *  # NOQA  # isort:skip
