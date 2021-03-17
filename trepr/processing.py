"""
General processing facilities.

Due to the inheritance from the :mod:`aspecd.processing` module, all processing
steps provided are fully self-documenting, i.e. they add all necessary
information to reproduce each processing step to the
:attr:`trepr.dataset.Dataset.history` attribute of the dataset.

"""
import cwepr.processing
import numpy as np

import aspecd.processing
import aspecd.exceptions
import scipy.signal


class Error(Exception):
    """Base class for exceptions in this module."""


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
    two-dimensional. To analyse the data it's often necessary to extract a
    one-dimensional spectrum. The one-dimensional spectrum can either be a cut
    along the field or the time axis. To get a representative spectrum, the
    average over several points along the respective axis is calculated.

    All parameters, implicit and explicit, necessary to perform the averaging
    processing step, will be stored in the attribute
    :attr:`trepr.processing.Averaging.parameters`.

    An example for using the averaging processing step may look like this::

        avg = Averaging(dimension=0, avg_range=[4.e-7, 6.e-7], unit='axis')
        dataset.process(avg)

    Parameters
    ----------
    dimension : {0,1}, optional
        Dimension along which the averaging is done. 0 is along the field axis
        and 1 is along the time axis. Default is 0.

    avg_range : list
        Range in which the averaging will take place.

    unit : {'axis', 'index'}, optional
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
        self._dim = 1 if self.parameters['dimension'] == 0 else 0

    def _perform_task(self):
        """Perform the processing step."""
        avg_range = self._get_avg_range()
        self._execute_averaging(avg_range)

    def _get_avg_range(self):
        """Calculate the range within the averaging will be performed."""
        if self.parameters['unit'] == 'axis':
            start_index = \
                self._get_index(self.dataset.data.axes[self._dim].values,
                                self.parameters['range'][0])
            end_index = \
                self._get_index(self.dataset.data.axes[self._dim].values,
                                self.parameters['range'][-1])
            avg_range = [start_index, end_index]
        else:
            avg_range = self.parameters['range']
        return avg_range

    def _execute_averaging(self, avg_range):
        """Apply the averaging on the given experimental dataset."""
        if self._dim == 0:
            # keep time and intensity axes
            axes = [self.dataset.data.axes[1], self.dataset.data.axes[2]]
            self.dataset.data.data = np.average(self.dataset.data.data[:,
                                                avg_range[0]:avg_range[1]],
                                                axis=0)
        else:
            # keep B and intensity axes
            axes = [self.dataset.data.axes[0], self.dataset.data.axes[2]]
            self.dataset.data.data = np.average(self.dataset.data.data[:,
                                                avg_range[0]:avg_range[1]],
                                                axis=1)
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
            if self.parameters['range'][0] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
                raise RangeError('Lower index out of range.')
            if self.parameters['range'][1] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
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
    average of the pretrigger time trace to zero. The so-called pretrigger
    offset compensation.

    All parameters, implicit and explicit, necessary to perform the averaging
    processing step, will be stored in the attribute
    :attr:`trepr.processing.PretriggerOffsetCompensation.parameters`.

    An example for using the pretrigger offset compensation processing step may
    look like this::

        poc = PretriggerOffsetCompensation()
        dataset.process(poc)

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
        self._execute_compensation(self.parameters['zeropoint_index'])

    def _get_zeropoint_index(self):
        """Get the index of the last time value before the trigger."""
        zeropoint_index = \
            np.argmin(abs(self.dataset.data.axes[1].values))
        self.parameters['zeropoint_index'] = int(zeropoint_index)

    def _execute_compensation(self, range_end):
        """Execute the pretrigger offset compensation."""
        for field_point, time_trace in enumerate(self.dataset.data.data):
            pretrig_avg = self._get_pretrigger_average(time_trace, range_end)
            self.dataset.data.data[field_point] = time_trace - pretrig_avg

    @staticmethod
    def _get_pretrigger_average(time_trace, range_end=1):
        """Calculate the average of the time trace before triggering."""
        array = time_trace[0:range_end]
        return np.average(array)


class Normalisation(aspecd.processing.Normalisation):
    """Class fully inherited from ASpecD for simple usage."""


class BackgroundCorrection(aspecd.processing.ProcessingStep):
    def __init__(self):
        super().__init__()
        # public properties:
        self.description = 'Background correction of 2D spectrum'
        self.undoable = True
        self.parameters['num_profiles'] = 5, 5

    @staticmethod
    def applicable(dataset):
        return len(dataset.data.axes) == 3

    def _sanitise_parameters(self):
        if isinstance(self.parameters['num_profiles'], tuple):
            self.parameters['num_profiles'] = \
                list(self.parameters['num_profiles'])
        if isinstance(self.parameters['num_profiles'], list) and \
                len(self.parameters['num_profiles']) == 1:
            self.parameters['num_profiles'] = self.parameters['num_profiles'][0]

    def _perform_task(self):
        self._check_data_size()
        self._subtract_background()

    def _check_data_size(self):
        if isinstance(self.parameters['num_profiles'], list):
            num_profiles = sum(self.parameters['num_profiles'])
        else:
            num_profiles = self.parameters['num_profiles']
        if len(self.dataset.data.axes[0].values) <= 2 * num_profiles:
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message='The given dataset ist too small to perform '
                        'appropriate background correction.')

    def _subtract_background(self):
        if isinstance(self.parameters['num_profiles'], list) and \
                len(self.parameters['num_profiles']) == 2:
            self._bg_corr_with_slope()
        else:
            self._bg_corr_one_side()

    def _bg_corr_with_slope(self):
        low = self.parameters['num_profiles'][0]
        high = abs(self.parameters['num_profiles'][1])
        lower_mean = np.mean(self.dataset.data.data[:low])
        higher_mean = np.mean(self.dataset.data.data[-high:])
        slope = (higher_mean - lower_mean) / self.dataset.data.data.shape[0]
        for idx, transient in enumerate(self.dataset.data.data):
            transient -= lower_mean + slope * idx

    def _bg_corr_one_side(self):
        assert type(self.parameters['num_profiles']) == int

        if self.parameters['num_profiles'] < 0:
            self._subtract_from_end()
        else:
            self._subtract_from_begin()

    def _subtract_from_end(self):
        bg = np.mean(self.dataset.data.data[self.parameters['num_profiles']:])
        self.dataset.data.data -= bg

    def _subtract_from_begin(self):
        bg = np.mean(self.dataset.data.data[:self.parameters['num_profiles']])
        self.dataset.data.data -= bg


