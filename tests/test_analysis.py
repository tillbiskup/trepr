import os
import unittest

import aspecd.exceptions
import numpy as np

import trepr.analysis
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestMwFreqAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysis = trepr.analysis.MwFreqAnalysis()
        source = os.path.join(ROOTPATH, 'testdata/speksim/')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_description(self):
        self.assertNotIn('Abstract', self.analysis.description)

    def test_analysis(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertTrue(analysis.result)

    def test_analyse_without_mw_frequency_dataset_raises(self):
        dataset = trepr.dataset.ExperimentalDataset()

        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.analyse(self.analysis)


class TestTimeStampAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysis = trepr.analysis.TimeStampAnalysis()
        source = os.path.join(ROOTPATH, 'testdata/speksim/')
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_description(self):
        self.assertNotIn('Abstract', self.analysis.description)

    def test_analysis(self):
        analysis = self.dataset.analyse(self.analysis)
        self.assertTrue(analysis.result)


class TestBasicCharacteristics(unittest.TestCase):

    def setUp(self):
        self.analysis = trepr.analysis.BasicCharacteristics()
        self.dataset = trepr.dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        pass

    def test_has_axis_parameter(self):
        self.assertTrue('axis' in self.analysis.parameters)

    def test_with_axis_and_index_results_in_scalar_value(self):
        self.dataset.data.data = np.random.random([5, 5])
        self.analysis.parameters['kind'] = 'max'
        self.analysis.parameters['output'] = 'indices'
        self.analysis.parameters['axis'] = 0
        analysis = self.dataset.analyse(self.analysis)
        self.assertNotIsInstance(analysis.result, list)

    def test_with_axis_and_value_ignores_axis(self):
        self.dataset.data.data = np.random.random([5, 5])
        self.analysis.parameters['kind'] = 'max'
        self.analysis.parameters['output'] = 'value'
        self.analysis.parameters['axis'] = 0
        analysis = self.dataset.analyse(self.analysis)
        self.assertNotIsInstance(analysis.result, list)

    def test_with_invalid_axis_value_raises(self):
        self.dataset.data.data = np.random.random([5, 5])
        self.analysis.parameters['kind'] = 'max'
        self.analysis.parameters['output'] = 'indices'
        self.analysis.parameters['axis'] = 2
        message = 'out of bounds'
        with self.assertRaisesRegex(IndexError, message):
            self.dataset.analyse(self.analysis)
