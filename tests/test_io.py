import collections
import glob
import os
import shutil
import struct
import tempfile
import unittest

import numpy as np
import aspecd.io

import trepr.io
import trepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = trepr.io.DatasetImporterFactory()

    def test_instantiate_class(self):
        pass

    def test_with_directory_returns_speksim_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'speksim')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.SpeksimImporter)

    def test_with_tez_extension_returns_tez_importer(self):
        source = 'test.tez'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.TezImporter)

    def test_tez_file_without_extension_returns_tez_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'tez', 'pentacene')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.TezImporter)

    def test_with_dat_extension_returns_fsc2_importer(self):
        source = 'test.dat'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.Fsc2Importer)

    def test_fsc2_file_without_extension_returns_fsc2_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'fsc2', 'P10test')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.Fsc2Importer)

    def test_with_adf_extension_returns_adf_importer(self):
        source = 'test.adf'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, aspecd.io.AdfImporter)

    def test_with_dsc_extension_returns_bes3t_importer(self):
        source = 'test.DSC'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.BES3TImporter)

    def test_with_dta_extension_returns_bes3t_importer(self):
        source = 'test.DTA'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.BES3TImporter)

    def test_dsc_file_without_extension_returns_tez_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'BES3T',
                              'pentacen-transient-field-vs-time')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, trepr.io.BES3TImporter)


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

    def test_import_with_no_infofile_continues(self):
        with tempfile.TemporaryDirectory() as testdir:
            new_source = os.path.join(testdir, 'test-wo-infofile')
            shutil.copytree(self.source, new_source)
            os.remove(glob.glob(os.path.join(new_source, '*.info'))[0])
            self.importer.source = new_source
            self.dataset.import_from(self.importer)


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
        self.assertEqual(dict, type(self.importer.xml_dict))

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

    def test_import_assigns_experiment_srt_metadata(self):
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
        self.assertEqual(
            10., self.dataset.metadata.experiment.shot_repetition_rate.value)
        self.assertEqual(
            'Hz', self.dataset.metadata.experiment.shot_repetition_rate.unit)

    def test_import_assigns_recorder_model_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['DEVICES:',
                                       'tds520A ;  // oscilloscope module',
                                       'VARIABLES:',
                                       '',
                                       'Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual('Tektronix TDS520A',
                         self.dataset.metadata.recorder.model)

    def test_import_assigns_magnetic_field_devices_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['DEVICES:',
                                       'bh15_fc;        // magnet module',
                                       'VARIABLES:',
                                       '',
                                       'Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual('Bruker BH15',
                         self.dataset.metadata.magnetic_field.controller)
        self.assertEqual('Bruker BH15',
                         self.dataset.metadata.magnetic_field.power_supply)
        self.assertEqual(
            'Bruker BH15',
            self.dataset.metadata.magnetic_field.field_probe_model)
        self.assertEqual(
            'Hall probe',
            self.dataset.metadata.magnetic_field.field_probe_type)

    def test_import_assigns_aeg_magnetic_field_devices_metadata(self):
        self.prepare_fsc2_file(length=30,
                               header=['DEVICES:',
                                       'er035m_s;        // gaussmeter module',
                                       'aeg_x_band;      // magnet module',
                                       'VARIABLES:',
                                       '',
                                       'Number of runs      = 1',
                                       'Start field         = 2700.00000 G',
                                       'End field           = 4300.00000 G',
                                       'Number of points    = 10',
                                       'Trigger position    = 1',
                                       'Slice length        = 10.0000000 us',
                                       f'Number of points   = 10'])
        self.importer.source = self.datafile
        self.dataset.import_from(self.importer)
        self.assertEqual('home-built',
                         self.dataset.metadata.magnetic_field.controller)
        self.assertEqual('AEG Magnet Power Supply',
                         self.dataset.metadata.magnetic_field.power_supply)
        self.assertEqual(
            'Bruker ER 035 M',
            self.dataset.metadata.magnetic_field.field_probe_model)
        self.assertEqual(
            'NMR Gaussmeter',
            self.dataset.metadata.magnetic_field.field_probe_type)

    def test_extension_does_not_get_added_to_dataset_id(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(self.source, self.dataset.id)


class TestBES3TImporter(unittest.TestCase):
    def setUp(self):
        self.source = os.path.join(ROOTPATH, 'testdata', 'BES3T',
                                   'pentacen-transient-field-vs-time')
        self.importer = trepr.io.BES3TImporter(source=self.source)
        self.dataset = trepr.dataset.ExperimentalDataset()
        self.datafile = 'test.DTA'
        self.descriptionfile = 'test.DSC'

    def tearDown(self):
        for filename in [self.datafile, self.descriptionfile]:
            if os.path.exists(filename):
                os.remove(filename)

    def prepare_dsc_file(self, contents=None):
        """
        Prepare a file that looks like a Bruker BES3T description file.

        ...
        """
        with open(self.descriptionfile, 'w', encoding='utf8') as file:
            for line in contents:
                file.write(line + '\n')

    def test_importer(self):
        self.dataset.import_from(self.importer)

    def test_with_minimal_1D_file(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'DSRC	EXP',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'YTYP	NODATA',
            'ZTYP	NODATA',
            'IRFMT	D',
            'XPTS	4096',
            'XMIN	3400.000000',
            'XWID	100.000000',
            "TITL	'Pentacen transient'",
            "IRNAM	'Intensity'",
            "XNAM	'Field'",
            "IRUNI	''",
            "XUNI	'G'",
            "*",
            "#SPL	1.2 * STANDARD PARAMETER LAYER",
            "OPER    johndoe",
            "DATE    12/02/13",
            "TIME    15:19:50",
            "CMNT    ",
            "SAMP    ",
            "SFOR    ",
            "STAG    C",
            "EXPT    PLS",
            "OXS1    TADC",
            "AXS1    B0VL",
            "AXS2    NONE",
            "AXS3    ",
            "MWPW    0.0006454",
            "A1CT    0.33",
            "B0VL    0.33",
            "A1SW    0.02",
            "MWFQ    9.722e+09",
            "AVGS    1",
            "*",
            "#DSL	1.0 * DEVICE SPECIFIC LAYER",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        with open(self.datafile, 'w+') as file:
            file.write('')
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertEqual('Pentacen transient', self.dataset.label)
        self.assertAlmostEqual(9.722e9,
                               self.dataset.metadata.bridge.mw_frequency.value)
        self.assertAlmostEqual(0.0006454,
                               self.dataset.metadata.bridge.power.value)
        self.assertEqual(1, self.dataset.metadata.recorder.averages)

    def test_data_real_big_double(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'IRFMT	D',
            'XPTS	10',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>d', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual(data, list(self.dataset.data.data))

    def test_data_real_little_double(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	LIT',
            'IKKF	REAL',
            'XTYP	IDX',
            'IRFMT	D',
            'XPTS	10',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('<d', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual(data, list(self.dataset.data.data))

    def test_data_real_big_short(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'IRFMT	S',
            'XPTS	10',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>h', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual(data, list(self.dataset.data.data))

    def test_data_real_big_int(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'IRFMT	I',
            'XPTS	10',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>i', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual(data, list(self.dataset.data.data))

    def test_data_real_big_float(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'IRFMT	F',
            'XPTS	10',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>f', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual(data, list(self.dataset.data.data))

    def test_2d_data_get_reshaped(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'YTYP	IDX',
            'IRFMT	D',
            'XPTS	5',
            'XMIN    3200.000000',
            'XWID    200.000000',
            "XNAM	'Field'",
            "XUNI	'G'",
            'YPTS    2',
            'YMIN	0.000000',
            'YWID	100.000000',
            "YNAM	'Time'",
            "YUNI	'ns'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>d', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertEqual((5, 2), self.dataset.data.data.shape)

    def test_2d_data_with_time_axis_first_get_transposed(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'YTYP	IDX',
            'IRFMT	D',
            'XPTS	5',
            'XMIN	0.000000',
            'XWID	100.000000',
            "XNAM	'Time'",
            "XUNI	'ns'",
            'YPTS    2',
            'YMIN    3200.000000',
            'YWID    200.000000',
            "YNAM	'Field'",
            "YUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>d', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertEqual((2, 5), self.dataset.data.data.shape)

    def test_2d_data_with_time_axis_first_assigns_axes(self):
        dsc_contents = [
            '#DESC	1.2 * DESCRIPTOR INFORMATION ***********************',
            '*',
            'BSEQ	BIG',
            'IKKF	REAL',
            'XTYP	IDX',
            'YTYP	IDX',
            'IRFMT	D',
            'XPTS	5',
            'XMIN	0.000000',
            'XWID	10000.000000',
            "XNAM	'Time'",
            "XUNI	'ns'",
            'YPTS    2',
            'YMIN    3200.000000',
            'YWID    200.000000',
            "YNAM	'Field'",
            "YUNI	'G'",
            "IRNAM	'Intensity'",
            "IRUNI	''",
            "TITL	'Pentacen transient'",
        ]
        self.prepare_dsc_file(contents=dsc_contents)
        data = list(np.arange(10))
        with open(self.datafile, 'wb') as file:
            for value in data:
                file.write(struct.pack('>d', value))
        self.importer.source = self.descriptionfile
        self.dataset.import_from(self.importer)
        self.assertListEqual([320., 340.],
                             list(self.dataset.data.axes[0].values))
        self.assertListEqual([0, 2.5e-6, 5.0e-6, 7.5e-6, 10.0e-6],
                             list(self.dataset.data.axes[1].values))
        self.assertEqual('magnetic field', self.dataset.data.axes[0].quantity)
        self.assertEqual('mT', self.dataset.data.axes[0].unit)
        self.assertEqual('time', self.dataset.data.axes[1].quantity)
        self.assertEqual('s', self.dataset.data.axes[1].unit)
        self.assertEqual('intensity', self.dataset.data.axes[-1].quantity)
        self.assertEqual('', self.dataset.data.axes[-1].unit)
