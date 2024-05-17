from __future__ import annotations

from coaster.sqlalchemy import BaseMixin

from ..utils import newid
from . import Mapped, Model, sa, sa_orm


class Thumbnail(BaseMixin, Model):
    """
    A thumbnail is a resized version of an image file. Imgee can
    generate thumbnails at user-specified sizes for recognized
    image types. Unrecognized types are always served as the original
    file.
    """

    __tablename__ = 'thumbnail'

    name: Mapped[str] = sa_orm.mapped_column(
        sa.Unicode(64), nullable=False, unique=True, index=True
    )
    width: Mapped[int | None] = sa_orm.mapped_column(sa.Integer, default=0, index=True)
    height: Mapped[int | None] = sa_orm.mapped_column(sa.Integer, default=0, index=True)
    stored_file_id: Mapped[int] = sa_orm.mapped_column(
        sa.ForeignKey('stored_file.id'), nullable=False
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.name:
            self.name = newid()

    def __repr__(self):
        return "Thumbnail <%s>" % (self.name)
