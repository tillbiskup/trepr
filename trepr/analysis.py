"""
Data analysis functionality.

.. sidebar:: Processing vs. analysis steps

    The key difference between processing and analysis steps: While a
    processing step *modifies* the data of the dataset it operates on,
    an analysis step returns a result based on data of a dataset, but leaves
    the original dataset unchanged.


Key to reproducible science is automatic documentation of each analysis
step applied to the data of a dataset. Such an analysis step each is
self-contained, meaning it contains every necessary information to perform
the analysis task on a given dataset.

Analysis steps, in contrast to processing steps (see
:mod:`trepr.processing` for details), operate on data of a
:class:`trepr.dataset.Dataset`, but don't change its data. Rather,
some result is obtained that is stored separately, together with the
parameters of the analysis step, in the
:attr:`trepr.dataset.Dataset.analyses` attribute of the dataset.

In order to quantify the quality of a measured spectrum or to interpret it, it
is often necessary to perform some analysis steps.

Due to inheritance from the :mod:`aspecd.analysis` module all analysis steps
provided are fully self-documenting, i.e. they add all necessary information
to reproduce each analysis step to the :attr:`aspecd.dataset.Dataset.history`
attribute of the dataset.

"""

import datetime
import matplotlib.dates as mdates

import numpy as np
import scipy.constants

import aspecd.analysis
import aspecd.metadata
import aspecd.utils

import trepr.dataset


