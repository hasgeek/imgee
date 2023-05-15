import unittest

from werkzeug.datastructures import FileStorage
import requests

from imgee import app, db, url_for
from imgee.storage import delete, save_file
from imgee.utils import get_image_url, get_thumbnail_url

from .fixtures import ImgeeTestCase


class UploadTestCase(ImgeeTestCase):
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.img_id = None
        self.test_files = [
            'imgee/static/img/imgee.png',
            'imgee/static/img/imgee.jpeg',
            'imgee/static/img/imgee.svg',
            'imgee/static/img/loading.gif',
        ]
        self.test_labels = ['logos', 'banners', 'profile-photos']
        self.files = self.upload_all()

    def tearDown(self):
        super(UploadTestCase, self).tearDown()

    def upload_all(self):
        files = []
        for test_file in self.test_files:
            files.append(self.upload(test_file))
        return files

    def upload(self, path=None):
        profile = self.get_test_profile()
        sf = None
        if path:
            with open(path, 'rb') as fp:
                fs = FileStorage(fp)
                title, sf = save_file(fs, profile)
            return sf

    def test_save_file(self):
        with app.test_request_context('/'):
            for test_file in self.files:
                resp = requests.get(get_image_url(test_file))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(
                    resp.headers.get('Content-Type', ''), test_file.mimetype
                )

    def test_resize(self):
        with app.test_request_context('/'):
            for test_file in self.files:
                resp = self.client.get(
                    url_for(
                        'get_image',
                        image=test_file.name,
                        size=app.config.get('THUMBNAIL_SIZE'),
                    )
                )
                self.assertEqual(resp.status_code, 301)
                self.assertEqual(
                    resp.headers.get('Location'), get_thumbnail_url(test_file)
                )

    def test_delete_file(self):
        for test_file in self.files:
            delete(test_file, commit=False)

        db.session.commit()

        for test_file in self.files:
            with app.test_request_context('/'):
                resp = requests.get(get_image_url(test_file))
                self.assertEqual(
                    resp.status_code, 403
                )  # S3 throws 403 for non existing files


if __name__ == '__main__':
    unittest.main()
