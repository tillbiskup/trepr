import os
import unittest

import aspecd.exceptions
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


class TestBackgroundCorrection(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.BackgroundCorrection()
        self.dataset = trepr.dataset.ExperimentalDataset()

    def create_dataset(self):
        data = np.ones([500, 200])
        data[10:-10] += 4
        self.dataset.data.data = data

    def test_description(self):
        self.create_dataset()
        self.assertNotIn('abstract', self.processing.description.lower())
        self.assertIn('background', self.processing.description.lower())

    def test_1D_dataset_raises(self):
        self.dataset.data.data = np.ones(200)
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.process(self.processing)

    def test_too_small_dataset_raises(self):
        self.dataset.data.data = np.ones((5, 20))
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.process(self.processing)

    def test_perform_task_with_defaults(self):
        self.create_dataset()
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])

    def test_perform_task_with_list_one_element(self):
        self.create_dataset()
        self.processing.parameters['num_profiles'] = [-10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])

    def test_perform_task_with_list_two_elements(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters['num_profiles'] = [10, -10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)

    def test_perform_task_with_list_two_other_elements(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters['num_profiles'] = [5, 10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)

    def test_perform_task_with_tuple(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters['num_profiles'] = 5, 10
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)


class TestFrequencyCorrection(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.FrequencyCorrection()
        self.dataset = trepr.dataset.ExperimentalDataset()
        data = np.ones([301, 200])
        data[10:-10] += 4
        self.dataset.data.data = data
        self.dataset.metadata.bridge.mw_frequency.value = 10.
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[0].values = np.linspace(200, 500, num=301)

    def test_correction(self):
        old_field_axis = np.copy(self.dataset.data.axes[0].values)
        self.processing.parameters['frequency'] = 8.
        self.dataset.process(self.processing)
        new_field_axis = self.dataset.data.axes[0].values
        diffs = old_field_axis - new_field_axis
        conditions = (diff == 0 for diff in diffs)
        self.assertFalse(all(conditions))


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.filter = trepr.processing.Filter()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.linspace(1, 100)

    def test_type_savgol(self):
        savgols = ['savitzky_golay', 'savitzky-golay', 'savitzky golay',
                       'savgol', 'savitzky']
        for filter_ in savgols:
            self.filter.parameters['type'] = filter_
            self.filter._get_type()
            self.assertEqual('savitzky_golay', self.filter.parameters['type'])

    def test_type_binom(self):
        filters = ['binom', 'binomial']
        for filter_ in filters:
            self.filter.parameters['type'] = filter_
            filter = self.dataset.process(self.filter)  # works on a copy...
            self.assertEqual('binomial', filter.parameters['type'])

    def test_type_boxcar(self):
        filters = ['box', 'boxcar', ]
        for filter_ in filters:
            self.filter.parameters['type'] = filter_
            filter = self.dataset.process(self.filter)  # works on a copy...
            self.assertEqual('boxcar', filter.parameters['type'])

    def test_window_length_is_odd(self):
        self.filter.parameters['type'] = 'savgol'
        self.filter.parameters['window_length'] = 30
        with self.assertRaises(ValueError):
            self.dataset.process(self.filter)


if __name__ == '__main__':
    unittest.main()
