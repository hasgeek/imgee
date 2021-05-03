from coaster.sqlalchemy import BaseMixin

from ..utils import newid
from . import db


class Thumbnail(BaseMixin, db.Model):
    """
    A thumbnail is a resized version of an image file. Imgee can
    generate thumbnails at user-specified sizes for recognized
    image types. Unrecognized types are always served as the original
    file.
    """

    __tablename__ = 'thumbnail'

    name = db.Column(db.Unicode(64), nullable=False, unique=True, index=True)
    width = db.Column(db.Integer, default=0, index=True)
    height = db.Column(db.Integer, default=0, index=True)
    stored_file_id = db.Column(None, db.ForeignKey('stored_file.id'), nullable=False)

    def __init__(self, **kwargs):
        super(Thumbnail, self).__init__(**kwargs)
        if not self.name:
            self.name = newid()

    def __repr__(self):
        return "Thumbnail <%s>" % (self.name)
