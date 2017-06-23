# -*- coding: utf-8 -*-

from coaster.sqlalchemy import BaseNameMixin, BaseScopedNameMixin
from imgee import app, url_for
from imgee.models import db
from imgee.utils import newid, guess_extension


image_labels = db.Table('image_labels',
    db.Column('label_id', db.Integer, db.ForeignKey('label.id'), nullable=False),
    db.Column('stored_file_id', db.Integer, db.ForeignKey('stored_file.id'), nullable=False),
)


class Label(BaseScopedNameMixin, db.Model):
    """
    Labels are used to categorize images for easy discovery.
    An image may have zero or more labels.
    """
    __tablename__ = 'label'
    profile_id = db.Column(None, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship('Profile', backref=db.backref('labels', cascade='all, delete-orphan'))
    parent = db.synonym('profile')

    def __repr__(self):
        return "<%s> of <%s>" % (self.name, self.profile.name)


class StoredFile(BaseNameMixin, db.Model):
    """
    Stored files are the original files uploaded by the user.
    Permanent copies are stored on Amazon S3 and a temporary cached
    copy is stored locally for thumbnail generation. Files are always
    served from S3.
    """
    __tablename__ = 'stored_file'
    profile_id = db.Column(None, db.ForeignKey('profile.id'), nullable=False)
    size = db.Column(db.BigInteger, default=0)  # in bytes
    width = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)
    mimetype = db.Column(db.Unicode(32), nullable=False)
    orig_extn = db.Column(db.Unicode(15), nullable=True)
    no_previews = db.Column(db.Boolean, default=False, nullable=False)
    thumbnails = db.relationship('Thumbnail', backref='stored_file',
                                 cascade='all, delete-orphan')
    labels = db.relationship('Label', secondary='image_labels',
                backref=db.backref('stored_files', lazy='dynamic'))

    def __init__(self, **kwargs):
        super(StoredFile, self).__init__(**kwargs)
        if not self.name:
            self.name = newid()

    def __repr__(self):
        return "StoredFile <%s>" % (self.title)

    @property
    def extn(self):
        return guess_extension(self.mimetype, self.orig_extn) or ''

    @property
    def filename(self):
        return self.name + self.extn

    def dict_data(self):
        return dict(
            title=self.title,
            uploaded=self.created_at.isoformat() + 'Z',
            filesize=app.jinja_env.filters['filesizeformat'](self.size),
            imgsize=u'%s×%s px' % (self.width, self.height),
            url=url_for('view_image', profile=self.profile.name, image=self.name),
            thumb_url=url_for('get_image', image=self.name, size=app.config.get('THUMBNAIL_SIZE'))
        )

    def add_labels(self, labels):
        new_labels = set(labels)
        old_labels = set(self.labels)
        if new_labels != old_labels:
            self.labels = labels

        if new_labels == old_labels:
            status, diff = '0', []
        elif new_labels > old_labels:
            status, diff = '+', (new_labels - old_labels)
        elif (old_labels > new_labels):
            status, diff = '-', (old_labels - new_labels)
        else:
            status, diff = '', new_labels

        return status, list(diff)
