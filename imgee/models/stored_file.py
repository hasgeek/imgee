from __future__ import annotations

from flask import url_for

from coaster.sqlalchemy import BaseNameMixin, BaseScopedNameMixin

from .. import app
from ..utils import guess_extension, newid
from . import Mapped, Model, backref, relationship, sa, sa_orm
from .profile import Profile
from .thumbnail import Thumbnail

image_labels = sa.Table(
    'image_labels',
    Model.metadata,
    sa.Column('label_id', sa.Integer, sa.ForeignKey('label.id'), nullable=False),
    sa.Column(
        'stored_file_id', sa.Integer, sa.ForeignKey('stored_file.id'), nullable=False
    ),
)


class Label(BaseScopedNameMixin, Model):
    """
    Labels are used to categorize images for easy discovery.
    An image may have zero or more labels.
    """

    __tablename__ = 'label'
    profile_id: Mapped[int] = sa_orm.mapped_column(
        sa.ForeignKey('profile.id'), nullable=False
    )
    profile: Mapped[Profile] = relationship(
        'Profile', backref=backref('labels', cascade='all, delete-orphan')
    )
    parent: Mapped[Profile] = sa_orm.synonym('profile')

    def __repr__(self):
        return f"<{self.name}> of <{self.profile.name}>"


class StoredFile(BaseNameMixin, Model):
    """
    Stored files are the original files uploaded by the user.
    Permanent copies are stored on Amazon S3 and a temporary cached
    copy is stored locally for thumbnail generation. Files are always
    served from S3.
    """

    __tablename__ = 'stored_file'
    profile_id: Mapped[int] = sa_orm.mapped_column(
        sa.ForeignKey('profile.id'), nullable=False
    )
    size: Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, default=0
    )  # in bytes
    width: Mapped[int | None] = sa_orm.mapped_column(sa.Integer, default=0)
    height: Mapped[int | None] = sa_orm.mapped_column(sa.Integer, default=0)
    mimetype: Mapped[str] = sa_orm.mapped_column(sa.Unicode(32), nullable=False)
    orig_extn: Mapped[str | None] = sa_orm.mapped_column(sa.Unicode(15), nullable=True)
    no_previews: Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, default=False, nullable=False
    )
    thumbnails: Mapped[list[Thumbnail]] = relationship(
        backref='stored_file', cascade='all, delete-orphan'
    )
    labels: Mapped[list[Label]] = relationship(
        secondary='image_labels', backref=backref('stored_files', lazy='dynamic')
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.name:
            self.name = newid()

    def __repr__(self):
        return "StoredFile <%s>" % (self.name)

    @property
    def extn(self):
        return guess_extension(self.mimetype, self.orig_extn) or ''

    @property
    def filename(self):
        return self.name + self.extn

    def dict_data(self):
        return {
            'title': self.title,
            'uploaded': self.created_at.isoformat() + 'Z',
            'filesize': app.jinja_env.filters['filesizeformat'](self.size),
            'imgsize': f'{self.width}×{self.height} px',
            'url': url_for(
                'view_image', profile=self.profile.name, image=self.name, _external=True
            ),
            'embed_url': url_for('get_image', image=self.name, _external=True),
            'thumb_url': url_for(
                'get_image', image=self.name, size=app.config.get('THUMBNAIL_SIZE')
            ),
        }

    def add_labels(self, labels):
        status = {'+': [], '-': [], '': []}

        new_labels = set(labels)
        old_labels = set(self.labels)
        if new_labels != old_labels:
            self.labels = labels

        status['+'] = new_labels - old_labels  # added labels
        status['-'] = old_labels - new_labels  # removed labels
        status[''] = old_labels.intersection(new_labels)  # unchanged labels

        return status
