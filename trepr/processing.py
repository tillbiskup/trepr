"""
General processing facilities.

For the sake of simplicity, the two processing classes averaging and
pretrigger_offset_compensation are combined in one module.
"""


import numpy as np

import aspecd.processing
from trepr import io


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class DimensionError(Error):
    """Exception raised when the dimension isn't zero or one.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class RangeError(Error):
    """Exception raised when the given range is out of the dataset's range.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class UnitError(Error):
    """Exception raised when the unit isn't either 'axsi' or 'index'.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Averaging(aspecd.processing.ProcessingStep):
    """Averaging of two-dimensional data along a given axis.

    When measuring TREPR data, the resulting spectrum is always
    two-dimensional. To analyse the data it's necessary to extract a
    one-dimensional spectrum. The one-dimensional spectrum can either be a cut
    along the field or the time axis. To get a representative spectrum, the
    average over several measurement points is calculated.

    Parameters
    ----------
    dimension : 0,1
        Dimension along the averaging is done. 0 is along the field axis and 1
        is along the time axis. Default is 0.

    avg_range : list
        Range in which the averaging will take place.

    unit : 'axis', 'index'
        Unit in which the average range is given. Either 'axis' for axis values
        or 'index' for indices. Default is axis.

    Attributes
    ----------
    parameters : dict
        All Parameters that must be known to reproduce the averaging.

    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.

    Raises
    ------
    DimensionError
        Raised if dimension is not in [0, 1].

    UnitError
        Raised if unit is not in ['axis', 'index'].

    RangeError
        Raised if range is not within axis.

    """

    def __init__(self, dimension=0, avg_range=None, unit='axis'):
        super().__init__()
        # public properties
        self.description = 'Averaging'
        self.undoable = True
        self.parameters['dimension'] = dimension
        self.parameters['range'] = avg_range
        self.parameters['unit'] = unit
        # protected properties:
        self._dim = self.parameters['dimension']

    def _perform_task(self):
        """Perform the processing step."""
        avg_range = self.parameters['range']
        if self.parameters['unit'] == 'axis':
            start_index =\
                self._get_index(self.dataset.data.axes[self._dim].values,
                                avg_range[0])
            end_index = \
                self._get_index(self.dataset.data.axes[self._dim].values,
                                avg_range[-1])
            avg_range = [start_index, end_index]
        if self._dim == 0:
            axes = [self.dataset.data.axes[1], self.dataset.data.axes[2]]
            self.dataset.data.data = \
                np.average(self.dataset.data.data[:, avg_range], axis=1)
            self.dataset.data.axes = axes
        else:
            axes = [self.dataset.data.axes[0], self.dataset.data.axes[2]]
            self.dataset.data.data = \
                np.average(self.dataset.data.data[avg_range, :], axis=0)
            self.dataset.data.axes = axes

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()

    def _sanitise_parameters(self):
        if self.parameters['dimension'] not in [0, 1]:
            raise DimensionError('Wrong dimension. Choose 0 or 1.')
        if self.parameters['unit'] not in ['index', 'axis']:
            raise UnitError('Wrong unit. Choose "axis" or "index".')
        if self.parameters['unit'] == 'index':
            if self.parameters['range'][0] \
                    not in range(len(self.dataset.data.axes[self._dim].values)):
                raise RangeError('Lower index out of range.')
            if self.parameters['range'][1] \
                    not in range(len(self.dataset.data.axes[self._dim].values)):
                raise RangeError('Upper index out of range.')
        if self.parameters['unit'] == 'axis':
            if not self._value_within_vector_range(
                    self.parameters['range'][0],
                    self.dataset.data.axes[self._dim].values):
                raise RangeError('Lower value out of range.')
            if not self._value_within_vector_range(
                    self.parameters['range'][1],
                    self.dataset.data.axes[self._dim].values):
                raise RangeError('Upper value out of range.')
        if self.parameters['range'][1] < self.parameters['range'][0]:
            raise RangeError('Values need to be ascending.')

    @staticmethod
    def _value_within_vector_range(value, vector):
        return np.amin(vector) <= value <= np.amax(vector)


class PretriggerOffsetCompensation(aspecd.processing.ProcessingStep):
    """
    Pretrigger offset compensation.

    One of the first processing steps after measuring TREPR data is to set the
    average of the pretrigger time trace to zero. The so called pretrigger
    offset compensation.

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.

    """

    def __init__(self):
        super().__init__()
        # public properties:
        # Note: self.parameters inherited
        self.description = 'Pretrigger offset compensation'
        self.undoable = True

    def _perform_task(self):
        """Perform the processing step and return the processed data."""
        self._get_zeropoint_index()
        range_end = self.parameters['zeropoint_index']
        for field_point, time_trace in enumerate(self.dataset.data.data):
            pretrig_avg = self._get_pretrigger_average(time_trace, range_end)
            self.dataset.data.data[field_point] = time_trace - pretrig_avg

    def _get_zeropoint_index(self):
        """Get the index of the last time value before the trigger."""
        zeropoint_index = \
            np.argmin(np.cumsum(self.dataset.data.axes[0].values))
        self.parameters['zeropoint_index'] = int(zeropoint_index)

    @staticmethod
    def _get_pretrigger_average(time_trace, range_end=1):
        """Calculate the average of the time trace before triggering."""
        array = time_trace[0:range_end]
        return np.average(array)


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = io.SpeksimImporter(source=PATH)
    dataset = aspecd.dataset.Dataset()
    dataset.import_from(importer)

    pretrigger = PretriggerOffsetCompensation()
    process1 = importer.dataset.process(pretrigger)
    print(importer.dataset.history[0].processing.parameters)

    avg = Averaging(dimension=1, avg_range=[2900, 2904], unit='axis')
    process2 = dataset.process(avg)
    print(importer.dataset.history[1].processing.parameters)
