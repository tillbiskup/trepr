"""
General analysis facilities.

In order to quantify the quality of a measured spectrum or to interpret it, it
may be helpful to perform some analysis steps.

Due to inheritance from the :mod:`aspecd.analysis` module all analysis steps
provided are fully self-documenting, i.e. they add all necessary information
to reproduce each analysis step to the :attr:`aspecd.dataset.Dataset.history`
attribute of the dataset.

"""

import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import numpy as np
import scipy.constants

import aspecd.analysis
import aspecd.metadata
import aspecd.utils


# import trepr.interfaces


class MwFreqAnalysis(aspecd.analysis.SingleAnalysisStep):
    """
    Calculate the frequency drift and compare it with the step size.

    In order to estimate the quality of a spectrum, it can be helpful to know
    the extent the frequency drifted during the measurement.

    An example for using the microwave frequency analysis step may look like
    this::

        dataset_ = trepr.dataset.ExperimentalDataset()
        analysis_step = MwFreqAnalysis()
        dataset_.analyse(analysis_step)

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Microwave frequency drift analysis.'
        # protected properties
        self._delta_mw_freq = float()
        self._delta_B0 = float()
        self._step_size_in_mT = float()
        self._ratio_frequency_drift_to_step_size = float()

    @staticmethod
    def applicable(dataset):
        return dataset.microwave_frequency.data.any()

    def _perform_task(self):
        """Perform all methods to do analysis."""
        self._calculate_mw_freq_amplitude()
        self._convert_delta_mw_freq_to_delta_B0()
        self._calculate_step_size()
        self._compare_delta_B0_with_step_size()
        self._write_result()

    def _calculate_mw_freq_amplitude(self):
        """Calculate the amplitude of the microwave frequency."""
        self._delta_mw_freq = max(self.dataset.microwave_frequency.data) - \
                              min(self.dataset.microwave_frequency.data)

    def _convert_delta_mw_freq_to_delta_B0(self):
        """Calculate delta B0 by using the resonance condition."""
        electron_g_factor = scipy.constants.value('electron g factor')
        bohr_magneton = scipy.constants.value('Bohr magneton')
        planck_constant = scipy.constants.value('Planck constant')
        self._delta_B0 = self._delta_mw_freq * 1e9 * planck_constant \
                         / (-1 * electron_g_factor * bohr_magneton)

    def _calculate_step_size(self):
        """Calculate the step size of the given dataset."""
        self._step_size_in_mT = \
            self.dataset.microwave_frequency.axes[0].values[1] \
            - self.dataset.microwave_frequency.axes[0].values[0]

    def _compare_delta_B0_with_step_size(self):
        """Calculate the ratio between delta B0 and the step size."""
        self._ratio_frequency_drift_to_step_size = \
            self._delta_B0 / self._step_size_in_mT

    def _write_result(self):
        """Write the results in the results dictionary."""
        self.result = {
            'frequency drift': aspecd.metadata.PhysicalQuantity(
                value=self._delta_B0, unit='T'),
            'ratio frequency drift/step size': \
                self._ratio_frequency_drift_to_step_size}


class TimeStampAnalysis(aspecd.analysis.SingleAnalysisStep):
    """
    Calculate the time spent for recording each time trace.

    Can be helpful for debugging the spectrometer.

    An example for using the time stamp analysis step may look like
    this::

        dataset_ = trepr.dataset.ExperimentalDataset()
        analysis_step = TimeStampAnalysis()
        dataset_.analyse(analysis_step)

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Time stamp analysis.'
        # protected properties
        self._time_field_matrix = None
        self._time_stamp_datetimes = list()

    def _perform_task(self):
        """Perform all methods to do analysis."""
        self._create_time_field_matrix()
        self._calculate_time_stamp_delta()
        self._write_result()

    def _create_time_field_matrix(self):
        """Create a matrix containing the time stamps and the corresponding
        field points"""
        time_stamp_floats = np.zeros(0)
        for time_stamp in self.dataset.time_stamp.data:
            time_stamp_floats = \
                np.append(time_stamp_floats, time_stamp.timestamp())
        self._time_field_matrix = np.zeros((len(time_stamp_floats), 2))
        self._time_field_matrix[:, 0] = time_stamp_floats
        self._time_field_matrix[:, 1] = self.dataset.time_stamp.axes[0].values
        self._time_field_matrix = \
            self._time_field_matrix[self._time_field_matrix[:, 0].argsort()]
        for time_stamp in self._time_field_matrix[:, 0]:
            self._time_stamp_datetimes.append(
                datetime.datetime.fromtimestamp(time_stamp))

    def _calculate_time_stamp_delta(self):
        """Calculate the time between the time stamps"""
        zero = datetime.datetime(2018, 1, 1)
        for i in range(len(self._time_stamp_datetimes) - 1):
            self._time_stamp_datetimes[i] = self._time_stamp_datetimes[i + 1] - \
                                            self._time_stamp_datetimes[i] + \
                                            zero
        del self._time_stamp_datetimes[-1]
        zero = mdates.date2num(zero)
        for i in range(len(self._time_stamp_datetimes)):
            self._time_stamp_datetimes[i] = \
                mdates.date2num(self._time_stamp_datetimes[i]) - zero
        self._time_field_matrix = \
            np.delete(self._time_field_matrix, -1, axis=0)
        #plt.plot(self._time_field_matrix[:, 1], self._time_stamp_datetimes,
        #         linestyle='', marker='.')
        #plt.show()

    def _write_result(self):
        """Write the result to the attribute
        :attr:`aspecd.analysis.AnalysisStep.result`"""
        self.result = {'time spent per time trace': self._time_stamp_datetimes}