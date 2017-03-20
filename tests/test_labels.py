import unittest

from imgee import storage
from imgee.models import StoredFile, Label, db, User, Profile
from fixtures import ImgeeTestCase
import test_utils


class LabelTestCase(ImgeeTestCase):
    def setUp(self):
        super(LabelTestCase, self).setUp()
        self.img_id = None
        self.test_files = ['../imgee/static/img/imgee.png', ]
        self.test_labels = ['logos', 'banners', 'profile-photos']

    def upload(self, path=None):
        return test_utils.upload(self.client, path or self.test_files[0], '/%s/new' % self.test_user_name)

    def create_label(self, label=None):
        label = label or self.test_labels[0]
        response = self.client.post('/%s/newlabel' % self.test_user_name, data={'label': label}, follow_redirects=True)
        return response

    def test_empty(self):
        r = self.client.get('/%s' % self.test_user_name)
        self.assertEquals(r.status_code, 200)
        self.assertEquals(len(Label.query.all()), 0)

    def test_create_label(self):
        label = self.test_labels[0]
        r = self.create_label(label)
        self.assertEquals(r.status_code, 200)
        self.assertEquals(len(Label.query.filter_by(title=label).all()), 1)

    def test_add_remove_label(self):
        # upload image
        img_title, r = self.upload()
        print img_title, r
        img = StoredFile.query.filter_by(title=unicode(img_title)).one()
        img_id, img_name = img.id, img.name
        self.assertFalse(img.labels)

        # create label
        label = self.test_labels[0]
        self.create_label(label)
        # attach label to image
        save_label_url = '/%s/save_labels/%s' % (self.test_user_name, img_name)
        r = self.client.post(save_label_url, data={'labels': label})

        img = StoredFile.query.get(img_id)
        self.assertEquals(len(img.labels), 1)

        r = self.client.get('/%s/%s' % (self.test_user_name, label))
        self.assertEquals(r.status_code, 200)

        # remove the label from image
        r = self.client.post(save_label_url, data={'labels': ''})
        img = StoredFile.query.get(img_id)
        self.assertEquals(len(img.labels), 0)

    def test_delete_label(self):
        label = self.test_labels[0]
        r = self.create_label(label)
        r = self.client.get('/%s/%s' % (self.test_user_name, label))
        self.assertEquals(r.status_code, 200)
        delete_url = '/%s/%s/delete' % (self.test_user_name, label)
        r = self.client.post(delete_url, data={})
        self.assertTrue(r.status_code, 200)
        r = self.client.get('/%s/%s', self.test_user_name, label)
        self.assertEquals(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()
