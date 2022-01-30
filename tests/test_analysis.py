import datetime
import os
import unittest

import aspecd.dataset
import aspecd.exceptions
import numpy as np
from scipy.fft import rfft, rfftfreq

import trepr.analysis
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestMWFrequencyDrift(unittest.TestCase):
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
                              aspecd.dataset.CalculatedDataset)

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

    def test_analyse_without_time_stamp_dataset_raises(self):
        dataset = trepr.dataset.ExperimentalDataset()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.analyse(self.analysis)

    def test_analyse_with_unknown_output_raises(self):
        self.analysis.parameters["output"] = "foo"
        with self.assertRaisesRegex(ValueError, "Unknown output type foo"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_unknown_kind_raises(self):
        self.analysis.parameters["kind"] = "foo"
        with self.assertRaisesRegex(ValueError, "Unknown kind foo"):
            self.dataset.analyse(self.analysis)

    def test_analyse_with_output_values_returns_list(self):
        self.analysis.parameters['output'] = 'values'
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result, list)

    def test_analyse_w_output_values_and_delta_returns_delta_in_seconds(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        self.analysis.parameters['output'] = 'values'
        self.analysis.parameters['kind'] = 'delta'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(10, analysis.result[0], 2)

    def test_analyse_w_output_values_delta_returns_only_positive_values(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        self.analysis.parameters['output'] = 'values'
        self.analysis.parameters['kind'] = 'delta'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(10, analysis.result[0], 2)

    def test_analyse_w_output_values_and_time_returns_times_in_seconds(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        self.analysis.parameters['output'] = 'values'
        self.analysis.parameters['kind'] = 'time'
        analysis = dataset.analyse(self.analysis)
        self.assertListEqual([0, 10], analysis.result)

    def test_analyse_w_output_values_time_returns_non_negative_values(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        self.analysis.parameters['output'] = 'values'
        self.analysis.parameters['kind'] = 'time'
        analysis = dataset.analyse(self.analysis)
        self.assertTrue(all([value >= 0 for value in analysis.result]))

    def test_analyse_with_output_dataset_returns_calculated_dataset(self):
        self.analysis.parameters['output'] = 'dataset'
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result,
                              aspecd.dataset.CalculatedDataset)

    def test_output_dataset_with_delta_has_time_deltas_as_data(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'delta'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(10, analysis.result.data.data[0], 2)

    def test_output_dataset_with_delta_has_field_axis_as_first_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        dataset.time_stamp.axes[0].quantity = 'magnetic field'
        dataset.time_stamp.axes[0].unit = 'mT'
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'delta'
        analysis = dataset.analyse(self.analysis)
        self.assertAlmostEqual(347.0,
                               analysis.result.data.axes[0].values[0], 2)
        self.assertEqual(dataset.time_stamp.axes[0].quantity,
                         analysis.result.data.axes[0].quantity)
        self.assertEqual(dataset.time_stamp.axes[0].unit,
                         analysis.result.data.axes[0].unit)

    def test_output_dataset_with_delta_has_correct_second_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'delta'
        analysis = dataset.analyse(self.analysis)
        self.assertEqual('Delta time', analysis.result.data.axes[1].quantity)
        self.assertEqual('s', analysis.result.data.axes[1].unit)

    def test_output_dataset_with_time_has_time_as_data(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'time'
        analysis = dataset.analyse(self.analysis)
        self.assertListEqual([0, 10, 20], list(analysis.result.data.data))

    def test_output_dataset_with_time_has_field_axis_as_first_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        dataset.time_stamp.axes[0].quantity = 'magnetic field'
        dataset.time_stamp.axes[0].unit = 'mT'
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'time'
        analysis = dataset.analyse(self.analysis)
        self.assertListEqual([345.0, 347.0, 349.0],
                             list(analysis.result.data.axes[0].values))
        self.assertEqual(dataset.time_stamp.axes[0].quantity,
                         analysis.result.data.axes[0].quantity)
        self.assertEqual(dataset.time_stamp.axes[0].unit,
                         analysis.result.data.axes[0].unit)

    def test_output_dataset_with_time_has_correct_second_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.time_stamp.data = np.asarray([
            datetime.datetime.strptime('Mon Feb 11 16:21:01 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:11 2013',
                                       '%a %b %d %H:%M:%S %Y'),
            datetime.datetime.strptime('Mon Feb 11 16:21:21 2013',
                                       '%a %b %d %H:%M:%S %Y'),
        ])
        dataset.time_stamp.axes[0].values = \
            np.asarray([345.0, 347.0, 349.0])
        self.analysis.parameters['output'] = 'dataset'
        self.analysis.parameters['kind'] = 'time'
        analysis = dataset.analyse(self.analysis)
        self.assertEqual('time', analysis.result.data.axes[1].quantity)
        self.assertEqual('s', analysis.result.data.axes[1].unit)


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


class TestTransientNutationFFT(unittest.TestCase):

    def setUp(self):
        self.analysis = trepr.analysis.TransientNutationFFT()
        self.dataset = trepr.dataset.ExperimentalDataset()

    def create_time_trace(self, raising_flank=True):
        """
        Create a time trace with an oscillation (transient nutation).

        A tr-EPR time trace showing transient nutations can be described by a
        zero-order Bessel function of first kind. Due to relaxation,
        the Bessel function is damped with an exponential.

        To add a raising flank to the time trace, the damped Bessel function
        is convoluted with a Gaussian.
        """
        from scipy.special import j0

        n_points = 1000

        x = np.linspace(0, 10, n_points)
        bessel = j0(x * 2 * np.pi)
        time_trace = bessel * np.exp(-0.4 * x)

        # Gaussian for convolution to get raising flank
        x2 = np.linspace(-2, 2, int(n_points / 5))
        amplitude = 1
        position = 0
        width = 2
        gaussian = amplitude * np.exp(-(x2 - position)**2 / 2 * width**2)

        if raising_flank:
            time_trace = np.insert(time_trace, 0, np.zeros(int(n_points / 10)))
            time_trace = np.convolve(time_trace, gaussian)
            self.dataset.data.axes[0].values = \
                np.linspace(-1, 9, n_points) * 1e-6
        else:
            self.dataset.data.axes[0].values = x * 1e-6

        self.dataset.data.data = time_trace[:n_points]
        self.dataset.data.axes[0].quantity = 'time'
        self.dataset.data.axes[0].unit = 's'
        self.dataset.data.axes[1].quantity = 'intensity'
        self.dataset.data.axes[1].unit = 'V'

    def plot_1D(self, dataset=None):
        import trepr.plotting
        import matplotlib.pyplot as plt
        plotter = trepr.plotting.SinglePlotter1D()
        if dataset:
            dataset.plot(plotter)
        else:
            self.dataset.plot(plotter)
        plt.show()

    def plot_2D(self, dataset=None):
        import trepr.plotting
        import matplotlib.pyplot as plt
        plotter = trepr.plotting.SinglePlotter2D()
        if dataset:
            dataset.plot(plotter)
        else:
            self.dataset.plot(plotter)
        plt.show()

    def test_instantiate_class(self):
        pass

    def test_has_sensible_description(self):
        self.assertIn('Perform FFT to extract transient nutation frequencies',
                      self.analysis.description)

    def test_requires_time_axis(self):
        with self.assertRaises(
                aspecd.exceptions.NotApplicableToDatasetError):
            self.dataset.analyse(self.analysis)

    def test_analysis_returns_calculated_dataset(self):
        self.create_time_trace()
        analysis = self.dataset.analyse(self.analysis)
        self.assertIsInstance(analysis.result,
                              aspecd.dataset.CalculatedDataset)

    def test_axis_contains_frequencies(self):
        self.create_time_trace(raising_flank=False)
        analysis = self.dataset.analyse(self.analysis)

        xt = rfftfreq(len(self.dataset.data.data),
                      float(np.diff(self.dataset.data.axes[0].values[-2:])))
        self.assertListEqual(list(xt),
                             list(analysis.result.data.axes[0].values))

    def test_cuts_negative_time_values(self):
        self.create_time_trace(raising_flank=True)
        self.analysis.parameters['start_in_extremum'] = False
        analysis = self.dataset.analyse(self.analysis)

        zero_index = np.argmin(np.abs(self.dataset.data.axes[0].values))
        xt = rfftfreq(len(self.dataset.data.data[zero_index:]),
                      float(np.diff(self.dataset.data.axes[0].values[-2:])))

        self.assertListEqual(list(xt),
                             list(analysis.result.data.axes[0].values))

    def test_cuts_in_extremum(self):
        self.create_time_trace(raising_flank=True)
        self.analysis.parameters['start_in_extremum'] = True
        analysis = self.dataset.analyse(self.analysis)

        cut_index = np.argmax(np.abs(self.dataset.data.data))
        xt = rfftfreq(len(self.dataset.data.data[cut_index:]),
                      float(np.diff(self.dataset.data.axes[0].values[-2:])))

        self.assertListEqual(list(xt),
                             list(analysis.result.data.axes[0].values))

    def test_cuts_in_negative_extremum(self):
        self.create_time_trace()
        self.dataset.data.data *= -1
        self.analysis.parameters['start_in_extremum'] = True
        analysis = self.dataset.analyse(self.analysis)

        cut_index = np.argmax(np.abs(self.dataset.data.data))
        xt = rfftfreq(len(self.dataset.data.data[cut_index:]),
                      float(np.diff(self.dataset.data.axes[0].values[-2:])))

        self.assertListEqual(list(xt),
                             list(analysis.result.data.axes[0].values))

    def test_padding(self):
        self.create_time_trace()
        self.analysis.parameters['padding'] = 5
        analysis = self.dataset.analyse(self.analysis)
        cut_index = np.argmax(np.abs(self.dataset.data.data))
        xt = rfftfreq(len(self.dataset.data.data[cut_index:]) * 5,
                      float(np.diff(self.dataset.data.axes[0].values[-2:])))
        self.assertEqual(len(xt),
                         len(analysis.result.data.data))

    def test_subtract_decay(self):
        self.create_time_trace()
        self.dataset.data.data += \
            15 * np.exp(-2e5 * self.dataset.data.axes[0].values)
        self.analysis.parameters['padding'] = 10
        self.analysis.parameters['subtract_decay'] = True
        analysis = self.dataset.analyse(self.analysis)
        # The frequency is about 1e6 Hz (slightly larger)
        self.assertLess(1e6, analysis.result.data.axes[0].values[
            np.argmax(analysis.result.data.data)])

    def test_apodisation_with_window(self):
        self.create_time_trace()
        self.dataset.data.data += \
            15 * np.exp(-2e5 * self.dataset.data.axes[0].values)
        self.analysis.parameters['padding'] = 10
        self.analysis.parameters['subtract_decay'] = True
        analysis = self.dataset.analyse(self.analysis)
        self.analysis.parameters['window'] = 'hann'
        analysis_window = self.dataset.analyse(self.analysis)
        # Assuming the standard deviation of the high-frequency tail to be
        # smaller for the apodised signal than the non-apodised one.
        self.assertLess(np.std(analysis_window.result.data.data[2000:]),
                        np.std(analysis.result.data.data[2000:]))

    def test_apodisation_with_window_with_parameter(self):
        self.create_time_trace()
        self.dataset.data.data += \
            15 * np.exp(-2e5 * self.dataset.data.axes[0].values)
        self.analysis.parameters['padding'] = 10
        self.analysis.parameters['subtract_decay'] = True
        analysis = self.dataset.analyse(self.analysis)
        self.analysis.parameters['window'] = 'kaiser'
        self.analysis.parameters['window_parameters'] = 3
        analysis_window = self.dataset.analyse(self.analysis)
        # Assuming the standard deviation of the high-frequency tail to be
        # smaller for the apodised signal than the non-apodised one.
        self.assertLess(np.std(analysis_window.result.data.data[2000:]),
                        np.std(analysis.result.data.data[2000:]))

    def test_apodisation_with_window_with_two_parameters(self):
        self.create_time_trace()
        self.dataset.data.data += \
            15 * np.exp(-2e5 * self.dataset.data.axes[0].values)
        self.analysis.parameters['padding'] = 10
        self.analysis.parameters['subtract_decay'] = True
        analysis = self.dataset.analyse(self.analysis)
        self.analysis.parameters['window'] = 'general_gaussian'
        self.analysis.parameters['window_parameters'] = [0.5, 2e2]
        analysis_window = self.dataset.analyse(self.analysis)
        # Assuming the standard deviation of the high-frequency tail to be
        # smaller for the apodised signal than the non-apodised one.
        self.assertLess(np.std(analysis_window.result.data.data[2000:]),
                        np.std(analysis.result.data.data[2000:]))

    def test_frequency_axis_has_correct_quantity_and_unit(self):
        self.create_time_trace()
        analysis = self.dataset.analyse(self.analysis)
        self.assertIn('Hz', analysis.result.data.axes[0].unit)
        self.assertEqual('frequency', analysis.result.data.axes[0].quantity)

    def test_intensity_axis_has_correct_quantity(self):
        self.create_time_trace()
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual(self.dataset.data.axes[-1].quantity,
                         analysis.result.data.axes[-1].quantity)

    def test_intensity_axis_has_no_unit_any_more(self):
        self.create_time_trace()
        analysis = self.dataset.analyse(self.analysis)
        self.assertEqual('', analysis.result.data.axes[-1].unit)

    def test_with_2D_dataset_returns_2D_dataset(self):
        self.create_time_trace()
        self.dataset.data.data = np.vstack((self.dataset.data.data,
                                            self.dataset.data.data))
        self.dataset.data.axes[0].values = [345., 346.]
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'time'
        self.dataset.data.axes[1].unit = 's'

        analysis = self.dataset.analyse(self.analysis)

        self.assertEqual(2, analysis.result.data.data.ndim)
