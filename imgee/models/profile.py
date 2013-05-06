from coaster.sqlalchemy import BaseNameMixin
from imgee.models import db


class PROFILE_TYPE:
    UNDEFINED = 0
    PERSON = 1
    ORGANIZATION = 2
    EVENTSERIES = 3


profile_types = {
    0: u"Undefined",
    1: u"Person",
    2: u"Organization",
    3: u"Event Series",
    }


class Profile(BaseNameMixin, db.Model):
    __tablename__ = 'profile'

    userid = db.Column(db.Unicode(22), nullable=False, unique=True)
    description = db.Column(db.UnicodeText, default=u'', nullable=False)
    type = db.Column(db.Integer, default=PROFILE_TYPE.UNDEFINED, nullable=False)
    stored_files = db.relationship('StoredFile', backref=db.backref('profile'), lazy='dynamic', cascade='all, delete-orphan')
    labels = db.relationship('Label', backref=db.backref('profile'), cascade='all, delete-orphan')

    def type_label(self):
        return profile_types.get(self.type, profile_types[0])

    def permissions(self, user, inherited=None):
        perms = super(Profile, self).permissions(user, inherited)
        if user is not None and self.userid in user.user_organizations_owned_ids():
            perms.add('view')
            perms.add('edit')
            perms.add('delete')
            perms.add('new-file')
            perms.add('new-label')
        return perms
