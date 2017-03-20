import unittest
import random
import string

from flask import g
from imgee import init_for, app, storage, lastuser
from imgee.models import db, User, Profile, StoredFile


def get_test_user(name=u'testuser'):
    u = db.session.query(User).first()
    if not u:
        userid = ''.join(random.sample(string.letters, 22))
        if not name:
            name = 'testuser_%d' % userid
        u = User(
            username=unicode(name), userid=unicode(userid),
            email=u"{}@hasgeek.com".format(userid))
        db.session.add(u)
        db.session.commit()
    return u


class ImgeeTestCase(unittest.TestCase):
    def setUp(self):
        init_for('testing')
        app.config['TESTING'] = True
        app.testing = True
        db.create_all()
        self.test_user_name = u'testuser'
        self.client = app.test_client()
        self.client.test_user = get_test_user(name=self.test_user_name)
        with self.client.session_transaction() as session:
            session['lastuser_userid'] = self.client.test_user.userid
            session['lastuser_sessionid'] = 'some-session-id'
            Profile.update_from_user(self.client.test_user, db.session)
            db.session.commit()

    def tearDown(self):
        for s in StoredFile.query.all():
            storage.delete(s)
        db.drop_all()


class DummyUser(object):
    def __init__(self, username):
        self.username = username

    def __enter__(self):
        g.user = get_test_user(name=self.username)
