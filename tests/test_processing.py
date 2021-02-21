import os
import unittest

import numpy as np

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
        self.assertNotIn('time', self.dataset.data.axes[1].quantity)

    def test_processing_raises_if_range_descending(self):
        self.processing.parameters['dimension'] = 0
        self.processing.parameters['range'] = [5e-6, 3.6e-6]
        self.processing.parameters['unit'] = 'axis'
        with self.assertRaises(trepr.processing.RangeError):
            self.dataset.process(self.processing)

    def test_processing_raises_if_dimension_is_wrong(self):
        self.processing.parameters['dimension'] = 2
        self.processing.parameters['range'] = [2e-6, 3.6e-6]
        self.processing.parameters['unit'] = 'axis'
        with self.assertRaises(trepr.processing.DimensionError):
            self.dataset.process(self.processing)

    def test_processing_raises_if_range_is_off(self):
        self.processing.parameters['dimension'] = 1
        self.processing.parameters['range'] = [2e-6, 3e-2]
        self.processing.parameters['unit'] = 'axis'
        with self.assertRaises(trepr.processing.RangeError):
            self.dataset.process(self.processing)

    def test_processing_raises_if_unit_is_wrong(self):
        self.processing.parameters['dimension'] = 1
        self.processing.parameters['range'] = [2e-6, 3.6e-6]
        self.processing.parameters['unit'] = 'foo'
        with self.assertRaises(trepr.processing.UnitError):
            self.dataset.process(self.processing)


class TestPretriggerOffsetCompensation(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.PretriggerOffsetCompensation()
        source = os.path.join(ROOTPATH, 'testdata/speksim/')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing(self):
        self.dataset.process(self.processing)

    def test_zeropoint_index(self):
        self.processing.dataset = self.dataset
        self.processing._get_zeropoint_index()
        self.assertNotEqual(0, self.processing.parameters['zeropoint_index'])


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.Normalisation()
        source = os.path.join(ROOTPATH, 'testdata/pentacene')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing_maximum(self):
        self.processing.parameters['type'] = "maximum"
        self.dataset.process(self.processing)
        self.assertEqual(1, np.amax(self.dataset.data.data))

    def test_processing_area(self):
        self.processing.parameters['type'] = "area"
        self.dataset.process(self.processing)
        self.assertEqual(1, sum(abs(self.dataset.data.data)).all())

    def test_processing_without_parameter(self):
        self.processing.parameters['type'] = ""
        self.dataset.process(self.processing)
        self.assertEqual(1, sum(abs(self.dataset.data.data)).all())


if __name__ == '__main__':
    unittest.main()
