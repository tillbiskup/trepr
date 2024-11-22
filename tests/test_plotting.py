import unittest

import matplotlib
import numpy as np

import trepr.dataset
import trepr.plotting


class TestSinglePlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.SinglePlotter1D()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"
        self.dataset.data.axes[1].unit = "V"
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue("g-axis" in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertIn(
            "g\\ value", secondary_axes[0].get_xaxis().get_label().get_text()
        )


class TestSinglePlotter2D(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.SinglePlotter2D()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "time"
        self.dataset.data.axes[1].unit = "s"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.data.axes[2].unit = "V"
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue("g-axis" in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertIn(
            "g\\ value", secondary_axes[0].get_xaxis().get_label().get_text()
        )


class TestSinglePlotter2DStacked(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.SinglePlotter2DStacked()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "time"
        self.dataset.data.axes[1].unit = "s"
        self.dataset.data.axes[2].quantity = "intensity"
        self.dataset.data.axes[2].unit = "V"
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue("g-axis" in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertIn(
            "g\\ value", secondary_axes[0].get_xaxis().get_label().get_text()
        )


class TestMultiPlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.MultiPlotter1D()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"
        self.dataset.data.axes[1].unit = "V"
        self.plotter.datasets = [self.dataset]

    def test_has_g_axis_parameter(self):
        self.assertTrue("g-axis" in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertIn(
            "g\\ value", secondary_axes[0].get_xaxis().get_label().get_text()
        )


class TestMultiPlotter1DStacked(unittest.TestCase):

    def setUp(self):
        self.plotter = trepr.plotting.MultiPlotter1DStacked()
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"
        self.dataset.data.axes[1].unit = "V"
        self.plotter.datasets = [self.dataset]

    def test_has_g_axis_parameter(self):
        self.assertTrue("g-axis" in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters["g-axis"] = True
        self.plotter.plot()
        secondary_axes = [
            child
            for child in self.plotter.ax.get_children()
            if isinstance(
                child, matplotlib.axes._secondary_axes.SecondaryAxis
            )
        ]
        self.assertIn(
            "g\\ value", secondary_axes[0].get_xaxis().get_label().get_text()
        )
