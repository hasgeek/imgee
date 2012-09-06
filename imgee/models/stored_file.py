# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db


class StoredFile(BaseNameMixin, db.Model):
    __tablename__ = 'stored_file'

    profile_id = db.Column(None, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship('Profile', backref='stored_file')
    thumbnails = db.relationship('Thumbnail', backref='stored_file',
                                 cascade='all, delete-orphan')

