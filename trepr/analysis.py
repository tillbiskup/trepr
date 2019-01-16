"""
General analysis facilities.

In order to quantify the quality of a measured spectrum or to interpret it, it
may be helpful to perform some analysis steps.

Due to the inheritance from :mod:`aspecd.analysis` all provided analysis
steps are fully self-documenting in order of adding all necessary information
to reproduce each analysis step to the :attr:`aspecd.dataset.Dataset.history`
attribute of a dataset.

"""


from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import numpy as np
from scipy import constants

import aspecd.analysis
import aspecd.metadata
import SpecProFi.trepr_interface
import trepr.io


class MwFreqAnalysis(aspecd.analysis.AnalysisStep):
    """
    Calculate the frequency shift and compare it with the step size.

    In order to estimate the quality of a spectrum, it can be helpful to know
    the frequency shift of the measurement.

    An example for using the microwave frequency analysis step may look like
    this::

        import trepr.dataset

        dataset_ = trepr.dataset.Dataset()
        analysis_step = MwFreqAnalysis()
        analysis_step.analyse(dataset=dataset_)

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Microwave frequency analysis'
        # protected properties
        self._delta_mw_freq = float()
        self._delta_B0 = float()
        self._step_size_in_T = float()
        self._ratio_frequency_drift_to_step_size = float()

    def _perform_task(self):
        """Perform all methods to do analysis."""
        self._calculate_mw_freq_amplitude()
        self._convert_delta_mw_freq_to_delta_B0()
        self._calculate_step_size()
        self._compare_delta_B0_with_step_size()
        self._write_results()

    def _calculate_mw_freq_amplitude(self):
        """Calculate the amplitude of the microwave frequency."""
        self._delta_mw_freq = max(self.dataset.microwave_frequency.data) \
                              - min(self.dataset.microwave_frequency.data)

    def _convert_delta_mw_freq_to_delta_B0(self):
        """Calculate delta B0 by using the resonance condition."""
        electron_g_factor = constants.value('electron g factor')
        bohr_magneton = constants.value('Bohr magneton')
        planck_constant = constants.value('Planck constant')
        self._delta_B0 = self._delta_mw_freq * 1e9 * planck_constant \
                         / (-1 * electron_g_factor * bohr_magneton)

    def _calculate_step_size(self):
        """Calculate the step size of the given dataset."""
        step_size_in_gauss = \
            self.dataset.microwave_frequency.axes[0].values[1] \
            - self.dataset.microwave_frequency.axes[0].values[0]
        self._step_size_in_T = step_size_in_gauss * 1e-4

    def _compare_delta_B0_with_step_size(self):
        """Calculate the ratio between delta B0 and the step size."""
        self._ratio_frequency_drift_to_step_size = \
            self._delta_B0 / self._step_size_in_T

    def _write_results(self):
        self.results['frequency drift'] = aspecd.metadata.PhysicalQuantity(
            value=self._delta_B0, unit='T')
        self.results['ratio frequency drift/step size'] = \
            self._ratio_frequency_drift_to_step_size


class TimeStampAnalysis(aspecd.analysis.AnalysisStep):
    """
    Calculate the measurement time of each time trace and plot them against the
    magnetic field.

    In order to estimate the quality of a spectrum, it can be helpful to know
    the measurement time of the each time trace.

    An example for using the time stamp analysis step may look like
    this::

        import trepr.dataset

        dataset_ = trepr.dataset.Dataset()
        analysis_step = TimeStampAnalysis()
        analysis_step.analyse(dataset=dataset_)

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
        self._write_results()

    def _create_time_field_matrix(self):
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
                datetime.fromtimestamp(time_stamp))

    def _calculate_time_stamp_delta(self):
        zero = datetime(2018, 1, 1)
        for i in range(len(self._time_stamp_datetimes) - 1):
            self._time_stamp_datetimes[i] = self._time_stamp_datetimes[i+1] - \
                                            self._time_stamp_datetimes[i] + \
                                            zero
        del self._time_stamp_datetimes[-1]
        zero = mdates.date2num(zero)
        for i in range(len(self._time_stamp_datetimes)):
            self._time_stamp_datetimes[i] = \
                mdates.date2num(self._time_stamp_datetimes[i]) - zero
        self._time_field_matrix = \
            np.delete(self._time_field_matrix, -1, axis=0)
        plt.plot(self._time_field_matrix[:, 1], self._time_stamp_datetimes,
                 linestyle='', marker='.')
        plt.show()

    def _write_results(self):
        self.results['time spent per time trace'] = self._time_stamp_datetimes


class FittingAnalysis(aspecd.analysis.AnalysisStep):
    """
    Fit a given spectrum with a set of parameters.

    In order to interpret a spectrum, it is essential to know the parameters
    that make up the shape of the spectrum. To achieve this, the spectrum can
    be fitted and the best possible parameters determined using a least-square.

    An example for using the fitting analysis analysis step may look like
    this::

        import trepr.io

        dataset_ = trepr.dataset.Dataset()
        yaml_file = trepr.io.YamlLoader('path/to/your/yaml/file')
        input_parameters = yaml_file.yaml_dict
        analysis_step = FittingAnalysis()
        analysis_step.parameters = input_parameters
        analysis_step.analyse(dataset=dataset_)

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    """

    def __init__(self):
        super().__init__()
        self.description = 'Fitting analysis.'

    def _perform_task(self):
        SpecProFi.trepr_interface.TREPRInterface(
            fitting_parameters=self.parameters, dataset_=self.dataset).fit()


if __name__ == '__main__':
    imp = trepr.io.SpeksimImporter(
        '/home/popp/nas/DatenBA/PCDTBT-PET-RNK-asCast/X-Band/080K/messung06/')
    dataset_ = trepr.dataset.Dataset()
    dataset_.import_from(imp)

    """
    analysis_step = TimeStampAnalysis()
    analysis_step.analyse(dataset=dataset_)
    """
    pretrigger = trepr.processing.PretriggerOffsetCompensation()
    dataset_.process(pretrigger)
    averaging = trepr.processing.Averaging(dimension=0, avg_range=[4.e-7, 6.e-7], unit='axis')
    dataset_.process(averaging)
    yaml = trepr.io.YamlLoader('specprofi-input.yaml')
    parameter_dict = yaml.yaml_as_dict
    fitting_obj = FittingAnalysis()
    fitting_obj.parameters = parameter_dict
    fitting_obj.analyse(dataset=dataset_)
