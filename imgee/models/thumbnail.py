# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseMixin
from imgee.models import db
from imgee.utils import newid


class Thumbnail(BaseMixin, db.Model):
    """
    A thumbnail is a resized version of an image file. Imgee can
    generate thumbnails at user-specified sizes for recognized
    image types. Unrecognized types are always served as the original
    file.
    """
    __tablename__ = 'thumbnail'

    name = db.Column(db.Unicode(64), nullable=False, unique=True, index=True)
    size = db.Column(db.Unicode(100), nullable=False, index=True)
    stored_file_id = db.Column(None, db.ForeignKey('stored_file.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Thumbnail, self).__init__(**kwargs)
        if not self.name:
            self.name = newid()
