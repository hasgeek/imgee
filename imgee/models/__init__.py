# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from imgee import app
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from imgee.models.user import *
