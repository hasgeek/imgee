# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db


class FileStorage(BaseNameMixin, db.Model):
    __tablename__ = 'file_storage'

    thumbnails = db.relationship('Thumbnail', backref='file_storage')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
