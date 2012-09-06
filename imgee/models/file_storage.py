# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db, Profile


class FileStorage(BaseNameMixin, db.Model):
    __tablename__ = 'file_storage'

    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship('Profile', backref='file_storage')
    thumbnails = db.relationship('Thumbnail', backref='file_storage')
