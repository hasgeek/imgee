# -*- coding: utf-8 -*-

from flask.ext.lastuser.sqlalchemy import UserBase
from imgee.models import db


class User(UserBase, db.Model):
    __tablename__ = 'user'
