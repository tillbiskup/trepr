"""Averaging.

When measuring trepr, the resulting spectrum is always two dimensional.
To analyse the data it's necessary to extract a one dimensional spectrum.
The one dimensional spectrum can either be a cut along the field- or the
timeaxis. To get a representative spectrum, the average over several
measurementpoints is calculatet.

This module calculates the average in a given range along a given axis.
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
    """Averaging of a given dataset along one of its two dimensions.

    Parameters
    ----------
    dimension : 0,1
        Dimension along the averaging is done. 0 is along the fieldaxis and 1
        is along the timeaxis. Default is 0.

    average_range : list
        Range in which the averaging will take place.

    unit : 'axis', 'index'
        Unit in which the average range is given. Either 'axis' for axisvalues
        or 'index' for indices. Default is axis.

    Attributes
    ----------
    parameters : dict
        All Parameters that must be known to reproduce the averaging.

    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.

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
        if self.parameters['unit'] == 'axis':
            start_index = self._get_index(self.dataset.data.axes[self._dim].values,
                                          self.parameters['range'][0])
            end_index = self._get_index(self.dataset.data.axes[self._dim].values,
                                        self.parameters['range'][-1])
            self.parameters['range'] = [start_index, end_index]
        if self._dim == 0:
            axes = [self.dataset.data.axes[1], self.dataset.data.axes[2]]
            self.dataset.data.data = np.average(
                self.dataset.data.data[:, self.parameters['range']], axis=1)
            self.dataset.data.axes = axes
        else:
            axes = [self.dataset.data.axes[0], self.dataset.data.axes[2]]
            self.dataset.data.data = np.average(
                self.dataset.data.data[self.parameters['range'], :], axis=0)
            self.dataset.data.axes = axes

    @staticmethod
    def _get_index(vector, value):
        return np.abs(vector - value).argmin()

    @staticmethod
    def _value_within_vector_range(value, vector):
        return np.amin(vector) <= value <= np.amax(vector)

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


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = importer.Importer(path=PATH)
    dataset = aspecd.dataset.Dataset()
    dataset.import_from(importer)
    obj = Averaging(dimension=1, avg_range=[2900, 2904], unit='axis')
    process = dataset.process(obj)
