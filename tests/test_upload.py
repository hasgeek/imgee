import os
import unittest
import requests

from imgee import app
from imgee.storage import save_file, delete
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
        resp = requests.get("http:" + os.path.join(app.config.get('MEDIA_DOMAIN'), app.config.get('AWS_FOLDER'), "{}{}".format(self.sf.name, self.sf.extn)))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get('Content-Type', ''), self.sf.mimetype)

    def test_delete_file(self):
        delete(self.sf)
        resp = requests.get("http:" + os.path.join(app.config.get('MEDIA_DOMAIN'), app.config.get('AWS_FOLDER'), "{}{}".format(self.sf.name, self.sf.extn)))
        self.assertEquals(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