class MWFrequencyDrift(aspecd.analysis.SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Calculate the frequency drift and compare it with the step size.

    In order to estimate the quality of a spectrum, it can be helpful to know
    the extent the frequency drifted during the measurement. Therefore,
    the frequency drift is converted into magnetic field units and can
    thus be compared to the step width of the magnetic field axis.

    Different outputs, *e.g.* a scalar value or a calculated dataset, are
    available, for details see below.


    Attributes
    ----------
    description : str
        Describes the aim of the class.

    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of characteristic to extract from the data

            Valid values are "ratio" and "drift".

            In case of "ratio", the ratio between drift and magnetic field
            step will be returned, in case of "drift", the amplitude of
            the microwave frequency values converted into magnetic field
            units (mT).

            Only relevant in case of "output" set to "value" or "dataset".

            Default: "ratio"

        output : :class:`str`
            Kind of output: value or dict

            Valid values are "value" (default), "dataset", and "dict".
            Usually, only values and datasets can be easily used within a
            recipe.

            Default: "value"

    result : :class:`float`, :class:`dict`, or :class:`trepr.dataset.CalculatedDataset`
        Results of the microwave frequency drift analysis.

        Depending on the output option set via the "output" parameter,
        either a scalar value (ratio or drift), , a dict containing both
        values, or a dataset containing either the ratios or the drifts as
        function of the magnetic field.

        In case of datasets, note that due to calculating a difference
        between microwave frequency points, the size of the data is -1
        compared to the size of the original microwave frequency values.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    If you have recorded a dataset containing microwave frequency values
    for each individual time trace and are interested in the drift of the
    microwave frequency converted into magnetic field values, you can
    obtain a calculated dataset with the values and plot the results:

    .. code-block:: yaml

        - kind: singleanalysis
          type: MWFrequencyDrift
          properties:
            parameters:
              kind: drift
              output: dataset
          apply_to: speksim/
          result: mwfreq-drift

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            parameters:
              tight_layout: true
            filename: mwfreq-drift.pdf
          apply_to: mwfreq-drift


    While getting the absolute values is often quite helpful, dividing the
    values by the magnetic field step width (assuming an equidistant axis)
    allows to directly assess whether the drift is relevant for the
    particular dataset. Which ratio is tolerable depends on the kind of
    spectra, but it should be <1 (better <0.5). Obtaining the ratio of
    frequency drift (in magnetic field units) and the step width is
    similar to the example above, and again, plotting the results is quite
    helpful:

    .. code-block:: yaml

        - kind: singleanalysis
          type: MWFrequencyDrift
          properties:
            parameters:
              kind: ratio
              output: dataset
          apply_to: speksim/
          result: mwfreq-ratio

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            parameters:
              tight_layout: true
            filename: mwfreq-ratio.pdf
          apply_to: mwfreq-ratio


    If you are only interested in the values of the maximum drift
    amplitude and maximum ratio, change the parameter ``output`` from
    "dataset" to "value".


    See Also
    --------
    trepr.analysis.MWFrequencyValues :
        Extract microwave frequency values recorded for each time trace.


    .. versionchanged:: 0.2
        New parameter ``output`` controlling output format and ``kind``
        controlling the kind of result. Fix with calculating the ratio.
        Renamed class from MwFreqAnalysis.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Microwave frequency drift analysis.'
        self.parameters['kind'] = 'ratio'
        self.parameters['output'] = 'value'
        # protected properties
        self._delta_mw_freq = float()
        self._delta_B0 = float()
        self._step_size_in_mT = float()
        self._ratio_frequency_drift_to_step_size = float()

    @staticmethod
    def applicable(dataset):
        """
        Check whether the processing step is applicable to the given dataset.

        To be able to perform a microwave frequency drift analysis,
        the values for the microwave frequency for each individual time
        trace need to be recorded and available from the dataset.
        """
        # noinspection PyUnresolvedReferences
        return dataset.microwave_frequency.data.any()

    def _sanitise_parameters(self):
        if self.parameters["output"] not in ['value', 'dict', 'dataset']:
            raise ValueError("Unknown output type %s"
                             % self.parameters["output"])
        if self.parameters["kind"] not in ['ratio', 'drift']:
            raise ValueError("Unknown kind %s"
                             % self.parameters["kind"])

    def _perform_task(self):
        """Perform all methods to do analysis."""
        self._calculate_mw_freq_amplitude()
        self._calculate_delta_B0()
        self._calculate_step_size()
        self._compare_delta_B0_with_step_size()
        self._write_result()

    def _calculate_mw_freq_amplitude(self):
        """Calculate the amplitude of the microwave frequency."""
        self._delta_mw_freq = max(self.dataset.microwave_frequency.data) - \
            min(self.dataset.microwave_frequency.data)

    # noinspection PyPep8Naming
    def _calculate_delta_B0(self):  # noqa: N802
        """Calculate delta B0 by using the resonance condition."""
        self._delta_B0 = self._GHz_to_mT(self._delta_mw_freq)

    # noinspection PyPep8Naming
    @staticmethod
    def _GHz_to_mT(frequency=None):  # noqa: N802
        electron_g_factor = scipy.constants.value('electron g factor')
        bohr_magneton = scipy.constants.value('Bohr magneton')
        planck_constant = scipy.constants.value('Planck constant')
        magnetic_field = frequency * 1e9 * planck_constant \
            / (-1 * electron_g_factor * bohr_magneton * 1e-3)
        return magnetic_field

    def _calculate_step_size(self):
        """Calculate the step size of the given dataset."""
        self._step_size_in_mT = \
            self.dataset.microwave_frequency.axes[0].values[1] \
            - self.dataset.microwave_frequency.axes[0].values[0]

    # noinspection PyPep8Naming
    def _compare_delta_B0_with_step_size(self):  # noqa: N802
        """Calculate the ratio between delta B0 and the step size."""
        self._ratio_frequency_drift_to_step_size = \
            self._delta_B0 / self._step_size_in_mT

    def _write_result(self):
        """Write the results in the results dictionary."""
        if self.parameters['output'] == 'value':
            if self.parameters['kind'] == 'ratio':
                self.result = self._ratio_frequency_drift_to_step_size
            elif self.parameters['kind'] == 'drift':
                self.result = self._delta_B0
        elif self.parameters['output'] == 'dataset':
            self.result = trepr.dataset.CalculatedDataset()
            self.result.data.data = self._GHz_to_mT(np.diff(
                self.dataset.microwave_frequency.data))
            self.result.data.axes[0].quantity = \
                self.dataset.microwave_frequency.axes[0].quantity
            self.result.data.axes[0].unit = \
                self.dataset.microwave_frequency.axes[0].unit
            self.result.data.axes[0].values = \
                self.dataset.microwave_frequency.axes[0].values[:-1] \
                + self._step_size_in_mT * 0.5
            self.result.data.axes[1].quantity = "drift"
            self.result.data.axes[1].unit = "mT"
            if self.parameters['kind'] == 'ratio':
                self.result.data.data /= self._step_size_in_mT
                self.result.data.axes[1].quantity = "drift/(field step size)"
                self.result.data.axes[1].unit = ""
        else:
            self.result = {
                'frequency drift': aspecd.metadata.PhysicalQuantity(
                    value=self._delta_B0, unit='mT'),
                'ratio frequency drift/step size':
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
        """Create matrix with time stamps and corresponding field points."""
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
        """Calculate the time between the time stamps."""
        zero = datetime.datetime(2018, 1, 1)
        for i in range(len(self._time_stamp_datetimes) - 1):
            self._time_stamp_datetimes[i] = \
                self._time_stamp_datetimes[i + 1] - \
                self._time_stamp_datetimes[i] + zero
        del self._time_stamp_datetimes[-1]
        zero = mdates.date2num(zero)
        for i in range(len(self._time_stamp_datetimes)):
            self._time_stamp_datetimes[i] = \
                mdates.date2num(self._time_stamp_datetimes[i]) - zero
        self._time_field_matrix = \
            np.delete(self._time_field_matrix, -1, axis=0)

    def _write_result(self):
        """Assign result.

        The result is assigned to :attr:`aspecd.analysis.AnalysisStep.result`.
        """
        self.result = {
            'time spent per time trace': self._time_stamp_datetimes}


class BasicCharacteristics(aspecd.analysis.BasicCharacteristics):
    # noinspection PyUnresolvedReferences
    r"""
    Extract basic characteristics of a dataset.

    This class extends the ASpecD class by the possibility to return axes
    values and indices for only one axis in case of *N*\ D datasets with
    *N*>1.

    Currently a workaround, the functionality may move upwards in the ASpecD
    framework eventually.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        Additionally to those from
        :class:`aspecd.analysis.BasicCharacteristics`, the following
        parameters are allowed:

        axis : :class:`int`
            Number of the axis to return the axes values or indices for.


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.parameters['axis'] = None

    def _sanitise_parameters(self):
        if self.parameters['axis'] > self.dataset.data.data.ndim - 1:
            raise IndexError("Axis %i out of bounds"
                             % self.parameters['axis'])

    def _perform_task(self):
        super()._perform_task()
        if self.parameters['axis'] is not None \
                and isinstance(self.result, list):
            self.result = self.result[self.parameters['axis']]


class MWFrequencyValues(aspecd.analysis.SingleAnalysisStep):
    """
    Extract microwave frequency values recorded for each time trace.

    tr-EPR measurements can take a rather long time, up to 12-24 hours,
    and the stability of the microwave frequency is not always guaranteed.
    Crucial here is that the frequency drift is small compared to the
    magnetic field step width.

    What does that mean practically? Using the resonance condition of
    magnetic resonance, one can convert magnetic field values in
    frequencies, and as a rule of thumb, 1 mT = 28 MHz. Therefore, if the
    microwave frequency drifted by < 1 MHz during the experiment, in most
    cases (except of experiments with very high field resolution) you
    should be safe and there is no reason to expect distortions of the
    spectra shape due to a drift in microwave frequency.

    Not all software used to record tr-EPR data does record the MW
    frequency for each individual time trace, though. Therefore,
    only those datasets containing the microwave frequency values can be
    analysed.

    The analysis step returns a calculated dataset with the magnetic field
    axis as the first axis and the microwave frequency values as data.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    If you have recorded a dataset containing microwave frequency values
    for each individual time trace and are interested in the drift of the
    microwave frequency, you can extract the microwave frequency values as
    function of the magnetic field as a calculated dataset:

    .. code-block:: yaml

        - kind: singleanalysis
          type: MWFrequencyValues
          result: mwfreq

    To plot the data contained in the newly obtained calculated dataset,
    simply proceed with a plotter of your choice:

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: mwfreq.pdf
          apply_to: mwfreq


    Don't be surprised if the drift seems not to be linear or even appears
    to be discontinuous. Depending on how you have recorded your data,
    *i.e.* what scheme of sampling the magnetic field axes you have used,
    this is perfectly normal.


    See Also
    --------
    trepr.analysis.MWFrequencyDrift :
        Calculate the frequency drift and compare it with the step size.


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = 'Extract MW frequency values'

    @staticmethod
    def applicable(dataset):
        """
        Check whether the processing step is applicable to the given dataset.

        To be able to extract the microwave frequency values for each
        individual time trace, these values need to be available from the
        dataset.
        """
        # noinspection PyUnresolvedReferences
        return dataset.microwave_frequency.data.any()

    def _perform_task(self):
        self.result = trepr.dataset.CalculatedDataset()
        self.result.data.data = self.dataset.microwave_frequency.data
        self.result.data.axes = self.dataset.microwave_frequency.axes
