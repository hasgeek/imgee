from werkzeug.utils import cached_property

from flask_lastuser.sqlalchemy import UserBase2

from . import db
from .profile import Profile


class User(UserBase2, db.Model):
    __tablename__ = 'user'

    @cached_property
    def profile(self):
        return Profile.query.filter_by(userid=self.userid).first()

    @cached_property
    def profiles(self):
        return [self.profile] + Profile.query.filter(
            Profile.userid.in_(self.organizations_adminof_ids())
        ).order_by(Profile.title).all()

    @cached_property
    def profile_url(self):
        return self.profile.url_for()
