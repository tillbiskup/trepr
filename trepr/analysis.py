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


Concrete analysis steps
=======================

Due to inheritance from the :mod:`aspecd.analysis` module all analysis
steps defined there are available from within the trepr package.
Furthermore, a number of **analysis steps specific for tr-EPR spectroscopy**
have been implemented here:

* :class:`MWFrequencyDrift`

  Calculate the frequency drift and compare it with the step size.

* :class:`MWFrequencyValues`

  Extract microwave frequency values recorded for each time trace.

* :class:`TimeStampAnalysis`

  Calculate the time spent for recording each time trace.

* :class:`TransientNutationFFT`

  Perform FFT to extract transient nutation frequencies.


And the following classes have been extended with respect to the
functionality available from the ASpecD classes:

* :class:`BasicCharacteristics`

  Extract basic characteristics of a dataset.


Module documentation
====================

"""
import copy

import numpy as np
import scipy.constants
from scipy.fft import rfft, rfftfreq
from scipy.optimize import curve_fit
from scipy.signal import windows

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

    This requires the software used to record the tr-EPR data to save the
    microwave frequency value for each individual time trace. As often,
    tr-EPR spectra are recorded using individual software, this is merely a
    design question of the program.

    Different outputs, *e.g.* a scalar value or a calculated dataset, are
    available, for details see below.


    Attributes
    ----------
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
            Kind of output: value, dict. or dataset

            Valid values are "value" (default), "dataset", and "dict".
            Usually, only values and datasets can be easily used within a
            recipe.

            Default: "value"

    result : :class:`float`, :class:`dict`, or :class:`aspecd.dataset.CalculatedDataset`
        Results of the microwave frequency drift analysis.

        Depending on the output option set via the "output" parameter,
        either a scalar value (ratio or drift), , a dict containing both
        values, or a dataset containing either the ratios or the drifts as
        function of the magnetic field.

        In case of datasets, note that due to calculating a difference
        between microwave frequency points, the size of the data is -1
        compared to the size of the original microwave frequency values.


    .. note::

        If you set the output to "dataset", you will get a field axis with
        values centred between the original field values, as the microwave
        frequency drift analysis requires to calculate differences between
        points, hence returning vectors with one element less than the
        original vector.


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
            self.result = self.create_dataset()
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
    # noinspection PyUnresolvedReferences
    """
    Calculate the time spent for recording each time trace.

    Can be helpful for debugging the spectrometer and for assessing
    whether delays during data acquisition are responsible for artifacts
    in a recorded dataset.

    This requires the software used to record the tr-EPR data to save the
    time stamp for each individual time trace. As often, tr-EPR spectra
    are recorded using individual software, this is merely a design
    question of the program.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        kind : :class:`str`
            Kind of characteristic to extract from the data

            Valid values are "delta" and "time".

            In case of "delta", the time difference (delta) in seconds
            between adjacent magnetic field points will be returned,
            in case of "time", the time (in seconds) for each time trace
            since start of the measurement will be returned.

            Default: "delta"

        output : :class:`str`
            Kind of output: value, dict. or dataset

            Valid values are "value" (default), "dataset", and "dict".
            Usually, only values and datasets can be easily used within a
            recipe.

            Default: "value"

    result : :class:`float`  or :class:`aspecd.dataset.CalculatedDataset`
        Results of the microwave frequency drift analysis.

        Depending on the output option set via the "output" parameter,
        either a scalar value (ratio or drift), , a dict containing both
        values, or a dataset containing either the ratios or the drifts as
        function of the magnetic field.

        In case of datasets, note that due to calculating a difference
        between microwave frequency points, the size of the data is -1
        compared to the size of the original microwave frequency values.


    .. note::

        If you set the output to "dataset" and the kind to "delta", you will
        get a field axis with one value less than the original field axis,
        as the analysis requires to calculate differences between points,
        hence returning vectors with one element less than the original
        vector.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    If you have recorded a dataset containing time stamps for each
    individual time trace and are interested in the time spent between
    adjacent magnetic field points, you can obtain a calculated dataset with
    the values and plot the results:

    .. code-block:: yaml

        - kind: singleanalysis
          type: TimeStampAnalysis
          properties:
            parameters:
              kind: delta
              output: dataset
          result: time-delta

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            parameters:
              tight_layout: true
            filename: time-delta.pdf
          apply_to: time-delta


    Please note that depending on the mode of measurement you will get
    different times between adjacent field points. In case of a background
    signal regularly recorded every *n*-th trace during measurement,
    you will regularly see about twice the time spent, and if you do not
    record linearly (up or down), but inward or outward with respect to
    the magnetic field axis, this will be reflected in the time deltas as
    well.

    Sometimes you may be interested in the relative times rather than the
    time deltas. This can be achieved similarly to the example above.
    Simply change "kind" from "delta" to "time":

    .. code-block:: yaml

        - kind: singleanalysis
          type: TimeStampAnalysis
          properties:
            parameters:
              kind: time
              output: dataset
          result: time-values

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            parameters:
              tight_layout: true
            properties:
              drawing:
                marker: '*'
            filename: time-values.pdf
          apply_to: time-values


    To better see the individual time points, here, additional markers are
    added to the plot. In case of outward measurement scheme, you will see a
    v-shaped result.


    .. versionchanged:: 0.2
        New parameter ``output`` controlling output format. Returns time
        deltas in seconds.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Time stamp analysis.'
        self.parameters['output'] = 'dataset'
        self.parameters['kind'] = 'delta'

    @staticmethod
    def applicable(dataset):
        """
        Check whether the processing step is applicable to the given dataset.

        To be able to perform a time stamp analysis, time stamps need to
        be available for each individual time trace of the dataset.
        """
        # noinspection PyUnresolvedReferences
        return dataset.time_stamp.data.any()

    def _sanitise_parameters(self):
        if self.parameters["output"] not in ['values', 'dataset']:
            raise ValueError("Unknown output type %s"
                             % self.parameters["output"])
        if self.parameters["kind"] not in ['delta', 'time']:
            raise ValueError("Unknown kind %s"
                             % self.parameters["kind"])

    def _perform_task(self):
        """Perform all methods to do analysis."""
        time_deltas = np.diff(self.dataset.time_stamp.data)
        time_deltas_in_seconds = [abs(x.total_seconds()) for x in time_deltas]
        times = [time.total_seconds() for time in
                 self.dataset.time_stamp.data
                 - min(self.dataset.time_stamp.data)]
        if self.parameters['output'] == 'dataset':
            self.result = self.create_dataset()
            if self.parameters['kind'] == 'delta':
                self.result.data.data = np.asarray(time_deltas_in_seconds)
                self.result.data.axes[0].values = \
                    self.dataset.time_stamp.axes[0].values[1:]
                self.result.data.axes[1].quantity = 'Delta time'
            elif self.parameters['kind'] == 'time':
                self.result.data.data = np.asarray(times)
                self.result.data.axes[0].values = \
                    self.dataset.time_stamp.axes[0].values
                self.result.data.axes[1].quantity = 'time'
            self.result.data.axes[0].quantity = \
                self.dataset.time_stamp.axes[0].quantity
            self.result.data.axes[0].unit = \
                self.dataset.time_stamp.axes[0].unit
            self.result.data.axes[1].unit = 's'
        else:
            if self.parameters['kind'] == 'delta':
                self.result = time_deltas_in_seconds
            elif self.parameters['kind'] == 'time':
                self.result = times


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


