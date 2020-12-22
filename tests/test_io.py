import collections
import os
import shutil
import unittest

import trepr.io
import trepr.dataset


class TestTezImporter(unittest.TestCase):
    def setUp(self):
        self.source = '/Users/mirjamschroder/Programmierkram/Python/test-data' \
                 '/Sa678-04'
        self.importer = trepr.io.TezImporter(source=self.source)
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.tempdir = os.path.join(os.path.split(self.source)[0], 'tmp')


    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_importer(self):
        self.dataset.import_from(self.importer)

    def test_converted_xml_is_dict(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(collections.OrderedDict, type(self.importer.xml_dict))

    def test_axes_are_created(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(3, len(self.importer.dataset.data.axes))




if __name__ == '__main__':
    unittest.main()
