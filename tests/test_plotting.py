import unittest

import numpy as np

import trepr.dataset
import trepr.plotting


class TestMultiPlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.MultiPlotter1D()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
        self.dataset.data.axes[1].unit = 'V'
        self.plotter.datasets = [self.dataset]

    def test_instantiate_class(self):
        pass

    def test_has_switch_axes_parameter(self):
        self.assertTrue('switch_axes' in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        self.plotter.parameters['switch_axes'] = True
        self.plotter.plot()
        self.assertIn('intensity', self.plotter.ax.get_xlabel())
        self.assertIn('magnetic', self.plotter.ax.get_ylabel())

    def test_has_tight_parameter(self):
        self.assertTrue('tight' in self.plotter.parameters)

    def test_tight_sets_correct_x_axes_limits(self):
        self.plotter.parameters['tight'] = 'x'
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_xlim()))

    def test_tight_sets_correct_y_axes_limits(self):
        self.plotter.parameters['tight'] = 'y'
        self.plotter.plot()
        self.assertListEqual([min(self.dataset.data.data),
                              max(self.dataset.data.data)],
                             list(self.plotter.ax.get_ylim()))

    def test_tight_sets_correct_axes_limits_with(self):
        self.plotter.parameters['tight'] = 'both'
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_xlim()))
        self.assertListEqual([min(self.dataset.data.data),
                              max(self.dataset.data.data)],
                             list(self.plotter.ax.get_ylim()))

    def test_tight_sets_correct_x_axes_limits_with_switched_axes(self):
        self.plotter.parameters['switch_axes'] = True
        self.plotter.parameters['tight'] = 'x'
        self.plotter.plot()
        self.assertListEqual([min(self.dataset.data.data),
                              max(self.dataset.data.data)],
                             list(self.plotter.ax.get_xlim()))

    def test_tight_sets_correct_y_axes_limits_with_switched_axes(self):
        self.plotter.parameters['switch_axes'] = True
        self.plotter.parameters['tight'] = 'y'
        self.plotter.plot()
        self.assertListEqual([0, 4], list(self.plotter.ax.get_ylim()))

    def test_tight_sets_correct_axes_limits_with_switched_axes(self):
        self.plotter.parameters['switch_axes'] = True
        self.plotter.parameters['tight'] = 'both'
        self.plotter.plot()
        self.assertListEqual([min(self.dataset.data.data),
                              max(self.dataset.data.data)],
                             list(self.plotter.ax.get_xlim()))
        self.assertListEqual([0, 4], list(self.plotter.ax.get_ylim()))
