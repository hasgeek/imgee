import unittest

import pytest
from werkzeug.datastructures import FileStorage

from imgee.models import Label, StoredFile
from imgee.storage import save_file
from imgee.views.labels import utils_delete_label, utils_save_label, utils_save_labels

from .fixtures import ImgeeTestCase


class LabelTestCase(ImgeeTestCase):
    def setUp(self):
        super().setUp()
        self.img_id = None
        self.test_files = ['imgee/static/img/imgee.png']
        self.test_labels = ['logos', 'banners', 'profile-photos']

    def upload(self, path=None):
        profile = self.get_test_profile()
        sf = None
        with open(path or self.test_files[0], 'rb') as fp:
            fs = FileStorage(fp)
            title, sf = save_file(fs, profile)
        return sf

    def test_empty(self):
        self.assertEqual(len(Label.query.all()), 0)

    def test_create_label(self):
        label_title = self.test_labels[0]
        utils_save_label(label_title, self.get_test_profile())
        self.assertEqual(len(Label.query.filter_by(title=label_title).all()), 1)

    @pytest.mark.enable_socket()
    def test_add_remove_label(self):
        # upload image
        img = self.upload()
        img_id = img.id
        self.assertFalse(img.labels)

        # create label
        label = self.test_labels[0]
        # attach label to image
        total_saved, msg = utils_save_labels(label, img, self.get_test_profile())
        self.assertEqual(total_saved, 1)

        img = StoredFile.query.get(img_id)
        self.assertEqual(len(img.labels), 1)

        self.assertEqual(len(self.get_test_profile().labels), 1)

        # remove the label from image
        total_saved, msg = utils_save_labels([], img, self.get_test_profile())
        img = StoredFile.query.get(img_id)
        self.assertEqual(len(img.labels), 0)

    def test_delete_label(self):
        label_title = self.test_labels[0]
        # create label
        utils_save_label(label_title, self.get_test_profile())
        # delete label
        utils_delete_label(label_title)
        self.assertEqual(len(Label.query.filter_by(title=label_title).all()), 0)


if __name__ == '__main__':
    unittest.main()
