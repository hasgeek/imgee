# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin, BaseMixin
from imgee.models import db


image_labels = db.Table('image_labels',
    db.Column('label_id', db.Integer, db.ForeignKey('label.id')),
    db.Column('stored_file_id', db.Integer, db.ForeignKey('stored_file.id')),
)

class Label(BaseMixin, db.Model):
    __tablename__ = 'label'
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)

class StoredFile(BaseNameMixin, db.Model):
    __tablename__ = 'stored_file'

    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    thumbnails = db.relationship('Thumbnail', backref='stored_file',
                                 cascade='all, delete-orphan')
    labels = db.relationship('Label', secondary='image_labels',
                backref=db.backref('files', lazy='dynamic'), cascade='all')
