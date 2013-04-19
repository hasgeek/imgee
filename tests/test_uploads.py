import unittest
import os, requests
from StringIO import StringIO

from imgee import storage
from imgee.models import db, User, StoredFile, Profile
from fixtures import get_test_user, ImgeeTestCase

import test_utils

class UploadTestCase(ImgeeTestCase):
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.img_id = None
        self.test_file = 'imgee/static/images/earth_moon_4test.gif'

    def exists_on_media_domain(self, img_id):
        r = self.client.get('/file/%s' % img_id)
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok

    def thumbnails_exists_on_media_domain(self, img_id):
        r = self.client.get('/thumbnail/%s' % img_id)
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok

    def upload(self, path=None):
        path = path or self.test_file
        content = open(path).read()
        filename = os.path.basename(path)
        d = {'uploaded_file': (StringIO(content), filename)}
        response = self.client.post('/new', data=d, follow_redirects=True)
        return filename, response

    def test_empty(self):
        r = self.client.get('/%s' % self.test_user_name)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('no images uploaded yet.' in r.data)
        self.assertTrue('No Labels yet.' in r.data)

    def test_upload(self):
        filename, r = self.upload()
        self.assertEquals(r.status_code, 200)
        self.assertTrue(filename in r.data)
        self.assertTrue("uploaded successfully." in r.data)

    def test_view_image(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(r.data, filename)
        view_url = '/%s/view/%s' % (self.test_user_name, self.img_id)
        r = self.client.get(view_url)
        self.assertEquals(r.status_code, 200)

    def test_file(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(r.data, filename)
        self.assertTrue(self.exists_on_media_domain(self.img_id))

    def test_thumbnail(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(r.data, filename)
        self.assertTrue(self.thumbnails_exists_on_media_domain(self.img_id))

    def tearDown(self):
        s = StoredFile.query.filter_by(name=self.img_id).first()
        if s: storage.delete_on_s3(s)
        super(UploadTestCase, self).tearDown()

if __name__ == '__main__':
    unittest.main()
