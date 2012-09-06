# -*- coding: utf-8 -*-

from flask.ext.lastuser.sqlalchemy import UserBase
from werkzeug.utils import cached_property
from imgee.models import db


class User(UserBase, db.Model):
    __tablename__ = 'user'

    @cached_property
    def profile(self):
        return Profile.query.filter_by(userid=self.userid).first()

    @cached_property
    def profiles(self):
        return [self.profile] + Profile.query.filter(
            Profile.userid.in_(self.organizations_owned_ids())).order_by('title').all()
