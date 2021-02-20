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
        self.processing.parameters['range'] = [1.99e-6, 3.6e-6]
        self.processing.parameters['unit'] = 'axis'
        self.dataset.process(self.processing)
        self.assertEqual(2, len(self.dataset.data.axes))
        self.assertIn('field', self.dataset.data.axes[0].quantity)


class TestPretriggerOffsetCompensation(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.PretriggerOffsetCompensation()
        source = os.path.join(ROOTPATH, 'testdata/pentacene')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing(self):
        self.dataset.process(self.processing)


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.Normalisation()
        source = os.path.join(ROOTPATH, 'testdata/pentacene')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing_maximum(self):
        self.processing.parameters['type'] = "maximum"
        self.dataset.process(self.processing)

    def test_processing_area(self):
        self.processing.parameters['type'] = "area"
        self.dataset.process(self.processing)


if __name__ == '__main__':
    unittest.main()
