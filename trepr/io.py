"""
General facilities for input (and output).

With this module trepr raw data in Freiburg Speksim format can be imported.
"""
import collections
import glob
import io
import os
import re
from zipfile import ZipFile

import datetime
import numpy as np

import aspecd.annotation
import aspecd.dataset
import aspecd.io
import aspecd.infofile
import xmltodict as xmltodict

import trepr.dataset


class SpeksimImporter(aspecd.io.DatasetImporter):
    """Import trepr raw data in Freiburg Speksim format including its metadata.

    Trepr raw data consist of several time traces, each of which is stored in a
    text file. In order to analyse the raw data, it is necessary to store the
    time traces all together in one dataset.

    The corresponding metadata are read from an external file in infofile
    format. For further information about the infofile format see:
    https://www.till-biskup.de/en/software/info/format

    Parameters
    ----------
    source : str
        Path to the raw data.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Entity containing data and metadata.

    Raises
    ------
    FileNotFoundError
        Raised if no infofile could be found.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.dataset = trepr.dataset.ExperimentalDataset()
        # protected properties
        self._headerlines = 5
        self._data = np.array([])
        self._file_format = str()
        self._time_stamps = np.array([])
        self._mwfreq = np.array([])
        self._comment_line = str()
        self._time_unit = str()
        self._field_unit = str()
        self._intensity_unit = str()
        self._mwfreq_unit = str()
        self._time_axis = np.array([])
        self._field_axis = np.array([])
        self._infofile = aspecd.infofile.Infofile()
        self._header = list()
        self._format_no = int()
        self._time_start = float()
        self._time_stop = float()
        self._time_points = int()

    def _import(self):
        """Execute all necessary methods and write the data to a dataset."""
        self._import_raw_data()
        self._hand_data_to_dataset()

        self._create_time_axis()
        self._ensure_field_axis_in_SI_unit()
        self._hand_axes_to_dataset()

        self._load_infofile()
        self._map_infofile()

        self._create_time_stamp_data()
        self._create_mw_freq_data()

    def _import_raw_data(self):
        """Import the time traces and cut off the header lines."""
        filenames = self._get_filenames()
        for filename in filenames:
            self._process_timetrace(filename)
        self._data = \
            np.reshape(self._data, [len(filenames), self._time_points])

    def _get_filenames(self):
        filenames = sorted(glob.glob(os.path.join(self.source,
                                                  '*.[0-9][0-9][0-9]')))
        return filenames

    def _process_timetrace(self, filename):
        with open(filename) as file:
            raw_data = file.read()
        lines = raw_data.splitlines()
        self._header = lines[0:self._headerlines]
        self._parse_header()
        numeric_data = self._process_numeric_data(raw_data)
        self._data = np.append(self._data, numeric_data)

    def _process_numeric_data(self, raw_data):
        numeric_data = np.loadtxt(io.StringIO(raw_data),
                                  skiprows=self._headerlines)
        numeric_data = np.reshape(numeric_data, self._time_points)
        return numeric_data

    def _parse_header(self):
        """Execute the methods which parse the header lines."""
        self._parse_header_1st_line()
        self._parse_header_2nd_line()
        self._parse_header_3rd_line()
        self._parse_header_4th_line()
        self._parse_header_5th_line()

    def _parse_header_1st_line(self):
        """Parse the 1st header line and extract the time and date.

        Example::

            Source : transient; Time : Wed Jun 7 08:44:57 2017

        """
        entries = self._header[0].split(';')
        self._file_format = entries[0].split(':')[1].strip()
        time_stamp = entries[1].split(' : ')[1]
        time_stamp = datetime.datetime.strptime(time_stamp,
                                                '%a %b %d %H:%M:%S %Y')
        self._time_stamps = np.append(self._time_stamps, time_stamp)

    def _parse_header_2nd_line(self):
        """Extract the field and frequency unit from the 2nd header line.

        Example::

            B0 = 4080.000000 Gauss, mw = 9.684967 GHz

        """

        def parse_line(line):
            matches = re.search('([A-Za-z0-9]*) = ([0-9.]*) ([A-Za-z]*)', line)
            return float(matches.group(2)), matches.group(3)

        entries = self._header[1].split(',')
        field, self._field_unit = parse_line(entries[0])
        mwfreq, self._mwfreq_unit = parse_line(entries[1])
        self._field_axis = np.append(self._field_axis, field)
        self._mwfreq = np.append(self._mwfreq, mwfreq)

    def _parse_header_3rd_line(self):
        """Parse the 3rd header line.

        Example::

             NDI-T2 sa64 20/2 42/25 523nm/1mJ

        """
        self._comment_line = self._header[2]

    def _parse_header_4th_line(self):
        """Extract format number and time information from 4th header line.

        Example::

            1 5000 -1.001e-06 8.997e-06 0 0

        """
        entries = self._header[3].split()[0:4]
        self._format_no = int(entries[0])
        self._time_points = int(entries[1])
        self._time_start = float(entries[2])
        self._time_stop = float(entries[3])

    def _parse_header_5th_line(self):
        """Extract the time- and intensity-unit from the 5th header line.

        Example::

            s                        V

        """
        self._time_unit, self._intensity_unit = self._header[4].split()

    def _create_time_axis(self):
        """Create the time axis using the start, end, and time points."""
        self._time_axis = \
            np.linspace(self._time_start,
                        self._time_stop,
                        num=self._time_points)

    def _load_infofile(self):
        """Import the infofile and parse it."""
        infofile_name = self._get_infofile_name()
        if not infofile_name:
            raise FileNotFoundError('Infofile not found.')
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _get_infofile_name(self):
        return glob.glob(os.path.join(self.source, '*.info'))

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _assign_comment_as_annotation(self):
        comment = aspecd.annotation.Comment()
        comment.comment = self._infofile.parameters['COMMENT']
        self.dataset.annotate(comment)

    def _map_metadata(self, infofile_version):
        """Bring the metadata into a unified format."""
        mapper = \
            trepr.dataset.MetadataMapper(version=infofile_version,
                                         metadata=self._infofile.parameters)
        mapper.map()
        self.dataset.metadata.from_dict(mapper.metadata)

    def _hand_data_to_dataset(self):
        """Hand the data to the dataset structure."""
        self.dataset.data.data = self._data

    def _ensure_field_axis_in_SI_unit(self):
        """Ensure that the field axis unit is in SI unit."""
        if self._field_unit == 'Gauss':
            self._field_unit = 'mT'
            self._field_axis = self._field_axis / 10

    def _hand_axes_to_dataset(self):
        """Hand the axes and intensity to the dataset structure."""
        self.dataset.data.axes[0].values = self._time_axis
        self.dataset.data.axes[0].unit = self._time_unit
        self.dataset.data.axes[0].quantity = 'time'
        self.dataset.data.axes[1].values = self._field_axis
        self.dataset.data.axes[1].unit = self._field_unit
        self.dataset.data.axes[1].quantity = 'magnetic field'
        self.dataset.data.axes[2].unit = self._intensity_unit
        self.dataset.data.axes[2].quantity = 'intensity'

    def _create_time_stamp_data(self):
        """Hand the time stamp data to the dataset structure."""
        self.dataset.time_stamp.data = self._time_stamps
        self.dataset.time_stamp.axes[0].values = self._field_axis
        self.dataset.time_stamp.axes[0].unit = self._field_unit
        self.dataset.time_stamp.axes[0].quantity = 'magnetic field'
        self.dataset.time_stamp.axes[1].quantity = 'date'

    def _create_mw_freq_data(self):
        """Hand the microwave frequency data to the dataset structure."""
        self.dataset.microwave_frequency.data = self._mwfreq
        self.dataset.microwave_frequency.axes[0].values = self._field_axis
        self.dataset.microwave_frequency.axes[0].unit = self._field_unit
        self.dataset.microwave_frequency.axes[0].quantity = 'magnetic field'
        self.dataset.microwave_frequency.axes[1].unit = self._mwfreq_unit
        self.dataset.microwave_frequency.axes[1].quantity = \
            'microwave frequency'


class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):
    """Create a :obj:`trepr.io.SpeksimImporter` object.

    With regard to the recipe-driven data analysis, it might be helpful not to
    have to think about data formats and the appropriate importer.
    With only one data format, as is currently the case, the
    :class:`trepr.DatasetImporterFactory` class does nothing other than
    initiate a :obj:`trepr.io.SpeksimImporter` object.

    """

    def _get_importer(self, source):
        return SpeksimImporter(source=source)


class TezImporter(aspecd.io.DatasetImporter):

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.xml_dict = None
        self.dataset = trepr.dataset.ExperimentalDataset()

    def _import(self):
        self._get_dir_and_filenames()
        self._unpack_zip()
        self.get_xml_data_as_struct()
        self.get_data_from_binary()
        self.parse_axes()

    def _unpack_zip(self):
        with ZipFile(self.source + '.tez', 'r') as zip_obj:
            zip_obj.extractall(os.path.join(self.root_dir, 'tmp'))

    def get_xml_data_as_struct(self):
        with open(os.path.join(self.root_dir, 'tmp', self.filename,
                               'struct.xml'), 'r') as file:
            xml_data = file.read()
        self.xml_dict = xmltodict.parse(xml_data)

    def _get_dir_and_filenames(self):
        self.root_dir, self.filename = os.path.split(self.source)
        self.raw_data_name = os.path.join(self.root_dir, 'tmp',
                                          self.filename, 'binaryData', 'data')
        self.raw_data_shape_filename = os.path.join(self.raw_data_name + '.dim')

    def parse_axes(self):
        for axis in self.xml_dict['struct']['axes']['data']['values']:
            id_ = int(axis['@id']) - 1
            if '#text' in axis.keys():
                values = [float(i) for i in axis['#text'].split(' ') if i]
                self.dataset.data.axes[id_].values = np.asarray(values)
            if '#text' in self.xml_dict['struct']['axes']['data']['measure'][
                id_].keys():
                self.dataset.data.axes[id_].quantity = self.xml_dict[
                    'struct']['axes']['data']['measure'][id_]['#text']
                self.dataset.data.axes[id_].unit = self.xml_dict[
                    'struct']['axes']['data']['unit'][id_]['#text']

    def get_data_from_binary(self):
        with open(self.raw_data_shape_filename, 'r') as f:
            shape = list([int(x) for x in f.read().split()])
        shape.reverse()  # Shape is given in reverse order?
        raw_data = np.fromfile(self.raw_data_name, dtype='<f8')
        raw_data = np.reshape(raw_data, shape).transpose()
        self.dataset.data.data = raw_data


if __name__ == '__main__':
    import trepr.plotting
    import trepr.processing

    dataset = trepr.dataset.ExperimentalDataset()
    imp = SpeksimImporter(source='/home/till/Documents/Uni/Daten/trepr'
                                 '/Pentacen/20150728/messung01/')
    dataset.import_from(imp)
    poc = trepr.processing.PretriggerOffsetCompensation()
    process1 = dataset.process(poc)
    saver_obj1 = aspecd.plotting.Saver(filename='plotter.pdf')
    plotter_obj1 = trepr.plotting.ScaledImagePlot()
    plotter_obj2 = aspecd.plotting.SinglePlotter2D()
    plot1 = dataset.plot(plotter_obj2)
    plotter_obj2.figure.show()
    plot1.save(saver_obj1)
