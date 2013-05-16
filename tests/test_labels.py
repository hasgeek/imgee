import unittest

from imgee import storage
from imgee.models import StoredFile
from fixtures import ImgeeTestCase
import test_utils


class LabelTestCase(ImgeeTestCase):
    def setUp(self):
        super(LabelTestCase, self).setUp()
        self.img_id = None
        self.test_files = ['imgee/static/img/imgee.png', ]
        self.test_labels = ['logos', 'banners', 'profile_photos']

    def upload(self, path=None):
        return test_utils.upload(self.client, path or self.test_files[0], '/%s/new' % self.test_user_name)

    def create_label(self, label=None):
        label = label or self.test_labels[0]
        response = self.client.post('/labels/new', data={'label': label}, follow_redirects=True)
        return response

    def test_empty(self):
        r = self.client.get('/%s' % self.test_user_name)
        self.assertEquals(r.status_code, 200)
        self.assertTrue('No Labels yet.' in r.data)

    def test_create_label(self):
        label = self.test_labels[0]
        r = self.create_label(label)
        self.assertEquals(r.status_code, 200)
        self.assertTrue(('The label %s was created.' % label) in r.data.replace('&#34;', ''))
        r = self.client.get('/%s' % self.test_user_name)
        self.assertTrue(label in r.data)

    def test_add_remove_label(self):
        # upload image
        img_name, r = self.upload()
        img_id = test_utils.get_img_id(r.data, img_name)
        # create label
        label = self.test_labels[0]
        self.create_label(label)
        # attach label to image
        save_label_url = '/%s/save_labels/%s' % (self.test_user_name, img_id)
        r = self.client.post(save_label_url, data={'label': [1]})
        self.assertTrue(r.status_code, 200)
        # check if the image is in the label page
        r = self.client.get('/%s/%s' % (self.test_user_name, label))
        self.assertTrue(r.status_code, 200)
        self.assertTrue(img_name in r.data)
        # remove the label from image
        r = self.client.post(save_label_url, data={'label': []})
        self.assertTrue(r.status_code, 200)
        # check that the image is NOT in the label page
        r = self.client.get('/%s/%s' % (self.test_user_name, label))
        self.assertTrue(r.status_code, 200)
        self.assertTrue('There are no images with label' in r.data)
        self.assertTrue('Removed label' in r.data)

    def test_delete_label(self):
        label = self.test_labels[0]
        self.create_label(label)
        delete_url = '/%s/%s/delete' % (self.test_user_name, label)
        r = self.client.post(delete_url, data={})
        self.assertTrue(r.status_code, 200)
        r = self.client.get('/%s' % self.test_user_name)
        self.assertTrue('was deleted' in r.data)
        r = self.client.get('/%s' % self.test_user_name)
        self.assertFalse(label in r.data)

    def tearDown(self):
        s = StoredFile.query.filter_by(name=self.img_id).first()
        if s:
            storage.delete_on_s3(s)
        super(LabelTestCase, self).tearDown()


if __name__ == '__main__':
    unittest.main()
