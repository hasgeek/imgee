# -*- coding: utf-8 -*-

from flask import url_for
from flask.ext.lastuser.sqlalchemy import UserBase
from werkzeug.utils import cached_property
from imgee.models import db
from imgee.models.profile import Profile


class User(UserBase, db.Model):
    __tablename__ = 'user'

    @cached_property
    def profile(self):
        return Profile.query.filter_by(userid=self.userid).first()

    @cached_property
    def profiles(self):
        return [self.profile] + Profile.query.filter(
            Profile.userid.in_(self.organizations_owned_ids())).order_by('title').all()

    @property
    def profile_url(self):
        return url_for('show_profile', profile_name=self.username or self.userid)
