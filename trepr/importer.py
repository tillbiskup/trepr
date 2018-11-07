"""
Importer.

Trepr raw data consists of multiple timetraces, each stored in a text file.
To analyze the raw data, it's necessary to bring the timetraces all together
in form which can be stored as one dataset.

This module imports raw data, defines the axis and hands all over to a dataset.
"""

import glob
import io
import os
import re

import numpy as np

import aspecd.data
import aspecd.dataset
import aspecd.importer
import aspecd.infofile
from trepr import Dataset


class Importer(aspecd.importer.Importer):
    """Import a dataset including its metadata.

    Parameters
    ----------
    path : str
        Path to the dataset.

    Attributes
    ----------
    dataset : object
        Object of the dataset class.

    """

    def __init__(self, path=''):
        super().__init__()
        # public properties
        self.dataset = Dataset()
        # private properties
        self._HEADERLINES = 5
        self._path = path
        self._data = np.array([])
        self._file_format = ''
        self._timestamps = list()
        self._freq = np.array([])
        self._commentline = ''
        self._timeunit = ''
        self._fieldunit = ''
        self._intensityunit = ''
        self._frequnit = ''
        self._timeaxis = np.array([])
        self._fieldaxis = np.array([])
        self._infofile = dict()
        self._header = list()
        self._formatno = int()
        self._time_start = float()
        self._time_stop = float()
        self._timepoints = int()

    def _import(self):
        """Execute all necessary methods and write the data to a dataset."""
        self._import_raw_data()
        self._create_timeaxis()
        self._read_infofile()
        self._hand_data_to_dataset()
        self._hand_axes_to_dataset()

    def _import_raw_data(self):
        """Import the timetraces and cut off the header lines."""
        filenames = sorted(glob.glob(os.path.join(self._path, '*.[0-9][0-9][0-9]')))
        for filename in filenames:
            with open(filename) as file:
                raw_data = file.read()
            lines = raw_data.splitlines()
            self._header = lines[0:5]
            self._parse_header()
            numeric_data = np.loadtxt(io.StringIO(raw_data), skiprows=5)
            numeric_data = np.reshape(numeric_data, self._timepoints)
            self._data = np.append(self._data, numeric_data)
        self._data = \
            np.reshape(self._data, [len(filenames), self._timepoints])

    def _hand_data_to_dataset(self):
        """Hand the data to the dataset structure."""
        self.dataset.data.data = self._data

    def _hand_axes_to_dataset(self):
        """Hand the axes and intensity to the dataset structure."""
        self.dataset.data.axes[0].values = self._timeaxis
        self.dataset.data.axes[0].unit = self._timeunit
        self.dataset.data.axes[0].quantity = 'time'
        self.dataset.data.axes[1].values = self._fieldaxis
        self.dataset.data.axes[1].unit = self._fieldunit
        self.dataset.data.axes[1].quantity = 'magnetic field'
        self.dataset.data.axes[2].unit = self._intensityunit
        self.dataset.data.axes[2].quantity = 'intensity'

    def _parse_header(self):
        """Execute the methods which parse the header lines."""
        self._parse_header_1st_line()
        self._parse_header_2nd_line()
        self._parse_header_3rd_line()
        self._parse_header_4th_line()
        self._parse_header_5th_line()

    def _parse_header_1st_line(self):
        """Parse the first header line and extract the time and date."""
        entries = self._header[0].split(';')
        self._file_format = entries[0].split(':')[1].strip()
        timestamp = entries[1].split(' : ')[1]
        self._timestamps.append(timestamp)

    def _parse_header_2nd_line(self):
        """Extract the field- and frequency-unit from the second header line."""
        def parse_line(line):
            obj = re.search('([A-Za-z0-9]*) = ([0-9.]*) ([A-Za-z]*)', line)
            return float(obj.group(2)), obj.group(3)
        entries = self._header[1].split(',')
        field, self._fieldunit = parse_line(entries[0])
        freq, self._frequnit = parse_line(entries[1])
        self._fieldaxis = np.append(self._fieldaxis, field)
        self._freq = np.append(self._freq, freq)

    def _parse_header_3rd_line(self):
        """Parse the third header line."""
        self._commentline = self._header[2]

    def _parse_header_4th_line(self):
        """Extract the format number, time information from the fourth header line."""
        entries = self._header[3].split()[0:4]
        self._formatno = int(entries[0])
        self._timepoints = int(entries[1])
        self._time_start = float(entries[2])
        self._time_stop = float(entries[3])

    def _parse_header_5th_line(self):
        """Extract the time- and intensity-unit from the fifth header line."""
        self._timeunit, self._intensityunit = self._header[4].split()

    def _create_timeaxis(self):
        """Create the timeaxis using the startpoint, endpoint and timepoints."""
        self._timeaxis = \
            np.linspace(self._time_start, self._time_stop, num=self._timepoints)

    def _read_infofile(self):
        """Import the infofile and parse it."""
        infofile_name = glob.glob(os.path.join(self._path, '*.info'))
        if not infofile_name:
            print('Besorg dir ein Infofile!')
            return
        self.dataset.metadata = aspecd.infofile.parse(infofile_name[0])
        #self._infofile = aspecd.infofile.parse(infofile_name[0])


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = Importer(path=PATH)
    importer.dataset.import_from(importer)
    print(importer.dataset.data.data)
