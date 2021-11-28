"""
General facilities for input (and output).

In order to work with TREPR data, these data need to be imported into the
trepr package. Therefore, the module provides importers for specific file
formats. In case of TREPR spectroscopy, the measurement control software is
often lab-written and specific for a local setup. One exception is the
Bruker BES3T file format written by Bruker Xepr and Xenon software that can
be used to record TREPR data in combination with a pulsed EPR spectrometer.

Another class implemented in this module is the
:class:`trepr.io.DatasetImporterFactory`, a prerequisite for recipe-driven
data analysis. This factory returns the correct dataset importer for a
specific dataset depending on the information provided (usually, a filename).


Importers for specific file formats
===================================

Currently, the following importers for specific file formats are available:

* :class:`SpeksimImporter`

  The Speksim format was developed in Freiburg in the group of Prof. G.
  Kothe and used afterwards in the group of Prof. S. Weber. The spectrometer
  control software was developed by Prof. U. Heinen.

  One speciality of this file format is that each transient is stored in an
  individual file. For each of these transients, a timestamp as well as the
  microwave frequency are recorded as well, allowing to analyse frequency
  drifts and irregularities in the data acquisition.

* :class:`TezImporter`

  The tez file format is the internal format used by the MATLAB(r) trepr
  toolbox developed by T. Biskup. It vaguely resembles the OpenDocument
  format used, *e.g.*, by OpenOffice and LibreOffice. In short, the metadata
  are contained in an XML file, while the numerical data are stored as IEEE
  754 standard binaries in separate files. The ASpecD dataset format (adf)
  is similar in some respect.

  tez files usually carry ".tez" as file extension.

* :class:`Fsc2Importer`

  The fsc2 file format originates from the fsc2 spectrometer control
  software developed by J. T. Törring at the FU Berlin and used in a number of
  labs. For details of the software, `see the fsc2 homepage
  <https://users.physik.fu-berlin.de/~jtt/fsc2.phtml>`_. As the actual
  experiments are defined in the "Experiment Description Language" (EDL),
  the importer necessarily makes a number of assumptions that work with
  the particular set of data recorded at a given time at FU Berlin.

  fsc2 files usually carry ".dat" as file extension, although they are bare
  text files.


Implementing importers for additional file formats is rather
straight-forward. For details, see the documentation of the :mod:`aspecd.io`
module.


Module documentation
====================

"""
import collections
import datetime
import glob
import io
import os
import re
import shutil
from zipfile import ZipFile

import numpy as np
import xmltodict

import aspecd.annotation
import aspecd.io
import aspecd.infofile
import aspecd.metadata
import aspecd.plotting
import aspecd.utils


class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):
    """Factory for creating importer objects based on the source provided.

    Often, data are available in different formats, and deciding which
    importer is appropriate for a given format can be quite involved. To
    free other classes from having to contain the relevant code, a factory
    can be used.

    Currently, the sole information provided to decide about the appropriate
    importer is the source (a string). A concrete importer object is
    returned by the method ``get_importer()``. If no source is provided,
    an exception will be raised.

    If the source string does not match any of the importers handled by this
    module, the standard importers from the ASpecD framework are checked.
    See the documentation of the :class:`aspecd.io.DatasetImporterFactory`
    base class for details.

    Attributes
    ----------
    supported_formats : :class:`dict`
        Dictionary who's keys correspond to the base name of the respective
        importer (*i.e.*, without the suffix "Importer") and who's values are a
        list of file extensions to detect the correct importer.

    data_format : :class:`str`
        Name of the format that has been detected.

    """

    def __init__(self):
        super().__init__()
        self.supported_formats = {"Speksim": "",
                                  "Tez": ".tez",
                                  "Fsc2": ".dat"}
        self.data_format = None

    def _get_importer(self):
        if os.path.isdir(self.source):
            return SpeksimImporter(source=self.source)
        self._find_format()
        importer = None
        if self.data_format:
            importer = aspecd.utils.object_from_class_name(
                ".".join(["trepr", "io", self.data_format + "Importer"]))
            importer.source = self.source
        return importer

    def _find_format(self):
        _, extension = os.path.splitext(self.source)
        if extension:
            if extension in self.supported_formats.values():
                self.data_format = self._format_from_extension(extension)
        else:
            for extension in [extension for extension in
                              self.supported_formats.values() if extension]:
                if os.path.isfile(self.source + extension):
                    self.data_format = self._format_from_extension(extension)

    def _format_from_extension(self, extension):
        return list(self.supported_formats.keys())[list(
            self.supported_formats.values()).index(extension)]


