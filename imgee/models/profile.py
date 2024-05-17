from __future__ import annotations

from coaster.sqlalchemy import BaseNameMixin
from flask_lastuser.sqlalchemy import ProfileMixin

from . import DynamicMapped, Mapped, Model, backref, relationship, sa, sa_orm


class Profile(ProfileMixin, BaseNameMixin, Model):
    __tablename__ = 'profile'

    userid: Mapped[str] = sa_orm.mapped_column(
        sa.Unicode(22), nullable=False, unique=True
    )
    stored_files: DynamicMapped[StoredFile] = relationship(
        backref=backref('profile'),
        lazy='dynamic',
        cascade='all, delete-orphan',
    )

    def permissions(self, user, inherited=None):
        perms = super().permissions(user, inherited)
        if user is not None and self.userid in user.user_organizations_adminof_ids():
            perms.add('view')
            perms.add('edit')
            perms.add('delete')
            perms.add('new-file')
            perms.add('new-label')
        return perms


from .stored_file import StoredFile
