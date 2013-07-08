#import os
import unittest
import requests
from PIL import Image

from imgee import storage
from imgee.models import StoredFile
from fixtures import ImgeeTestCase, app
import test_utils


class UploadTestCase(ImgeeTestCase):
    def setUp(self):
        super(UploadTestCase, self).setUp()
        self.img_id = None
        self.test_file = '../imgee/static/img/imgee.jpeg'

    def upload(self, path=None):
        return test_utils.upload(self.client, path or self.test_file, '/%s/new' % self.test_user_name)

    def exists_on_media_domain(self, img_id):
        r = self.client.get('/%s/file/%s' % (self.test_user_name, img_id))
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok

    def thumbnails_exists_on_media_domain(self, img_id):
        r = self.client.get('/%s/thumbnail/%s' % (self.test_user_name, img_id))
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok

    def get_image_size(self, img_path=None):
        return test_utils.get_image_size(img_path or self.test_file)

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
        self.img_id = test_utils.get_img_id(filename)
        view_url = '/%s/view/%s' % (self.test_user_name, self.img_id)
        r = self.client.get(view_url)
        self.assertEquals(r.status_code, 200)

    def test_file(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(filename)
        self.assertTrue(self.exists_on_media_domain(self.img_id))

    def test_thumbnail(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(filename)
        self.assertTrue(self.thumbnails_exists_on_media_domain(self.img_id))

    def test_delete(self):
        filename, r = self.upload()
        self.img_id = test_utils.get_img_id(filename)

        # check if the file and thumbnail exists
        self.assertTrue(self.exists_on_media_domain(self.img_id))
        self.assertTrue(self.thumbnails_exists_on_media_domain(self.img_id))

        r = self.client.post('/%s/delete/%s' % (self.test_user_name, self.img_id))

        # check if the file exists now
        r = self.client.get('/%s/file/%s' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 404)

        # check if the thumbnail exists
        r = self.client.get('/%s/thumbnail/%s' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 404)

    def test_file_count(self):
        filename1, r1 = self.upload()

        # if the same file is uploaded twice, imgee should treat them as different
        filename2, r2 = self.upload()
        self.assertEquals(filename1, filename2)

        imgs = StoredFile.query.filter_by(title=filename1).all()
        self.assertEquals(len(imgs), 2)

    def test_thumbnail_size(self):
        img_name, r = self.upload()
        # get the thumbnail link
        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/%s/thumbnail/%s' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 301)
        imgio = test_utils.download_image(r.location)
        img = Image.open(imgio)
        self.assertEquals(img.size, app.config['THUMBNAIL_SIZE'])

    def test_resize(self):
        img_name, r = self.upload()
        img_w, img_h = self.get_image_size()

        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/%s/file/%s?size=100x0' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 301)
        resized_img = test_utils.download_image(r.location)
        resized_w, resized_h = self.get_image_size(resized_img)
        self.assertEquals(resized_w, 100)
        # check aspect ratio
        self.assertEquals(int(img_w/resized_w), int(img_h/resized_h))

    def test_resize2(self):
        img_name, r = self.upload()
        img_w, img_h = self.get_image_size()

        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/%s/file/%s?size=100x150' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 301)
        resized_img = test_utils.download_image(r.location)
        resized_w, resized_h = self.get_image_size(resized_img)

        self.assertEquals(resized_h, 150)
        # check aspect ratio
        if resized_w < img_w:
            self.assertEquals(int(img_w/resized_w), int(img_h/resized_h))
        else:
            self.assertEquals(int(resized_w/img_w), int(resized_h/img_h))

    def test_non_image_file(self):
        file_name, r = self.upload('../imgee/static/css/app.css')
        self.assertEquals(r.status_code, 200)
        self.assertTrue('Sorry, unknown image format' in r.data)

    def test_resize3_file(self):
        # non resizable images
        file_name, r = self.upload('../imgee/static/img/imgee.svg')
        file_id = test_utils.get_img_id(file_name)
        r1 = self.client.get('/%s/file/%s' % (self.test_user_name, file_id))
        r2 = self.client.get('/%s/file/%s?size=100x200' % (self.test_user_name, file_id))
        self.assertEquals(r1.status_code, 301)
        self.assertEquals(r2.status_code, 301)
        self.assertEquals(r1.location, r2.location)
        self.assertTrue(file_id in r2.location)

    def test_resize_single_dimension(self):
        img_name, r = self.upload()
        img_w, img_h = self.get_image_size()

        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/%s/file/%s?size=100' % (self.test_user_name, self.img_id))
        self.assertEquals(r.status_code, 301)
        resized_img = test_utils.download_image(r.location)
        resized_w, resized_h = self.get_image_size(resized_img)
        self.assertEquals(resized_w, 100)
        # check aspect ratio
        self.assertEquals(int(img_w/resized_w), int(img_h/resized_h))

    def tearDown(self):
        for s in StoredFile.query.all():
            storage.delete_on_s3(s)
        super(UploadTestCase, self).tearDown()


if __name__ == '__main__':
    unittest.main()
