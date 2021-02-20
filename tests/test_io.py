import collections
import os
import shutil
import unittest

import aspecd.metadata

import trepr.io
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestTezImporter(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(ROOTPATH, 'testdata', 'pentacene')
        self.importer = trepr.io.TezImporter(source=self.source)
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.tempdir = os.path.join(os.path.split(self.source)[0], 'tmp')

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def test_importer(self):
        self.dataset.import_from(self.importer)

    def test_importer_unpacks_zip(self):
        self.importer._unpack_zip()
        files = os.listdir(self.tempdir)
        self.assertEqual(1, len(files))

    def test_converted_xml_is_dict(self):
        self.importer._unpack_zip()
        self.importer._get_dir_and_filenames()
        self.importer._get_xml_data_as_struct()
        self.assertEqual(collections.OrderedDict, type(self.importer.xml_dict))

    def test_axes_are_created(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(3, len(self.importer.dataset.data.axes))

    def test_data_shape_matches_axes_lengths(self):
        """Crucial test for dimensions!
        0: magnetic field axis
        1: time axis
        """
        self.dataset.import_from(self.importer)
        print(len(self.importer.dataset.data.axes[0].values),
              len(self.importer.dataset.data.axes[1].values))
        self.assertEqual((len(self.importer.dataset.data.axes[0].values),
                          len(self.importer.dataset.data.axes[1].values)),
                         self.importer.dataset.data.data.shape)

    def test_too_many_axes_in_xml_dict_raises(self):
        self.importer._unpack_zip()
        self.importer._get_dir_and_filenames()
        self.importer._get_xml_data_as_struct()
        self.importer.xml_dict['struct']['axes']['data']['measure'].append({
            '@class': 'char',
            '@id': '3',
            '@size': '[0 0]'})
        with self.assertRaises(NotImplementedError):
            self.importer._parse_axes()


    def test_axes_are_filled(self):
        self.dataset.import_from(self.importer)
        self.assertFalse(self.dataset.data.axes[0].values[0] == 0)
        self.assertFalse(self.dataset.data.axes[1].values[0] == 0)

    def test_get_physical_quantity(self):
        test_dict = {
            'field': {
                '@class': 'struct',
                '@id': '1',
                '@size': '[1 1]',
                'value': {
                    '@class': 'double',
                    '@id': '1',
                    '@size': '[0 0]',
                    '#text': '50'},
                'unit': {
                    '@class': 'char',
                    '@id': '1',
                    '@size': '[0 0]',
                    '#text': 'mT'}}
        }
        ret = self.importer._get_physical_quantity(test_dict['field'])
        self.assertEqual(type(ret), dict)


if __name__ == '__main__':
    unittest.main()
