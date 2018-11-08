import unittest

from trepr import dataset

class TestMetadataMapper(unittest.TestCase):
    def setUp(self):
        self.metadata_mapper = dataset.MetadataMapper()

    def test_instantiate_class(self):
        pass

    def test_has_method_rename_key(self):
        self.assertTrue(callable(self.metadata_mapper.rename_key))

    def test_rename_key(self):
        new_key = 'foo'
        old_key = 'bar'
        self.metadata_mapper.metadata[old_key] = 'bar'
        self.metadata_mapper.rename_key(old_key, new_key)
        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        self.assertFalse(old_key in self.metadata_mapper.metadata.keys())

    def test_has_method_combine_items(self):
        self.assertTrue(callable(self.metadata_mapper.combine_items))

    def test_combine_items(self):
        old_keys = ['key1', 'key2']
        new_key = 'new_key'
        self.metadata_mapper.metadata = {'key1':'bla', 'key2':'blub'}
        self.metadata_mapper.combine_items(old_keys, new_key)
        self.assertTrue(new_key in self.metadata_mapper.metadata.keys())
        for key in old_keys:
            self.assertFalse(key in self.metadata_mapper.metadata.keys())
        self.assertEqual(self.metadata_mapper.metadata[new_key], 'bla blub')

