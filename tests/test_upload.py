import unittest
import requests

from imgee import app
from imgee.storage import save_file, delete
from imgee.utils import get_image_url
from fixtures import ImgeeTestCase
from werkzeug.datastructures import FileStorage


class UploadTestCase(ImgeeTestCase):
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.img_id = None
        self.test_files = ['../imgee/static/img/imgee.png', ]
        self.test_labels = ['logos', 'banners', 'profile-photos']
        self.sf = self.upload()

    def tearDown(self):
        super(UploadTestCase, self).tearDown()

    def upload(self, path=None):
        profile = self.get_test_profile()
        sf = None
        with open(path or self.test_files[0]) as fp:
            fs = FileStorage(fp)
            title, sf = save_file(fs, profile)
        return sf

    def test_save_file(self):
        with app.test_request_context('/'):
            resp = requests.get(get_image_url(self.sf))
            self.assertEquals(resp.status_code, 200)
            self.assertEquals(resp.headers.get('Content-Type', ''), self.sf.mimetype)

    def test_delete_file(self):
        delete(self.sf)
        with app.test_request_context('/'):
            resp = requests.get(get_image_url(self.sf))
            self.assertEquals(resp.status_code, 403)  # S3 throws 403 for non existing files


if __name__ == '__main__':
    unittest.main()
