import os
import unittest

import aspecd.exceptions

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


if __name__ == '__main__':
    unittest.main()
