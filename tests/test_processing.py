import os
import unittest

import aspecd.exceptions
import numpy as np

import trepr.exceptions
import trepr.processing
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestPretriggerOffsetCompensation(unittest.TestCase):
    def setUp(self):
        self.processing = trepr.processing.PretriggerOffsetCompensation()
        source = os.path.join(ROOTPATH, "testdata/speksim/")
        importer = trepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_processing(self):
        self.dataset.process(self.processing)

    def test_zeropoint_index(self):
        self.processing.dataset = self.dataset
        self.processing._get_zeropoint_index()
        self.assertNotEqual(0, self.processing.parameters["zeropoint_index"])


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
        self.assertNotIn("abstract", self.processing.description.lower())
        self.assertIn("background", self.processing.description.lower())

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
        self.processing.parameters["num_profiles"] = [-10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])

    def test_perform_task_with_list_two_elements(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters["num_profiles"] = [10, -10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)

    def test_perform_task_with_list_two_other_elements(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters["num_profiles"] = [5, 10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)

    def test_perform_task_with_list(self):
        self.create_dataset()
        self.dataset.data.data[-10:] += 2
        self.processing.parameters["num_profiles"] = [5, 10]
        self.dataset.process(self.processing)
        self.assertGreater(5.0, self.dataset.data.data[16, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[0, 0])
        self.assertAlmostEqual(0, self.dataset.data.data[-1, 0], 2)


class TestTriggerAutodetection(unittest.TestCase):

    def setUp(self):
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.processing = trepr.processing.TriggerAutodetection()

    @staticmethod
    def create_time_trace():
        x1 = np.linspace(0, 10, 1000)
        x2 = np.linspace(-2, 2, 200)
        y1 = np.exp(-x1)
        y1 = np.insert(y1, 0, np.zeros(100))

        amplitude = 1
        position = 0
        width = 2
        y2 = amplitude * np.exp(-((x2 - position) ** 2) / 2 * width**2)
        convolved = np.convolve(y1, y2)
        return convolved + np.random.random(len(convolved))

    def test_instantiate_class(self):
        pass

    def test_has_appropriate_description(self):
        self.assertIn(
            "autodetect trigger position", self.processing.description.lower()
        )

    def test_with_1D_dataset_without_time_axis_raises(self):
        dataset = trepr.dataset.ExperimentalDataset()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_with_2D_dataset_without_time_axis_raises(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.data.data = np.random.random([5, 5])
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(self.processing)

    def test_with_2D_dataset_with_time_axis(self):
        dataset = trepr.dataset.ExperimentalDataset()
        dataset.data.data = np.random.random([5, 100])
        dataset.data.axes[1].quantity = "time"
        dataset.process(self.processing)

    def test_with_1D_dataset_sets_trigger_position(self):
        self.dataset.data.data = self.create_time_trace()
        self.dataset.data.axes[0].quantity = "time"
        self.dataset.process(self.processing)
        self.assertGreaterEqual(
            self.dataset.metadata.transient.trigger_position, 100
        )

    def test_with_2D_dataset_sets_trigger_position(self):
        self.dataset.data.data = np.tile(self.create_time_trace(), (5, 1))
        self.dataset.data.axes[1].quantity = "time"
        self.dataset.process(self.processing)
        self.assertGreaterEqual(
            self.dataset.metadata.transient.trigger_position, 100
        )

    def test_with_1D_dataset_sets_time_axis(self):
        self.dataset.data.data = self.create_time_trace()
        self.dataset.data.axes[0].quantity = "time"
        self.dataset.process(self.processing)
        self.assertLess(self.dataset.data.axes[0].values[0], 0)

    def test_with_2D_dataset_sets_time_axis(self):
        self.dataset.data.data = np.tile(self.create_time_trace(), (5, 1))
        self.dataset.data.axes[1].quantity = "time"
        self.dataset.process(self.processing)
        self.assertLess(self.dataset.data.axes[1].values[0], 0)