class NormalisationOld(aspecd.processing.ProcessingStep):
    """Normalise data.

    Possible normalisations are area and maximum.

    applicable in 2D datasets as well?

    See Also
    --------
    aspecd.processing.Normalisation :
        Equivalent method with even more functionalities

    """

    def __init__(self):
        super().__init__()
        self.description = 'Normalise data in dataset.'
        self.parameters['type'] = 'area'

    def _perform_task(self):
        if self.parameters['type'] == "area":
            self.dataset.data.data = \
                self.dataset.data.data / np.sum(abs(self.dataset.data.data),
                                                axis=1)
        elif self.parameters['type'] == "maximum":
            self.dataset.data.data = \
                self.dataset.data.data / np.amax(abs(self.dataset.data.data))
        else:
            self.dataset.data.data = \
                self.dataset.data.data / sum(abs(self.dataset.data.data))


class FrequencyCorrection(cwepr.processing.FrequencyCorrection):
    """Frequency correction of the cwepr package should work."""


class Filter(aspecd.processing.ProcessingStep):
    """Apply a filter to smooth 1D data.

    Be careful to show filtered spectra.

    It can be chosen between boxcar, Savitzky-Golay and binomial filters.

    Savitzky-Golay:
    Takes a certain number of points and fits a polynomial through them.

    Reference for the Savitzky-Golay Filter:

     * A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of Data by
       Simplified Least Squares Procedures. Analytical Chemistry, 1964,
       36 (8), pp 1627-1639.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        type : :class:`str`
            Type of the applied filter. Valid inputs: savitzky-golay,
            binomial, boxcar and some abbreviations and variations.

            Default: savitzky-golay

        window_width : :class:`int`
            Full filter window width. Must be an odd number

            Default: 1/5 of the data length.

    """

    def __init__(self):
        super().__init__()
        self.description = 'Filter 1D dataset.'
        self.parameters['type'] = 'savitzky-golay'
        self.parameters['window_width'] = None
        self.parameters['order'] = 2

    @staticmethod
    def applicable(dataset):
        return len(dataset.data.axes) == 2

    def _sanitise_parameters(self):
        self._set_defaults()  # must be here for referring to right type.
        if int(self.parameters['window_width']) % 2 == 0:
            self.parameters['window_width'] += 1
            print('For applying the filter, the window length must be odd. '
                  'I added one.')

    def _get_type(self):
        """Allow for different inputs, unify them."""
        types = {
            'savitzky_golay': ['savitzky_golay', 'savitzky-golay',
                               'savitzky golay', 'savgol', 'savitzky'],
            'binomial': ['binom', 'binomial'],
            'boxcar': ['box', 'boxcar', 'moving-average', 'car']
        }
        for key, value in types.items():
            if self.parameters['type'] in value:
                self.parameters['type'] = key
            if self.parameters['type'] == 'car':
                print('Haha, good joke! You\'ve got a boxcar')

    def _perform_task(self):
        if self.parameters['type'] == 'boxcar':
            self._apply_boxcar()
        elif self.parameters['type'] == 'binomial':
            self._apply_binomial()
        else:
            self._apply_savitzky_golay()

    def _set_defaults(self):
        self._get_type()
        if not self.parameters['window_width']:
            self.parameters['window_width'] = int(np.ceil((1/10 * len(
                self.dataset.data.axes[0].values))) * 2+1)

    def _apply_savitzky_golay(self):
        filtered_data = \
            scipy.signal.savgol_filter(self.dataset.data.data,
                                       int(self.parameters['window_width']),
                                       self.parameters['order'])
        self.dataset.data.data = filtered_data

    def _apply_binomial(self):
        self._add_padding()
        self._perform_binomial_filtering()

    def _apply_boxcar(self):
        self._add_padding()
        self._perform_boxcar_filtering()

    def _add_padding(self):
        """Add padding to get same lenth of data at the end."""
        width = self.parameters['window_width']
        self.dataset.data.data = np.concatenate((
            np.ones(int(np.floor(width/2)))*self.dataset.data.data[0],
            self.dataset.data.data,
            np.ones(int(np.floor(width/2))+1)*self.dataset.data.data[-1]
        ))

    def _perform_binomial_filtering(self):
        filter_coefficients = (np.poly1d([0.5, 0.5]) ** self.parameters[
            'window_width']).coeffs
        filtered_data = np.array(np.convolve(self.dataset.data.data,
                                             filter_coefficients, mode='valid'))
        self.dataset.data.data = filtered_data

    def _perform_boxcar_filtering(self):
        filter_ = np.ones(self.parameters['window_width'])/self.parameters[
            'window_width']
        filtered_data = np.array(np.convolve(self.dataset.data.data,
                                             filter_, mode='valid'))
        self.dataset.data.data = filtered_data[:-1]



