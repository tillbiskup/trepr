import collections
import os
import shutil
import unittest

import numpy as np

import trepr.io
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestSpeksimImporter(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(ROOTPATH, 'testdata', 'speksim')
        self.importer = trepr.io.SpeksimImporter(source=self.source)
        self.dataset = trepr.dataset.ExperimentalDataset()

    def test_importer(self):
        self.dataset.import_from(self.importer)

    def test_data_shape_matches_axes_lengths(self):
        """Crucial test for dimensions!
        0: magnetic field axis
        1: time axis
        """
        self.dataset.import_from(self.importer)
        self.assertEqual((len(self.importer.dataset.data.axes[0].values),
                          len(self.importer.dataset.data.axes[1].values)),
                         self.importer.dataset.data.data.shape)

    def test_metadata_is_imported_correctly(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.metadata.measurement.operator)
        self.assertTrue(self.dataset.metadata.spectrometer.software)


class TestTezImporter(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(ROOTPATH, 'testdata', 'tez', 'pentacene')
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
        self.importer._import_xml_data_to_dict()
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
        self.assertEqual((len(self.importer.dataset.data.axes[0].values),
                          len(self.importer.dataset.data.axes[1].values)),
                         self.importer.dataset.data.data.shape)

    def test_too_many_axes_in_xml_dict_raises(self):
        self.importer._unpack_zip()
        self.importer._get_dir_and_filenames()
        self.importer._import_xml_data_to_dict()
        self.importer.xml_dict['struct']['axes']['data']['measure'].append({
            '@class': 'char',
            '@id': '4',
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

    def test_import_infofile_is_true(self):
        self.assertTrue(self.importer.load_infofile)

    def test_infofile_exists_is_true(self):
        self.assertTrue(self.importer._infofile_exists())

    def test_infofile_is_loaded(self):
        self.importer._load_infofile()
        self.assertTrue(
            self.importer._infofile.parameters['GENERAL']['Operator'])

    def test_map_infofile_into_dataset(self):
        self.dataset.import_from(self.importer)
        self.importer._load_infofile()
        self.importer._map_infofile()
        self.assertTrue(self.importer._infofile.infofile_info['version'])

    def test_infofile_is_imported(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.metadata.measurement.operator)
        self.assertEqual(20, self.dataset.metadata.pump.repetition_rate.value)
        self.assertEqual(0.6324555320336759,
                         self.dataset.metadata.bridge.power.value)


class TestFsc2Importer(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(ROOTPATH, 'testdata', 'fsc2', 'P10test')
        self.importer = trepr.io.Fsc2Importer(source=self.source)
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.datafile = 'test.dat'

    def tearDown(self):
        if os.path.exists(self.datafile):
            os.remove(self.datafile)

    def prepare_fsc2_file(self, length=5, header=None):
        """
        Prepare a file that looks like an fsc2 file.

        fsc2 files start with a header marked by "% " and otherwise contain
        the data as single column.
        """
        header = header or []
        header_lines = ['', '#!/usr/local/bin/fsc2', '']
        header_lines.extend(header)
        data = np.random.random(length)
        np.savetxt(self.datafile, data, fmt='%.12f', comments='% ',
                   header='\n'.join(header_lines))

    def test_importer(self):
        self.dataset.import_from(self.importer)

    def test_with_minimal_fsc2_file(self):
        self.prepare_fsc2_file(length=20,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual((2, 10), self.dataset.data.data.shape)

    def test_with_minimal_fsc2_file_and_comment(self):
        comment = 'And here some sample description'
        self.prepare_fsc2_file(length=20,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10',
                                       '',
                                       f'{comment}',
                                       ''])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(comment,
                         self.dataset.annotations[0].annotation.content)

    def test_with_minimal_fsc2_file_sets_field_axis(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(270, self.dataset.data.axes[0].values[0])
        self.assertEqual(430, self.dataset.data.axes[0].values[-1])
        self.assertEqual(3, len(self.dataset.data.axes[0].values))
        self.assertEqual('magnetic field', self.dataset.data.axes[0].quantity)
        self.assertEqual('mT', self.dataset.data.axes[0].unit)

    def test_with_minimal_fsc2_file_sets_time_axis(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(-1e-6, self.dataset.data.axes[1].values[0])
        self.assertAlmostEqual(9e-6, self.dataset.data.axes[1].values[-1], 18)
        self.assertEqual(10, len(self.dataset.data.axes[1].values))
        self.assertEqual('time', self.dataset.data.axes[1].quantity)
        self.assertEqual('s', self.dataset.data.axes[1].unit)

    def test_with_minimal_fsc2_file_sets_intensity_axis(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual('intensity', self.dataset.data.axes[2].quantity)
        self.assertEqual('V', self.dataset.data.axes[2].unit)

    def test_with_minimal_fsc2_file_assigns_transient_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(10, self.dataset.metadata.transient.points)
        self.assertEqual(1, self.dataset.metadata.transient.trigger_position)
        self.assertAlmostEqual(
            1e-5, self.dataset.metadata.transient.length.value, 18)
        self.assertEqual('s', self.dataset.metadata.transient.length.unit)

    def test_with_minimal_fsc2_file_assigns_number_of_runs(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(1, self.dataset.metadata.experiment.runs)

    def test_import_assigns_recorder_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Sensitivity    = 50.0000000 mV/div',
                                       'Number of averages  = 5',
                                       'Time base      = 1.00000000 us/div',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(50, self.dataset.metadata.recorder.sensitivity.value)
        self.assertEqual('mV', self.dataset.metadata.recorder.sensitivity.unit)
        self.assertEqual(1, self.dataset.metadata.recorder.time_base.value)
        self.assertEqual('us', self.dataset.metadata.recorder.time_base.unit)
        self.assertEqual(5, self.dataset.metadata.recorder.averages)
        self.assertEqual(1e-6, self.dataset.metadata.recorder.pretrigger.value)
        self.assertEqual('s', self.dataset.metadata.recorder.pretrigger.unit)

    def test_import_assigns_bridge_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'MW frequency        = 9.75000000 GHz',
                                       'Attenuation         = 20.0000000 dB',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(9.75, self.dataset.metadata.bridge.mw_frequency.value)
        self.assertEqual('GHz', self.dataset.metadata.bridge.mw_frequency.unit)
        self.assertEqual(20, self.dataset.metadata.bridge.attenuation.value)
        self.assertEqual('dB', self.dataset.metadata.bridge.attenuation.unit)

    def test_import_assigns_temperature_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Temperature         = 299.000000 K',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(
            299., self.dataset.metadata.temperature_control.temperature.value)
        self.assertEqual(
            'K', self.dataset.metadata.temperature_control.temperature.unit)

    def test_import_assigns_pump_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'MW frequency        = 9.75000000 GHz',
                                       'Laser wavelength = 430.000000 nm ('
                                       '10.0000000 Hz)',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual(430., self.dataset.metadata.pump.wavelength.value)
        self.assertEqual('nm', self.dataset.metadata.pump.wavelength.unit)
        self.assertEqual(10., self.dataset.metadata.pump.repetition_rate.value)
        self.assertEqual('Hz', self.dataset.metadata.pump.repetition_rate.unit)
