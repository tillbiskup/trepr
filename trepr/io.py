"""
General facilities for input and output.

With this module either a trepr raw data or a YAML file can be imported.
"""
import matplotlib.pyplot as plt
import collections
import glob
import io
import os
import re

from datetime import datetime
import numpy as np
import oyaml

import aspecd.annotation
import aspecd.dataset
import aspecd.io
import aspecd.infofile
from trepr import dataset


class SpeksimImporter(aspecd.io.DatasetImporter):
    """Import trepr raw data in Freiburg Speksim format including its metadata.

    Trepr raw data consist of several time traces, each of which is stored in a
    text file. In order to analyze the raw data, it is necessary to store the
    time traces all together in one dataset.

    Parameters
    ----------
    source : str
        Path to the dataset.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Object of the dataset class.

    Raises
    ------
    FileNotFoundError
        Raised if no infofile could be found.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.dataset = dataset.Dataset()
        # protected properties
        self._HEADERLINES = 5
        self._data = np.array([])
        self._file_format = ''
        self._time_stamps = np.array([])
        self._freq = np.array([])
        self._comment_line = ''
        self._time_unit = ''
        self._field_unit = ''
        self._intensity_unit = ''
        self._frequency_unit = ''
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
        self._create_time_axis()
        self._load_infofile()
        self._map_infofile()
        self._hand_data_to_dataset()
        self._hand_axes_to_dataset()
        self._create_time_stamp_data()
        self._create_mw_freq_data()

    def _import_raw_data(self):
        """Import the time traces and cut off the header lines."""
        filenames = sorted(glob.glob(os.path.join(self.source,
                                                  '*.[0-9][0-9][0-9]')))
        for filename in filenames:
            with open(filename) as file:
                raw_data = file.read()
            lines = raw_data.splitlines()
            self._header = lines[0:self._HEADERLINES]
            self._parse_header()
            numeric_data = np.loadtxt(io.StringIO(raw_data),
                                      skiprows=self._HEADERLINES)
            numeric_data = np.reshape(numeric_data, self._time_points)
            self._data = np.append(self._data, numeric_data)
        self._data = \
            np.reshape(self._data, [len(filenames), self._time_points])

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
        time_stamp = datetime.strptime(time_stamp, '%a %b %d %H:%M:%S %Y')
        self._time_stamps = np.append(self._time_stamps, time_stamp)

    def _parse_header_2nd_line(self):
        """Extract the field and frequency unit from the 2nd header line.

        Example::

            B0 = 4080.000000 Gauss, mw = 9.684967 GHz

        """
        def parse_line(line):
            obj = re.search('([A-Za-z0-9]*) = ([0-9.]*) ([A-Za-z]*)', line)
            return float(obj.group(2)), obj.group(3)
        entries = self._header[1].split(',')
        field, self._field_unit = parse_line(entries[0])
        freq, self._frequency_unit = parse_line(entries[1])
        self._field_axis = np.append(self._field_axis, field)
        self._freq = np.append(self._freq, freq)

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
        infofile_name = glob.glob(os.path.join(self.source, '*.info'))
        if not infofile_name:
            raise FileNotFoundError('Infofile not found.')
        self._infofile = aspecd.infofile.Infofile(infofile_name[0])
        self._infofile.parse()

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        mapper = dataset.MetadataMapper(version=infofile_version,
                                        metadata=self._infofile.parameters)
        mapper.map()
        self.dataset.metadata.from_dict(mapper.metadata)
        comment = aspecd.annotation.Comment()
        comment.comment = self._infofile.parameters['COMMENT']
        self.dataset.annotate(comment)

    def _hand_data_to_dataset(self):
        """Hand the data to the dataset structure."""
        self.dataset.data.data = self._data

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
        self.dataset.time_stamp.data = self._time_stamps
        self.dataset.time_stamp.axes[0].values = self._field_axis
        self.dataset.time_stamp.axes[0].unit = self._field_unit
        self.dataset.time_stamp.axes[0].quantity = 'magnetic field'
        self.dataset.time_stamp.axes[1].quantity = 'date'

    def _create_mw_freq_data(self):
        self.dataset.microwave_frequency.data = self._freq
        self.dataset.microwave_frequency.axes[0].values = self._field_axis
        self.dataset.microwave_frequency.axes[0].unit = self._field_unit
        self.dataset.microwave_frequency.axes[0].quantity = 'magnetic field'
        self.dataset.microwave_frequency.axes[1].unit = self._frequency_unit
        self.dataset.microwave_frequency.axes[1].quantity = \
            'microwave frequency'


class YamlLoader:
    """Load YAML files and write the information to a dictionary.

    YAML files are a good way to generate files that are both human and machine
    readable.

    Parameters
    ----------
    filename : str
        Name of the YAML file to load.

    Attributes
    ----------
    yaml_as_dict : dict
        Contents of YAML file.

    """

    def __init__(self, filename=''):
        # public properties
        self.yaml_as_dict = collections.OrderedDict()
        # protected properties
        self._filename = filename
        # calls to methods
        self._read_yaml_file()

    def _read_yaml_file(self):
        with open(self._filename, 'r') as stream:
            self.yaml_as_dict = oyaml.load(stream)


if __name__ == '__main__':
    obj = YamlLoader('metadata_mapper.yaml')
    PATH = '../../Daten/messung01/'
    imp = SpeksimImporter(source=PATH)
    imp.dataset.import_from(imp)
