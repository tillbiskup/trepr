import unittest

from trepr import dataset

class TestMetadataMapper(unittest.TestCase):
    def setUp(self):
        self.metadata_mapper = dataset.MetadataMapper()

