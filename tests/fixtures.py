import unittest
import random
import string

from flask import g
from imgee import init_for, app
from imgee.models import db, User
from imgee.views.login import make_profiles

def get_test_user(name, id=1):
    if not name:
        name = 'testuser_%d' % id
    userid = ''.join(random.sample(string.letters, 22))
    u = User(username=unicode(name), userid=unicode(userid),
            lastuser_token_scope=u'id email organizations', lastuser_token_type=u'bearer',
            lastuser_token=u'last-user-token',
            fullname=name.capitalize(), id=id)
    db.session.add(u)
    db.session.commit()
    return u


class ImgeeTestCase(unittest.TestCase):
    def setUp(self):
        init_for('testing')
        app.config['TESTING'] = True
        app.testing = True
        db.create_all()
        self.test_user_name = 'testuser'
        test_user = get_test_user(name=self.test_user_name)
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['lastuser_userid'] = test_user.userid
            make_profiles(test_user)

    def tearDown(self):
        db.drop_all()


class DummyUser(object):
    def __init__(self, username):
        self.username = username

    def __enter__(self):
        g.user = get_test_user(name=self.username)
