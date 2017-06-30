# -*- coding: utf-8 -*-

from flask import url_for
from flask_lastuser.sqlalchemy import UserBase
from werkzeug.utils import cached_property
from . import db
from .profile import Profile


class User(UserBase, db.Model):
    __tablename__ = 'user'

    @cached_property
    def profile(self):
        return Profile.query.filter_by(userid=self.userid).first()

    @cached_property
    def profiles(self):
        return [self.profile] + Profile.query.filter(
            Profile.userid.in_(self.organizations_owned_ids())).order_by('title').all()

    @cached_property
    def profile_url(self):
        return url_for('profile_view', profile=self.profile_name)