class SpeksimImporter(aspecd.io.DatasetImporter):
    """Importer for data in Freiburg Speksim format including its metadata.

    Datasets in this format consist of several time traces, each of which is
    stored in a text file. In order to analyse the raw data, it is necessary
    to store the time traces all together in one dataset.

    The corresponding metadata are read from an external file in infofile
    format. For further information about the infofile format see:
    `<https://www.till-biskup.de/en/software/info/format>`_.

    Parameters
    ----------
    source : :class:`str`
        Path to the raw data.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.ExperimentalDataset`
        Entity containing data and metadata.

    Raises
    ------
    FileNotFoundError
        Raised if no infofile could be found.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.dataset = None
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
        # noinspection PyTypeChecker
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
        # noinspection PyTypeChecker
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
        mapper = aspecd.metadata.MetadataMapper()
        mapper.version = infofile_version
        mapper.metadata = self._infofile.parameters
        mapper.recipe_filename = 'trepr@metadata_mapper.yaml'
        mapper.map()
        self.dataset.metadata.from_dict(mapper.metadata)

    def _hand_data_to_dataset(self):
        """Hand the data to the dataset structure."""
        self.dataset.data.data = self._data

    # noinspection PyPep8Naming
    def _ensure_field_axis_in_SI_unit(self):  # noqa: N802
        """Ensure that the field axis unit is in SI unit."""
        if self._field_unit == 'Gauss':
            self._field_unit = 'mT'
            self._field_axis = self._field_axis / 10

    def _hand_axes_to_dataset(self):
        """Hand the axes and intensity to the dataset structure."""
        self.dataset.data.axes[0].values = self._field_axis
        self.dataset.data.axes[0].unit = self._field_unit
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[1].values = self._time_axis
        self.dataset.data.axes[1].unit = self._time_unit
        self.dataset.data.axes[1].quantity = 'time'
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


class TezImporter(aspecd.io.DatasetImporter):
    """Importer for MATLAB(r) trepr toolbox format.

    The MATLAB(r) trepr toolbox format is basically a ZIP archive consisting
    of a list of standard IEEE 754 binary files containing the data and an
    XML file containing the accompanying metadata in structured form,
    enriched with information necessary to directly convert them back into
    MATLAB structures (corresponding to a Python :class:`dict`).

    Parameters
    ----------
    source : :class:`str`
        Path to the raw data.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.ExperimentalDataset`
        Entity containing data and metadata.

    """

    def __init__(self, source=''):
        # Dirty fix: Cut file extension
        if source.endswith(".tez"):
            source = source[:-4]
        super().__init__(source=source)
        # public properties
        self.tez_mapper_filename = 'trepr@tez_mapper.yaml'
        self.xml_dict = None
        self.dataset = None
        self.metadata_filename = ''
        self.load_infofile = True
        # private properties
        self._metadata = None
        self._infofile = aspecd.infofile.Infofile()
        self._root_dir = ''
        self._filename = ''
        self._tmpdir = ''
        self._raw_data_name = ''
        self._raw_data_shape_filename = ''

    def _import(self):
        self._unpack_zip()
        self._get_dir_and_filenames()
        self._import_xml_data_to_dict()
        self._get_data_from_binary()
        self._parse_axes()

        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()

        self._get_metadata_from_xml()
        self._get_mw_frequencies()

        self._remove_tmp_directory()

    def _unpack_zip(self):
        self._root_dir, self._filename = os.path.split(self.source)
        self._tmpdir = os.path.join(self._root_dir, 'tmp')
        with ZipFile(self.source + '.tez', 'r') as zip_obj:
            zip_obj.extractall(self._tmpdir)

    def _get_dir_and_filenames(self):
        hidden_filename = os.listdir(os.path.join(self._root_dir, 'tmp'))[0]
        self.metadata_filename = os.path.join(self._root_dir, 'tmp',
                                              hidden_filename, 'struct.xml')
        self._raw_data_name = \
            os.path.join(self._root_dir, 'tmp', hidden_filename,
                         'binaryData', 'data')
        self._raw_data_shape_filename = os.path.join(self._raw_data_name +
                                                     '.dim')

    def _import_xml_data_to_dict(self):
        with open(self.metadata_filename, 'r') as file:
            xml_data = file.read()
        self.xml_dict = xmltodict.parse(xml_data)

    def _get_data_from_binary(self):
        with open(self._raw_data_shape_filename, 'r') as f:
            shape = list([int(x) for x in f.read().split()])
        shape.reverse()  # Shape is given in reverse order in .dim file
        raw_data = np.fromfile(self._raw_data_name, dtype='<f8')
        raw_data = np.reshape(raw_data, shape).transpose()
        self.dataset.data.data = raw_data

    def _parse_axes(self):
        if len(self.xml_dict['struct']['axes']['data']['measure']) > 3:
            raise NotImplementedError('No method to import more than 3 axes. '
                                      'This task is left to you.')
        for axis in self.xml_dict['struct']['axes']['data']['measure']:
            self._get_magnetic_field_axis(axis)
            self._get_time_axis(axis)

    def _get_magnetic_field_axis(self, axis):
        if '#text' in axis.keys() and axis['#text'] == 'magnetic field':
            id_ = int(axis['@id']) - 1
            self.dataset.data.axes[0].quantity = 'magnetic field'
            self.dataset.data.axes[0].values = \
                self._get_values_from_xml_dict(id_=id_)
            assert int(self.xml_dict['struct']['axes']['data']['values'][
                id_]['@id']) == (id_ + 1), 'Axis-IDs do not match!'
            self.dataset.data.axes[0].unit = self.xml_dict['struct']['axes'][
                'data']['unit'][id_]['#text']

    def _get_time_axis(self, axis):
        if '#text' in axis.keys() and axis['#text'] == 'time':
            id_ = int(axis['@id']) - 1
            self.dataset.data.axes[1].quantity = 'time'
            self.dataset.data.axes[1].values = \
                self._get_values_from_xml_dict(id_=id_)
            assert int(self.xml_dict['struct']['axes']['data']['values'][
                id_]['@id']) == (id_ + 1)
            self.dataset.data.axes[1].unit = self.xml_dict['struct']['axes'][
                'data']['unit'][id_]['#text']

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
                self._get_infofile_name()[0]):
            return True
        print('No infofile found for dataset %s, import continued without '
              'infofile.' % os.path.split(self.source)[1])
        return False

    def _get_infofile_name(self):
        return glob.glob(''.join([self.source.strip(), '.info']))

    def _load_infofile(self):
        """Import infofile and parse it."""
        infofile_name = self._get_infofile_name()
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _map_metadata(self, infofile_version):
        """Bring the metadata into a unified format."""
        mapper = aspecd.metadata.MetadataMapper()
        mapper.version = infofile_version
        mapper.metadata = self._infofile.parameters
        mapper.recipe_filename = 'trepr@metadata_mapper.yaml'
        mapper.map()
        self._metadata = \
            aspecd.utils.convert_keys_to_variable_names(mapper.metadata)

    def _assign_comment_as_annotation(self):
        comment = aspecd.annotation.Comment()
        comment.comment = self._infofile.parameters['COMMENT']
        self.dataset.annotate(comment)

    def _get_values_from_xml_dict(self, id_=None):
        values = np.asarray([float(i) for i in
                             self.xml_dict['struct']['axes']['data'][
                                 'values'][id_]['#text'].split(' ') if i])
        return values

    def _get_metadata_from_xml(self):
        mapping = aspecd.utils.Yaml()
        mapping.read_stream(
            aspecd.utils.get_package_data(self.tez_mapper_filename).encode())
        metadata_dict = collections.OrderedDict()
        for key, subdict in mapping.dict.items():
            metadata_dict[key] = collections.OrderedDict()
            for key2, value in subdict.items():
                metadata_dict[key][key2] = \
                    self._cascade(self.xml_dict['struct'], value)

        self._metadata = self._fuse_with_existing_metadata(metadata_dict)
        self.dataset.metadata.from_dict(self._metadata)
        # Cause Copycat in UdS measurement program:
        self.dataset.metadata.bridge.attenuation.unit = 'dB'

    def _fuse_with_existing_metadata(self, metadata_dict):
        metadata_dict = \
            aspecd.utils.remove_empty_values_from_dict(metadata_dict)
        infofile_metadata = \
            aspecd.utils.copy_values_between_dicts(target=self._metadata,
                                                   source=metadata_dict)
        return infofile_metadata

    def _cascade(self, dict_, value):
        keys = value.split('.')
        return_value = dict_
        for key in keys:
            return_value = return_value[key]
        if self._get_physical_quantity(return_value):
            return_value = self._get_physical_quantity(return_value)
        elif self._get_value(return_value):
            return_value = self._get_value(return_value)
        else:
            return_value = ''
        return return_value

    @staticmethod
    def _get_value(dict_):
        return_value = None
        if '#text' in dict_.keys():
            return_value = dict_['#text']
        return return_value

    @staticmethod
    def _get_physical_quantity(dict_):
        return_value = None
        if 'value' and 'unit' in dict_.keys():
            if '#text' in dict_['value'].keys():
                return_value = {
                    'value': float(dict_['value']['#text']),
                    'unit': dict_['unit']['#text']
                }
        return return_value

    def _get_mw_frequencies(self):
        """Get the dataset with real frequencies of each magnetic field point.

        This is special for the trepr dataset but useful to track frequency
        drifts. In th UdS-measurement program, the frequency is automaticly
        written in the tez structure.
        """
        if self._xml_contains_mw_frequencies():
            self.dataset.microwave_frequency.data = \
                np.asarray([float(i) for i in self.xml_dict['struct'][
                    'parameters']['bridge']['MWfrequency']['values'][
                    '#text'].split(' ') if i])
            self.dataset.microwave_frequency.axes[0] = \
                self.dataset.data.axes[0]
            self.dataset.microwave_frequency.axes[1].unit = \
                self.dataset.metadata.bridge.mw_frequency.unit
            self.dataset.microwave_frequency.axes[1].quantity = \
                'microwave frequency'

    def _xml_contains_mw_frequencies(self):
        answer = False
        if '#text' in self.xml_dict['struct']['parameters']['bridge'][
                'MWfrequency']['values']:
            answer = True
        return answer

    def _remove_tmp_directory(self):
        if os.path.exists(self._tmpdir):
            shutil.rmtree(self._tmpdir)


class Fsc2Importer(aspecd.io.DatasetImporter):
    """
    Importer for data in Berlin fsc2 format.

    These data have been recorded using the flexible fsc2 spectrometer
    control software written by J. T. Törring, allowing to define user-specific
    experiments. For details, `see the fsc2 homepage
    <https://users.physik.fu-berlin.de/~jtt/fsc2.phtml>`_. As the actual
    experiments are defined in the "Experiment Description Language" (EDL),
    the importer necessarily makes a number of assumptions that work with
    the particular set of data recorded at a given time at FU Berlin.

    Key aspects of the data format are:

    * The data files are bare text files (ASCII)

    * The entire EDL program defining the experiment is contained in a header

    * The header usually starts with ``%``

    * The data are stored as ASCII numbers in one (very) long column.

    * At the bottom of the header is a series of key-value pairs with
      crucial metadata necessary to reshape the data and assign the axes.

    The following strategy has been applied to reading the data:

    * Read the header first, separately storing the key-value pairs at the end.

    * Read the data using :func:`numpy.loadtxt`.

    * Reshape the data according to the parameters read from the header.

    Only those parameters that can definitely be obtained from the header
    are stored within the metadata of the dataset. Note that using this
    format by the authors predates the development of the info file format,
    hence many parameters can only implicitly be guessed, as most of the
    time no corresponding record of metadata exists.

    .. note::

        While it may seem strange to store the data as one long column,
        this is actually a very robust way of storing data, as each
        individual trace gets written to the file immediately after
        obtaining the data from the transient recorder. Thus, even if
        something crashed during a measurement (blackout, ...), all data up
        to this event are usually retained.


    .. versionadded:: 0.2

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        self._header = []
        self._parameters = dict()
        self._comment = []
        self._devices = []
        self._device_list = {
            'tds520A': 'Tektronix TDS520A',
            'bh15_fc': 'Bruker BH15',
            'aeg_x_band': 'AEG Magnet Power Supply',
            'er035m_s': 'Bruker ER 035 M',
        }
        self._orig_source = ''

    def _import(self):
        if not os.path.splitext(self.source)[1]:
            self._orig_source = self.source
            self.source += '.dat'

        self._read_header()
        self._load_and_assign_data()

        self._assign_field_axis()
        self._assign_time_axis()
        self._assign_intensity_axis()

        # Metadata can only be assigned after the axes
        self._assign_metadata()
        self._assign_comment()

        self.source = self._orig_source or self.source

    # pylint: disable=too-many-nested-blocks
    def _read_header(self):
        """
        fsc2 files start with a header containing the entire program.

        The header is usually marked with ``%``, and at the end, after the
        program, a series of key-value pairs are printed that are crucial to
        reshape the data and assign the axes.

        The list of parameters got extended over time, and the very end of
        the header consists of comments the user can enter immediately
        before starting the experiment.
        """
        in_header = True
        parameter_line = False
        with open(self.source, 'r', encoding="utf8") as file:
            while in_header:
                line = file.readline()
                if line.startswith('%'):
                    line = line.replace('%', '', 1).strip()
                    self._header.append(line)
                    if line.startswith('Number of runs'):
                        parameter_line = True
                    if parameter_line:
                        if ' = ' in line:
                            key, value = line.split(' = ')
                            try:
                                if '.' in value:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass
                            self._parameters[key.strip()] = value
                        elif line:
                            self._comment.append(line)
                else:
                    in_header = False
        self._get_list_of_active_devices()

    def _load_and_assign_data(self):
        data = np.loadtxt(self.source, comments="% ")
        self.dataset.data.data = \
            data.reshape([-1, self._parameters['Number of points']])

    def _assign_field_axis(self):
        field_start = float(self._parameters['Start field'].split(' ')[0]) / 10
        field_end = float(self._parameters['End field'].split(' ')[0]) / 10
        self.dataset.data.axes[0].values = \
            np.linspace(field_start, field_end, self.dataset.data.data.shape[0])
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'

    def _assign_time_axis(self):
        trigger_position = self._parameters['Trigger position']
        number_of_points = self.dataset.data.data.shape[1]
        relative_trigger_position = trigger_position / number_of_points
        slice_length = \
            float(self._parameters['Slice length'].split(' ')[0]) * 1e-6
        self.dataset.data.axes[1].values = np.linspace(
            -slice_length * relative_trigger_position,
            slice_length - (slice_length * relative_trigger_position),
            number_of_points
        )
        self.dataset.data.axes[1].quantity = 'time'
        self.dataset.data.axes[1].unit = 's'

    def _assign_intensity_axis(self):
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.data.axes[2].unit = 'V'

    def _assign_metadata(self):
        """
        Assign as many metadata as sensibly possible.

        Admittedly, this is currently pretty much hand-coding. For sure,
        there are more elegant ways to do it.
        """
        self._assign_transient_metadata()
        self._assign_recorder_metadata()
        self._assign_bridge_metadata()
        self._assign_temperature_control_metadata()
        self._assign_pump_metadata()
        self._assign_magnetic_field_metadata()
        # Needs to be done after assigning pump metadata
        self._assign_experiment_metadata()

    def _assign_transient_metadata(self):
        self.dataset.metadata.transient.points = \
            self._parameters['Number of points']
        self.dataset.metadata.transient.trigger_position = \
            self._parameters['Trigger position']
        value, _ = self._parameters['Slice length'].split()
        self.dataset.metadata.transient.length.value = float(value) * 1e-6
        self.dataset.metadata.transient.length.unit = 's'

    def _assign_recorder_metadata(self):
        if 'Sensitivity' in self._parameters:
            self._assign_value_unit('Sensitivity',
                                    self.dataset.metadata.recorder.sensitivity)
        if 'Time base' in self._parameters:
            self._assign_value_unit('Time base',
                                    self.dataset.metadata.recorder.time_base)
        if 'Number of averages' in self._parameters:
            self.dataset.metadata.recorder.averages = \
                self._parameters['Number of averages']
        self.dataset.metadata.recorder.pretrigger.value = \
            np.abs(self.dataset.data.axes[1].values[0])
        self.dataset.metadata.recorder.pretrigger.unit = \
            self.dataset.data.axes[1].unit
        if 'tds520A' in self._devices:
            self.dataset.metadata.recorder.model = self._device_list['tds520A']

    def _assign_bridge_metadata(self):
        if 'MW frequency' in self._parameters:
            self._assign_value_unit('MW frequency',
                                    self.dataset.metadata.bridge.mw_frequency)
        if 'Attenuation' in self._parameters:
            self._assign_value_unit('Attenuation',
                                    self.dataset.metadata.bridge.attenuation)

    def _assign_temperature_control_metadata(self):
        if 'Temperature' in self._parameters:
            self._assign_value_unit(
                'Temperature',
                self.dataset.metadata.temperature_control.temperature)

    def _assign_pump_metadata(self):
        if 'Laser wavelength' in self._parameters:
            wavelength, repetition_rate = \
                self._parameters['Laser wavelength'].split(' (')
            value, unit = wavelength.split()
            self.dataset.metadata.pump.wavelength.value = float(value)
            self.dataset.metadata.pump.wavelength.unit = unit
            value, unit = repetition_rate.split()
            self.dataset.metadata.pump.repetition_rate.value = float(value)
            self.dataset.metadata.pump.repetition_rate.unit = \
                unit.replace(')', '')

    def _assign_magnetic_field_metadata(self):
        if 'bh15_fc' in self._devices:
            self.dataset.metadata.magnetic_field.controller = \
                self._device_list['bh15_fc']
            self.dataset.metadata.magnetic_field.power_supply = \
                self._device_list['bh15_fc']
            self.dataset.metadata.magnetic_field.field_probe_model = \
                self._device_list['bh15_fc']
            self.dataset.metadata.magnetic_field.field_probe_type = 'Hall probe'
        if 'aeg_x_band' in self._devices:
            self.dataset.metadata.magnetic_field.controller = 'home-built'
            self.dataset.metadata.magnetic_field.power_supply = \
                self._device_list['aeg_x_band']
        if 'er035m_s' in self._devices:
            self.dataset.metadata.magnetic_field.field_probe_model = \
                self._device_list['er035m_s']
            self.dataset.metadata.magnetic_field.field_probe_type = \
                'NMR Gaussmeter'

    def _assign_experiment_metadata(self):
        self.dataset.metadata.experiment.runs = \
            self._parameters['Number of runs']
        self.dataset.metadata.experiment.shot_repetition_rate = \
            self.dataset.metadata.pump.repetition_rate

    def _assign_comment(self):
        if self._comment:
            comment = aspecd.annotation.Comment()
            comment.content = ' '.join(self._comment)
            self.dataset.annotate(comment)

    def _assign_value_unit(self, parameter='', metadata=None):
        value, unit = self._parameters[parameter].split()
        metadata.value = float(value)
        metadata.unit = unit.split('/')[0]

    def _get_list_of_active_devices(self):
        in_devices = False
        for line in self._header:
            if 'DEVICES:' in line:
                in_devices = True
                continue
            if 'VARIABLES:' in line:
                break
            if in_devices and line and not line.startswith('//'):
                device = line.split()[0].replace(';', '').strip()
                self._devices.append(device)
