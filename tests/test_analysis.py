import os
import unittest

import aspecd.exceptions
import numpy as np

import trepr.analysis
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestMwFreqAnalysis(unittest.TestCase):
    def setUp(self):
        self.analysis = trepr.analysis.MWFrequencyDrift()
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

    def test_analyse_with_unknown_kind_raises(self):
        self.analysis.parameters["output"] = "value"
        self.analysis.parameters["kind"] = "foo"
        with self.assertRaisesRegex(ValueError, "Unknown kind foo"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_unknown_output_raises(self):
        self.analysis.parameters["output"] = "foo"
        with self.assertRaisesRegex(ValueError, "Unknown output type foo"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_output_value_returns_numpy_float(self):
        self.analysis.parameters['output'] = 'value'
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result, np.float64)

    def test_analyse_with_output_value_returns_correct_value(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 346.0])
        self.analysis.parameters['output'] = 'value'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(1, analysis.result, 2)

    def test_analyse_with_output_value_returns_correct_ratio(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.5000, 9.5028])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 346.0])
        self.analysis.parameters['output'] = 'value'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(0.1, analysis.result, 3)

    def test_analyse_with_kind_drift_returns_correct_value(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0])
        self.analysis.parameters['kind'] = 'drift'
        self.analysis.parameters['output'] = 'value'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(1, analysis.result, 2)

    def test_analyse_with_output_dataset_returns_calculated_dataset(self):
        self.analysis.parameters['output'] = 'dataset'
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result,
                              trepr.dataset.CalculatedDataset)

    def test_output_dataset_kind_drift_contains_field_drifts_as_data(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528, 9.556])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'drift'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(1, analysis.result.data.data[0], 2)

    def test_output_dataset_kind_ratio_contains_drift_ratio_as_data(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528, 9.556])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'ratio'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(0.5, analysis.result.data.data[0], 2)

    def test_output_dataset_contains_field_axis_as_first_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528, 9.556])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'drift'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(346.0,
                               analysis.result.data.axes[0].values[0], 2)
        self.assertEqual(dataset.microwave_frequency.axes[0].quantity,
                         analysis.result.data.axes[0].quantity)
        self.assertEqual(dataset.microwave_frequency.axes[0].unit,
                         analysis.result.data.axes[0].unit)

    def test_output_dataset_kind_drift_has_correct_second_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528, 9.556])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'drift'
        analysis = dataset.analyse(self.analysis)
        self.assertEqual('drift', analysis.result.data.axes[1].quantity)
        self.assertEqual('mT', analysis.result.data.axes[1].unit)

    def test_output_dataset_kind_ratio_has_correct_second_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.microwave_frequency.data = np.asarray([9.500, 9.528, 9.556])
        dataset.microwave_frequency.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'ratio'
        analysis = dataset.analyse(self.analysis)
        self.assertEqual('drift/(field step size)',
                         analysis.result.data.axes[1].quantity)
        self.assertEqual('', analysis.result.data.axes[1].unit)


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


class TestMWFrequencyValues(unittest.TestCase):

    def setUp(self):
        self.analysis = trepr.analysis.MWFrequencyValues()
        self.dataset = trepr.dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        pass

    def test_has_sensible_description(self):
        self.assertIn('Extract MW frequency values',
                      self.analysis.description)

    def test_needs_mw_frequency_values_in_dataset(self):
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_analysis_returns_calculated_dataset(self):
        self.dataset.microwave_frequency.data = np.random.random(5)
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result,
                              trepr.dataset.CalculatedDataset)

    def test_returned_dataset_contains_mw_frequency_values(self):
        self.dataset.microwave_frequency.data = np.random.random(5)
        analysis = self.dataset.analyse(self.analysis)
        self.assertListEqual(list(self.dataset.microwave_frequency.data),
                             list(analysis.result.data.data))

    def test_returned_dataset_contains_magnetic_field_axis(self):
        self.dataset.microwave_frequency.data = np.random.random(5)
        self.dataset.microwave_frequency.axes[0].values = \
            np.linspace(340, 350, 5)
        analysis = self.dataset.analyse(self.analysis)
        self.assertListEqual(
            list(self.dataset.microwave_frequency.axes[0].values),
            list(analysis.result.data.axes[0].values))

    def test_returned_dataset_has_mw_frequency_axis_as_second_axis(self):
        self.dataset.microwave_frequency.data = np.random.random(5)
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(self.dataset.microwave_frequency.axes[1],
                             analysis.result.data.axes[1])
