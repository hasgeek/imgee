import unittest
import os, requests
from StringIO import StringIO

from imgee import storage
from imgee.models import db, User, StoredFile
from fixtures import get_test_user, ImgeeTestCase

import test_utils

class UploadTestCase(ImgeeTestCase):
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.img_id = None

    def test_empty(self):
        r = self.client.get('/%s' % self.test_user_name)
        assert r.status_code == 200
        assert 'no images uploaded yet.' in r.data
        assert 'No Labels yet.' in r.data

    def exists_on_media_domain(self, img_id):
        r = self.client.get('/file/%s' % img_id)
        assert r.status_code == 301
        return requests.get(r.location).ok

    def thumbnais_exists_on_media_domain(self, img_id):
        r = self.client.get('/thumbnail/%s' % img_id)
        assert r.status_code == 301
        return requests.get(r.location).ok

    def test_upload(self):
        test_file = 'imgee/static/images/earth_moon_4test.gif'
        content = open(test_file).read()
        filename = os.path.basename(test_file)
        d = {'uploaded_file': (StringIO(content), filename)}
        r = self.client.post('/new', data=d, follow_redirects=True)
        assert r.status_code == 200
        assert filename in r.data
        assert "uploaded successfully." in r.data
        self.img_id = test_utils.get_img_id(r.data, filename)
        assert self.exists_on_media_domain(self.img_id) == True
        assert self.thumbnais_exists_on_media_domain(self.img_id) == True

    def tearDown(self):
        s = StoredFile.query.filter_by(name=self.img_id).first()
        if s: storage.delete_on_s3(s)
        super(UploadTestCase, self).tearDown()

if __name__ == '__main__':
    unittest.main()
