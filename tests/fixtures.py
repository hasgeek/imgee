import unittest
import random
import string

from imgee import app, storage
from imgee.models import db, User, Profile, StoredFile


class ImgeeTestCase(unittest.TestCase):
    def get_test_user(self, name='testuser', id=1):
        u = User.query.filter_by(username=unicode(name)).first()
        if not u:
            userid = ''.join(random.sample(string.letters, 22))
            u = User(
                username=unicode(name),
                userid=unicode(userid),
                lastuser_token_scope=u'id email organizations',
                lastuser_token_type=u'bearer',
                lastuser_token=u'last-user-token',
                fullname=unicode(name.capitalize()),
                id=id,
            )
            db.session.add(u)
            db.session.commit()
        return u

    def get_test_profile(self):
        return self.get_test_user().profile

    def setUp(self):
        app.config['TESTING'] = True
        app.testing = True

        db.create_all()
        self.test_user_name = u'testuser'
        test_user = self.get_test_user(name=self.test_user_name)
        self.client = app.test_client()
        with self.client.session_transaction() as session:
            session['lastuser_userid'] = test_user.userid
            Profile.update_from_user(test_user, db.session)
            db.session.commit()

    def tearDown(self):
        for s in StoredFile.query.all():
            storage.delete(s)
        db.drop_all()
