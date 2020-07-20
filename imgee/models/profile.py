# -*- coding: utf-8 -*-
from flask_lastuser.sqlalchemy import ProfileMixin

from coaster.sqlalchemy import BaseNameMixin

from . import db


class Profile(ProfileMixin, BaseNameMixin, db.Model):
    __tablename__ = 'profile'

    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    stored_files = db.relationship(
        'StoredFile',
        backref=db.backref('profile'),
        lazy='dynamic',
        cascade='all, delete-orphan',
    )

    def permissions(self, user, inherited=None):
        perms = super(Profile, self).permissions(user, inherited)
        if user is not None and self.userid in user.user_organizations_adminof_ids():
            perms.add('view')
            perms.add('edit')
            perms.add('delete')
            perms.add('new-file')
            perms.add('new-label')
        return perms