class TransientNutationFFT(aspecd.analysis.SingleAnalysisStep):
    # noinspection PyUnresolvedReferences
    """
    Perform FFT to extract transient nutation frequencies.

    A tr-EPR time trace showing transient nutations can be described by a
    zero-order Bessel function of first kind. Due to relaxation, the Bessel
    function is damped with an exponential.

    One way to extract the transient nutation frequencies is to perform a 1D
    discrete Fourier transform (using the FFT algorithm) along the time
    axis. In case of 2D datasets, this means to perform the FFT for each
    time trace individually.

    In any case, the analysis step will return a calculated dataset with the
    data representing the FFT for all time traces. Here, the ``nfft`` function
    from :mod:`scipy.fft` gets used.

    In case the time trace has been recorded for negative times
    (pre-trigger), the FFT will only be performed starting at *t* = 0.

    Generally, if full time traces including the raising flank are analysed,
    it is best to cut the time traces from the left up to the extremum
    (maximum of the absolute value) to suppress low-frequency background of
    the resulting FT. This is the default behaviour and can be controlled
    using the ``start_in_extremum`` parameter (see below). In case of 2D
    datasets, the global extremum will be used for all time traces.

    As long as the oscillation clearly dominates the time trace(s), *i.e.*
    the signal intensity crossing the zero line multiple times, there should
    be no need for further preprocessing. Things are different, however,
    if the time trace is dominated by an exponential decay and the
    oscillation merely modulates this decay. In this case, you will usually
    need to subtract the exponential decay from the data to obtain
    meaningful results from the FFT.

    As a side note: An alternative way to analyse transient nutations would
    be to fit a damped Bessel function of first kind to the data. Thus one
    can extract both, frequency and relaxation rate directly from the data.
    Note, however, that this will only be possible if the oscillation
    clearly dominates the time trace. In cases where the oscillation merely
    resides on top of a dominating exponential decay, this will typically
    not be possible.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        start_in_extremum : :class:`bool`
            Whether to cut the time trace(s) from the left at the extremum.

            Extremum here means the maximum of the absolute values of the
            data of the dataset.

            Default: True

        padding : :class:`int`
            Factor the original length of the time trace used for FFT should
            be elongated and padded with zeros ("zero filling").

            Usually, to reasonably resolve lower frequencies, a factor of
            3--5 is useful.

            Default: 1

        subtract_decay : :class:`bool`
            Whether to subtract a fitted exponential decay from each time trace.

            Sometimes the time trace is dominated by an exponential decay
            rather than the transient nutation, *i.e.* the nutation appears
            as modulation *on top* of an exponential decay. In this case,
            the FFT will usually not allow for reliably extracting the
            nutation frequencies, due to a huge background at the
            low-frequency end.

            In this case, fitting and afterwards subtracting an exponential
            decay from each time trace helps a lot. As usually the exact
            form and parameters of the exponential decay are not known,
            here, an exponential decay with two parameters in the form
            ``f(x) = a * exp(-b * t)`` gets used. While leading to quite
            reliable results in the FFT, the fitted parameters can usually
            *not* be interpreted.

            Default: False

        window : :class:`str`
            Name of the window for apodisation of the data.

            Windows are often applied to the signal before Fourier transform
            to suppress artifacts (side lobes). Note, however, that applying
            windows might shift your frequencies, particularly in the
            low-frequency range, towards higher frequency. Therefore,
            it is always good to compare non-windowed and windowed signals
            if you need to extract reliable nutation frequencies from your data.

            All types of windows supported by :mod:`scipy.signal.windows`
            can be used. See there for further details. If a window requires
            additional parameters, use the parameter ``window_parameters``.
            For details, see below.

            Internally, the function :func:`scipy.signal.windows.get_window`
            is used to obtain the respective window. Note that only the
            right half of the (symmetric) window is applied to the data.

            Default: None

        window_parameters : :class:`float` or :class:`list`
            Parameters used for the window for apodising the data.

            For details of data apodisation, see above.

            Default: None



    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In its simplest form, you just apply the analysis step to a dataset and
    assign it to a result:

    .. code-block:: yaml

        - kind: singleanalysis
          type: TransientNutationFFT
          result: fft

    To plot the data contained in the newly obtained calculated dataset,
    simply proceed with a plotter of your choice (in this case for a 1D
    dataset):

    .. code-block:: yaml

        - kind: singleplot
          type: SinglePlotter1D
          properties:
            filename: fft.pdf
          apply_to: fft


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = \
            'Perform FFT to extract transient nutation frequencies'
        self.parameters['start_in_extremum'] = True
        self.parameters['padding'] = 1
        self.parameters['subtract_decay'] = False
        self.parameters['window'] = None
        self.parameters['window_parameters'] = None

        self._time_axis = 0
        self._cut_index = 0
        self._n_points = 0
        self._xt = None
        self._y = None

    @staticmethod
    def applicable(dataset):
        """
        Check whether the processing step is applicable to the given dataset.

        To be able to analyse transient nutations, a time axis needs to be
        present.
        """
        return any(['time' in axis.quantity for axis in dataset.data.axes])

    def _perform_task(self):
        self.result = self.create_dataset()

        self._get_time_axis()
        self._get_cut_index()
        self._apply_padding()
        self._cut_data()

        if self.parameters['subtract_decay']:
            self._subtract_decay()

        if self.parameters['window']:
            self._apply_window()

        self._perform_fft()
        self._assign_result_axes()

    def _get_time_axis(self):
        for idx, axis in enumerate(self.dataset.data.axes):
            if 'time' in axis.quantity:
                self._time_axis = idx

    def _get_cut_index(self):
        if self.parameters['start_in_extremum']:
            self._cut_index = np.argmax(np.abs(self.dataset.data.data)) % \
                              self.dataset.data.data.shape[self._time_axis]
        else:
            self._cut_index = np.argmin(np.abs(self.dataset.data.axes[
                                                   self._time_axis].values))

    def _apply_padding(self):
        if self.dataset.data.data.ndim > 1:
            self._n_points = \
                self.dataset.data.data[:, self._cut_index:].shape[1] \
                * self.parameters['padding']
        else:
            self._n_points = \
                self.dataset.data.data[self._cut_index:].shape[0] \
                * self.parameters['padding']

    def _cut_data(self):
        if self.dataset.data.data.ndim > 1:
            self._y = copy.copy(self.dataset.data.data[:, self._cut_index:])
        else:
            self._y = copy.copy(self.dataset.data.data[self._cut_index:])

    def _subtract_decay(self):

        def mono_exponential(x, a, t):
            return a * np.exp(-t * x)

        start_parameters = (1, 1)
        time_values = \
            self.dataset.data.axes[self._time_axis].values[self._cut_index:]

        if self.dataset.data.data.ndim > 1:
            for idx, row in enumerate(self._y):
                fitted_parameters, cv = curve_fit(mono_exponential,
                                                  time_values,
                                                  row,
                                                  start_parameters)
                self._y[idx, :] = row - mono_exponential(time_values,
                                                        *fitted_parameters)
        else:
            fitted_parameters, cv = curve_fit(mono_exponential,
                                              time_values,
                                              self._y,
                                              start_parameters)
            self._y -= mono_exponential(time_values, *fitted_parameters)

    def _apply_window(self):
        if self.parameters['window_parameters']:
            if aspecd.utils.isiterable(self.parameters['window_parameters']):
                window_name = (self.parameters['window'],
                               *self.parameters['window_parameters'])
            else:
                window_name = (self.parameters['window'],
                               self.parameters['window_parameters'])
        else:
            window_name = self.parameters['window']

        if self.dataset.data.data.ndim > 1:
            for idx, row in enumerate(self._y):
                window = windows.get_window(window_name,
                                            len(row) * 2)[len(row):]
                self._y[idx, :] *= window
        else:
            window = windows.get_window(window_name,
                                        len(self._y) * 2)[len(self._y):]
            self._y *= window

    def _perform_fft(self):
        self._xt = rfftfreq(
            self._n_points,
            float(np.diff(self.dataset.data.axes[self._time_axis].values[-2:])))
        yt = rfft(self._y, axis=self._time_axis, n=self._n_points)
        self.result.data.data = np.abs(yt)

    def _assign_result_axes(self):
        if self.dataset.data.data.ndim > 1:
            for idx in range(len(self.result.data.axes)):
                if idx != self._time_axis:
                    self.result.data.axes[idx] = self.dataset.data.axes[idx]
        self.result.data.axes[self._time_axis].values = self._xt
        self.result.data.axes[self._time_axis].quantity = 'frequency'
        self.result.data.axes[self._time_axis].unit = 'Hz'
        self.result.data.axes[-1].unit = ''
