from coaster.sqlalchemy import BaseMixin
from imgee.models import db


class Thumbnail(BaseMixin, db.Model):
    __tablename__ = 'thumbnail'

    name = db.Column(db.Unicode(250), nullable=False, unique=True)
    uploaded_file_id = db.Column(db.Integer, db.ForeignKey('file.id'))
