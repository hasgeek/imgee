# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db


class UploadedFile(BaseNameMixin, db.Model):
    __tablename__ = 'file'

    thumbnails = db.relationship('Thumbnail', backref='uploadedfile')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
