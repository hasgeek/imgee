#import os
import unittest
import requests
from PIL import Image

from imgee.models import StoredFile, Thumbnail
from imgee.views import upload_file
from fixtures import ImgeeTestCase, app
import test_utils


class ImgeeBaseTest(ImgeeTestCase):
    def setUp(self):
        super(ImgeeBaseTest, self).setUp()
        self.img_id = None
        self.test_file = '../imgee/static/img/imgee.jpeg'

    def upload(self, path=None):
        return test_utils.upload(self.client, path or self.test_file, '/%s/new' % self.test_user_name)

    def exists_on_media_domain(self, img_id):
        r = self.client.get('/embed/file/%s' % (img_id))
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok

    def thumbnails_exists_on_media_domain(self, img_id):
        r = self.client.get('/embed/thumbnail/%s' % (img_id))
        self.assertEquals(r.status_code, 301)
        return requests.get(r.location).ok


class TestEmpty(ImgeeBaseTest):
    def test_empty(self):
        r = self.client.get('/%s' % self.test_user_name)
        self.assertEquals(r.status_code, 200)
        self.assertEquals(len(StoredFile.query.all()), 0)


class TestUpload(ImgeeBaseTest):
    def setUp(self):
        super(TestUpload, self).setUp()
        self.filetitle, self.r = self.upload()
        self.img_id = test_utils.get_img_id(self.filetitle)

    def test_upload(self):
        self.assertEquals(self.r.status_code, 200)
        self.assertEquals(len(StoredFile.query.filter_by(title=self.filetitle).all()), 1)

    def test_view_image(self):
        view_url = '/%s/view/%s' % (self.test_user_name, self.img_id)
        r = self.client.get(view_url)
        self.assertEquals(r.status_code, 200)

    def test_file(self):
        self.assertTrue(self.exists_on_media_domain(self.img_id))

    def test_thumbnail(self):
        self.assertTrue(self.thumbnails_exists_on_media_domain(self.img_id))
        img = StoredFile.query.filter_by(name=self.img_id).first()
        self.assertEquals(len(img.thumbnails), 1)

    def test_delete(self):
        filetitle, r = self.upload()
        self.img_id = test_utils.get_img_id(filetitle)

        # check if the file and thumbnail exists
        self.assertTrue(self.exists_on_media_domain(self.img_id))
        self.assertTrue(self.thumbnails_exists_on_media_domain(self.img_id))

        r = self.client.post('/%s/delete/%s' % (self.test_user_name, self.img_id))

        # check if the file exists now
        r = self.client.get('/embed/file/%s' % (self.img_id))
        self.assertEquals(r.status_code, 404)

        # check if the thumbnail exists
        r = self.client.get('/embed/thumbnail/%s' % (self.img_id))
        self.assertEquals(r.status_code, 404)

    def test_file_count(self):
        # if the same file is uploaded twice, imgee should treat them as different
        filetitle2, r2 = self.upload()
        self.assertEquals(self.filetitle, filetitle2)

        imgs = StoredFile.query.filter_by(title=self.filetitle).all()
        self.assertEquals(len(imgs), 2)

    def test_thumbnail_size(self):
        img_name, r = self.upload()
        # get the thumbnail link
        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/embed/thumbnail/%s' % (self.img_id))
        self.assertEquals(r.status_code, 301)
        imgio = test_utils.download_image(r.location)
        img = Image.open(imgio)
        self.assertEquals('%sx%s' % img.size, app.config.get('THUMBNAIL_SIZE'))

    def test_non_image_file(self):
        file_name, r = self.upload('../imgee/static/css/app.css')
        self.assertEquals(r.status_code, 200)
        self.assertTrue('Sorry, unknown image format' in r.data)


class TestResize(ImgeeBaseTest):
    def get_image_size(self, img_path=None):
        self.test_file = '../imgee/static/img/imgee.jpeg'
        return test_utils.get_image_size(img_path or self.test_file)

    def test_resize(self):
        img_name, r = self.upload()
        img_w, img_h = self.get_image_size()

        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/embed/file/%s?size=100x0' % (self.img_id))
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
        r = self.client.get('/embed/file/%s?size=100x150' % (self.img_id))
        self.assertEquals(r.status_code, 301)
        resized_img = test_utils.download_image(r.location)
        resized_w, resized_h = self.get_image_size(resized_img)

        self.assertEquals(resized_w, 100)
        # check aspect ratio
        if resized_w < img_w:
            self.assertEquals(int(img_w/resized_w), int(img_h/resized_h))
        else:
            self.assertEquals(int(resized_w/img_w), int(resized_h/img_h))

    def test_resize3_file(self):
        # non resizable images
        file_name, r = self.upload('../imgee/static/img/imgee.svg')
        file_id = test_utils.get_img_id(file_name)
        r1 = self.client.get('/embed/file/%s' % (file_id))
        r2 = self.client.get('/embed/file/%s?size=100x200' % (file_id))
        self.assertEquals(r1.status_code, 301)
        self.assertEquals(r2.status_code, 301)
        self.assertEquals(r1.location, r2.location)
        self.assertTrue(file_id in r2.location)

    def test_resize_single_dimension(self):
        img_name, r = self.upload()
        img_w, img_h = self.get_image_size()

        self.img_id = test_utils.get_img_id(img_name)
        r = self.client.get('/embed/file/%s?size=100' % (self.img_id))
        self.assertEquals(r.status_code, 301)
        resized_img = test_utils.download_image(r.location)
        resized_w, resized_h = self.get_image_size(resized_img)
        self.assertEquals(resized_w, 100)
        # check aspect ratio
        self.assertEquals(int(img_w/resized_w), int(img_h/resized_h))


if __name__ == '__main__':
    unittest.main()
