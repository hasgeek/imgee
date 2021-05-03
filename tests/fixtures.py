import random
import string
import unittest

from imgee import app, storage
from imgee.models import Profile, StoredFile, User, db


class ImgeeTestCase(unittest.TestCase):
    def get_test_user(self, name='testuser', uid=1):
        u = User.query.filter_by(username=name).first()
        if not u:
            userid = ''.join(random.sample(string.ascii_letters, 22))
            u = User(
                username=name,
                userid=userid,
                lastuser_token_scope='id email organizations',
                lastuser_token_type='bearer',
                lastuser_token='last-user-token',
                fullname=name.capitalize(),
                id=uid,
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
        self.test_user_name = 'testuser'
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
