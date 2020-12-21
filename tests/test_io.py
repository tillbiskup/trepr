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

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_importer(self):
        self.tempdir = os.path.join(os.path.split(self.source)[0], 'tmp')
        self.dataset.import_from(self.importer)

    def test_converted_xml_is_dict(self):
        self.tempdir = os.path.join(os.path.split(self.source)[0], 'tmp')
        self.dataset.import_from(self.importer)



if __name__ == '__main__':
    unittest.main()
