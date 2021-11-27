import unittest

import trepr.plotting


class TestMultiPlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.MultiPlotter1D()

    def test_instantiate_class(self):
        pass

    def test_has_switch_axes_parameter(self):
        self.assertTrue('switch_axes' in self.plotter.parameters)

    def test_switch_axes_sets_correct_axes_labels(self):
        # TBD
        pass

    def test_has_tight_parameter(self):
        self.assertTrue('tight' in self.plotter.parameters)

    def test_tight_sets_correct_axes_limits(self):
        # TBD: check with x, y, both and in conjunction with 'switch_axes'
        pass
