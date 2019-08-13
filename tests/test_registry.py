import time
import unittest
from werkzeug.datastructures import FileStorage

from imgee import registry
from .fixtures import ImgeeTestCase


class RegistryTestCase(ImgeeTestCase):
    def setUp(self):
        super(RegistryTestCase, self).setUp()
        self.test_key = 'testkey'
        self.test_key2 = self.test_key + '_second'

    def tearDown(self):
        super(RegistryTestCase, self).tearDown()
        registry.remove_all()  # this is called after every test method runs

    def test_invalid_query(self):
        assert registry.is_valid_query('SREM keyname') is False

    def test_valid_query(self):
        assert registry.is_valid_query('keyname') is True

    def test_key_addition(self):
        registry.add(self.test_key)
        assert self.test_key in registry

    def test_key_expiry(self):
        registry.add(self.test_key, 2)
        assert self.test_key in registry
        time.sleep(3)
        assert self.test_key not in registry

    def test_search(self):
        registry.add(self.test_key)
        assert (
            len(registry.search(self.test_key[:4])) == 1
        )  # searching for a part of the key

    def test_key_removal(self):
        registry.add(self.test_key)
        assert self.test_key in registry
        registry.remove(self.test_key)
        assert self.test_key not in registry

    def test_multiple_key_removal_starting_with(self):
        registry.add(self.test_key)
        registry.add(self.test_key2)

        assert len(registry.get_all_keys()) == 2
        registry.remove_keys_starting_with(self.test_key)
        assert len(registry.get_all_keys()) == 0


if __name__ == '__main__':
    unittest.main()
