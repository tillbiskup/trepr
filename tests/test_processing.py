import os
import unittest

import trepr.processing
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestAveraging(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.Averaging()
        source = os.path.join(ROOTPATH, 'testdata/pentacene')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing(self):
        self.processing.parameters['dimension'] = 0
        self.processing.parameters['range'] = [1.99952828e-06, 2.23752827e-06]# [1.99e-6, 3.6e-6]
        self.processing.parameters['unit'] = 'axis'
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))


if __name__ == '__main__':
    unittest.main()
