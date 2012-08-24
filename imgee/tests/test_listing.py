import os
from imgee import init_for, app
from imgee.models import db, User
import unittest
import tempfile

class UploadTestCase(unittest.TestCase):

    def setUp(self):
        init_for('testing')
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def create_user(self):
        user = User(username=u'nigelb', userid=u'WzTwFMKEQ5yozIkDj7feCw',
                    lastuser_token_scope=u'id', lastuser_token_type=u'bearer',
                    lastuser_token=u'-zhQm-NRSRaVfLQnebR3Mw',
                    fullname=u'Nigel Babu', id=1)
        db.session.add(user)
        db.session.commit()

    def test_listing_without_login(self):
        rv = self.app.get('/list')
        assert "You should be redirected automatically to target URL" in rv.data
