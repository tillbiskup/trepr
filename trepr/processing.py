"""
Data processing functionality.

.. sidebar:: Processing *vs.* analysis steps

    The key difference between processing and analysis steps: While a
    processing step *modifies* the data of the dataset it operates on,
    an analysis step returns a result based on data of a dataset, but leaves
    the original dataset unchanged.


Key to reproducible science is automatic documentation of each processing
step applied to the data of a dataset. Each processing step is
self-contained, meaning it contains every necessary information to perform
the processing task on a given dataset.

Processing steps, in contrast to analysis steps (see :mod:`trepr.analysis`
for details), not only operate on data of a :class:`trepr.dataset.Dataset`,
but change its data. The information necessary to reproduce each processing
step gets added to the :attr:`trepr.dataset.Dataset.history` attribute of a
dataset.

Due to the inheritance from the :mod:`aspecd.processing` module, all processing
steps provided are fully self-documenting, *i.e.* they add all necessary
information to reproduce each processing step to the
:attr:`trepr.dataset.ExperimentalDataset.history` attribute of the dataset.


Concrete processing steps
=========================

This module provides a series of processing steps that can be divided into
those specific for tr-EPR data and those generally applicable to
spectroscopic data and directly inherited from the ASpecD framework.

What follows is a list as a first overview. For details, see the detailed
documentation of each of the classes, readily accessible by the link.


Processing steps specific for tr-EPR data
-----------------------------------------

A number of processing steps are rather specific for tr-EPR data namely
correcting DC offsets, background, and microwave frequency:

* :class:`PretriggerOffsetCompensation`

  Correct for DC offsets of tr-EPR data

* :class:`BackgroundCorrection`

  Subtract background, mainly laser-induced field-independent background

* :class:`FrequencyCorrection`

  Correct for same microwave frequency, necessary to compare measurements

* :class:`TriggerAutodetection`

  Automatically detect trigger position for time axis.


General processing steps contained in the ASpecD framework
----------------------------------------------------------

Besides the processing steps specific for tr-EPR data, all processing steps
of the underlying ASpecD framework are available. To list those most
relevant for tr-EPR spectroscopy:

* :class:`aspecd.processing.Normalisation`

  Normalise data.

  There are different kinds of normalising data: maximum, minimum,
  amplitude, area

* :class:`aspecd.processing.ScalarAlgebra`

  Perform scalar algebraic operation on one dataset.

  Operations available: add, subtract, multiply, divide (by given scalar)

* :class:`aspecd.processing.ScalarAxisAlgebra`

  Perform scalar algebraic operation on axis values of a dataset.

  Operations available: add, subtract, multiply, divide, power (by given scalar)

* :class:`aspecd.processing.DatasetAlgebra`

  Perform scalar algebraic operation on two datasets.

  Operations available: add, subtract

* :class:`aspecd.processing.Projection`

  Project data, *i.e.* reduce dimensions along one axis.

* :class:`aspecd.processing.SliceExtraction`

  Extract slice along one ore more dimensions from dataset.

* :class:`aspecd.processing.BaselineCorrection`

  Correct baseline of dataset.

* :class:`aspecd.processing.Averaging`

  Average data over given range along given axis.

* :class:`aspecd.processing.Filtering`

  Filter data


Implementing own processing steps is rather straight-forward. For details,
see the documentation of the :mod:`aspecd.processing` module.


Module documentation
====================

"""

import numpy as np

import aspecd.processing
import aspecd.exceptions


class PretriggerOffsetCompensation(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Correct for DC offsets of tr-EPR data.

    Usually the first processing step after recording tr-EPR data is to
    compensate for DC offsets due to experimental instabilities. This is
    done by setting the average of the pretrigger part of the time trace to
    zero (pretrigger offset compensation). At the same time, this will
    remove any background signals of stable paramagnetic species, as they
    would appear as DC offset as well.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        zeropoint_index : :class:`int`
            Index of the time axis corresponding to *t* = 0

            Will be automatically detected during processing.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the pretrigger offset compensation with
    default values:

    .. code-block:: yaml

       - kind: processing
         type: PretriggerOffsetCompensation

    This will correct your data accordingly and should always be the first
    step when processing and analysing tr-EPR data.

    """

    def __init__(self):
        super().__init__()
        # public properties:
        # Note: self.parameters inherited
        self.description = "Pretrigger offset compensation"
        self.undoable = True
        self.parameters["zeropoint_index"] = 0

    def _perform_task(self):
        """Perform the processing step and return the processed data."""
        self._get_zeropoint_index()
        self._execute_compensation(self.parameters["zeropoint_index"])

    def _get_zeropoint_index(self):
        """Get the index of the last time value before the trigger."""
        zeropoint_index = np.argmin(abs(self.dataset.data.axes[1].values))
        self.parameters["zeropoint_index"] = int(zeropoint_index)

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


class BackgroundCorrection(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Subtract background, mainly laser-induced field-independent background.

    When the laser hits the EPR cavity, this usually introduces a
    field-independent absorptive background signal that needs to be
    subtracted from the data.

    Depending on the spectrometer control and measurement software used,
    this background signal can get automatically subtracted already during
    the measurement. More often, it needs to be done afterwards,
    and therefore, it is crucial to record the tr-EPR data with sufficient
    baseline at both ends of the magnetic field range to allow for reliable
    background correction.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        num_profiles : :class:`list`
            Number of time profiles (transients) to use from lower and upper
            end of the magnetic field axis.

            If two values are provided, a linear regression will be
            performed between lower and upper end and the background
            subtracted accordingly. If only a scalar (or a list with one
            element) is provided, the background traces from the lower
            magnetic field position are used.

            Default: [5, 5]


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the background correction with default
    values:

    .. code-block:: yaml

       - kind: processing
         type: BackgroundCorrection

    This will correct your data accordingly.

    If you would like to control more carefully the transients (time profiles)
    used to obtain the background signal, you can set the respective
    parameters. Suppose you would want to use only the first 10 transients
    from the lower end of the magnetic field:

    .. code-block:: yaml

       - kind: processing
         type: BackgroundCorrection
         properties:
           parameters:
             num_profiles: 10

    Similarly, if you would want to use only the *last* 10 transients from the
    lower end of the magnetic field:

    .. code-block:: yaml

       - kind: processing
         type: BackgroundCorrection
         properties:
           parameters:
             num_profiles: -10

    And finally, if you would like to use the first 5 and the last 10
    transients, you would write:

    .. code-block:: yaml

       - kind: processing
         type: BackgroundCorrection
         properties:
           parameters:
             num_profiles: [5, 10]

    """

    def __init__(self):
        super().__init__()
        # public properties:
        self.description = "Background correction of 2D spectrum"
        self.undoable = True
        self.parameters["num_profiles"] = None

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Background correction is only applicable to 2D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
        return len(dataset.data.axes) == 3

    def _sanitise_parameters(self):
        if not isinstance(self.parameters["num_profiles"], list):
            self.parameters["num_profiles"] = [
                self.parameters["num_profiles"]
            ]
        if len(self.parameters["num_profiles"]) == 1:
            self.parameters["num_profiles"] = self.parameters["num_profiles"][
                0
            ]

    def _set_defaults(self):
        self.parameters["num_profiles"] = self.parameters["num_profiles"] or [
            5,
            5,
        ]

    def _perform_task(self):
        self._check_data_size()
        self._subtract_background()

    def _check_data_size(self):
        if isinstance(self.parameters["num_profiles"], list):
            num_profiles = sum(self.parameters["num_profiles"])
        else:
            num_profiles = self.parameters["num_profiles"]
        if len(self.dataset.data.axes[0].values) <= 2 * num_profiles:
            raise aspecd.exceptions.NotApplicableToDatasetError(
                message="The given dataset ist too small to perform "
                "appropriate background correction."
            )

    def _subtract_background(self):
        if (
            isinstance(self.parameters["num_profiles"], list)
            and len(self.parameters["num_profiles"]) == 2
        ):
            self._bg_corr_with_slope()
        else:
            self._bg_corr_one_side()

    def _bg_corr_with_slope(self):
        low = self.parameters["num_profiles"][0]
        high = abs(self.parameters["num_profiles"][1])
        lower_mean = np.mean(self.dataset.data.data[:low, :], axis=0)
        higher_mean = np.mean(self.dataset.data.data[-high:, :], axis=0)
        slope = (higher_mean - lower_mean) / self.dataset.data.data.shape[0]
        for idx, transient in enumerate(self.dataset.data.data):
            transient -= lower_mean + slope * idx

    def _bg_corr_one_side(self):
        assert isinstance(self.parameters["num_profiles"], int)

        if self.parameters["num_profiles"] < 0:
            self._subtract_from_end()
        else:
            self._subtract_from_begin()

    def _subtract_from_end(self):
        bg = np.mean(
            self.dataset.data.data[self.parameters["num_profiles"] :, :],
            axis=0,
        )
        self.dataset.data.data -= bg

    def _subtract_from_begin(self):
        bg = np.mean(
            self.dataset.data.data[: self.parameters["num_profiles"], :],
            axis=0,
        )
        self.dataset.data.data -= bg


class FrequencyCorrection(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Convert data to a given microwave frequency.

    To compare EPR spectra, it is necessary to first correct them for the
    same microwave frequency, *i.e.* to adjust the magnetic field axis
    accordingly. Note that each individual measurement will have its own
    microwave frequency. Particularly for tr-EPR data with their usually
    quite large steps of the magnetic field axis, one could first check
    whether the difference in microwave frequency is reasonably large
    compared to the magnetic field steps, and only in this case correct for
    the same frequency.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        frequency : :class:`float`
            Microwave frequency to correct for in GHz.

        Default: 9.5


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the frequency correction with default
    values:

    .. code-block:: yaml

       - kind: processing
         type: FrequencyCorrection

    This will correct your data accordingly.

    If you would like to set the target microwave frequency explicitly,
    this can be done as well:

    .. code-block:: yaml

       - kind: processing
         type: BackgroundCorrection
         properties:
           parameters:
             frequency: 9.8

    In this case, the data would be corrected for a microwave frequency of
    9.8 GHz.

    .. codeauthor:: Mirjam Schröder

    """

    def __init__(self):
        super().__init__()
        self.parameters["frequency"] = 9.5
        self.description = "Correct magnetic field axis for given frequency"

    def _perform_task(self):
        """Perform the actual transformation / correction.

        For the conversion the x axis data is first converted to an axis in
        units of using the given frequency, then converted back using target
        frequency.
        """
        nu_target = self.parameters["frequency"]
        for axis in self.dataset.data.axes:
            # TODO: Question: Better check for quantity rather than unit? (
            #   Difficult if not filled)
            # if axis.quantity == 'magnetic field'
            if axis.unit in ("mT", "G"):
                axis.values = self._correct_field_for_frequency(
                    nu_target, axis.values
                )
                self._write_new_frequency()

    def _correct_field_for_frequency(self, nu_target=None, b_initial=None):
        """
        Calculate new field axis for given frequency.

        Parameters
        ----------
        nu_target : :class:`float`
            Frequency the magnetic field should be computed for

        b_initial : :class:`numpy.ndarray`
            Original field axis

        Returns
        -------
        b_target : :class:`numpy.ndarray`
            Computed field axis

        """
        nu_initial = self.dataset.metadata.bridge.mw_frequency.value
        b_target = (nu_target / nu_initial) * b_initial
        return b_target

    def _write_new_frequency(self):
        self.dataset.metadata.bridge.mw_frequency.value = self.parameters[
            "frequency"
        ]


class TriggerAutodetection(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Automatically detect trigger position for time axis.

    Depending on the setup used for recording tr-EPR data, either the
    trigger position (*i.e.* index of the zero value of the time axis) is
    set directly in the transient recorder, or it is not set at all (in
    case the start of recording data of the transient recorder can not be
    set to times prior to the trigger pulse).

    However, a valid trigger position is a prerequisite for pretrigger
    offset compensation (via :class:`PregriggerOffsetCompensation`).
    Therefore, in cases no pretrigger has been set, automatically
    detecting this position would be helpful.

    .. note::

        Auto-detecting the trigger position depends on the statistics of
        the time trace used. Hence the position will never be the same as
        if you synchronise it to the laser pulse (or flash lamp trigger,
        or else). Nevertheless, keep in mind that even in case of
        triggering the transient recorder by the laser flash detected by a
        fast photodiode, signal travel time within your cables will be in
        the range of tens of nanoseconds (for both, the cable connecting
        the photodiode with the recorder as well as for the signal path
        within the EPR bridge). Therefore, trigger positions are always
        somewhat arbitrary and can never be used to obtain accurate delays
        between laser flash and raise/maximum of the tr-EPR signal.

    .. important::

        If you try to auto-detect the trigger position, do *not* perform a
        background subtraction (via :class:`BackgroundCorrection`) before,
        as this will remove the laser background signal used to
        auto-detect the trigger position.

    Notes
    -----
    Automatically detecting the trigger position relies on a number of
    assumptions regarding the shape of a time trace and the underlying
    statistics:

    * The time trace should be dominated by the laser-induced background
      resulting in an absorptive signal or otherwise have an absorptive
      signal.

    * The time trace needs to be recorded starting *before* the actual
      laser flash and hence the signal raise. Currently, at least 50
      points need to be recorded *before* the actual laser flash.

    * The trigger position is the position of the time trace where the
      signal (positively) deviates by a threshold from the value before.

    In case of two-dimensional data, the first time trace will be used to
    detect the trigger position.

    The algorithm used for auto-detecting the trigger position works
    basically as follows:

    * Compute differences of adjacent points of the time trace

    * Smooth the differences by applying a boxcar filter

    * Obtain the first point where the difference is larger than a given
      threshold

    The window length used for smoothing is set to 1/20 of the length of
    the time trace, and the threshold is computed as the standard
    deviation of the first 50 points of the time trace multiplied by a
    factor (``n_sigma``) that can be set (for details, see below).


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        n_sigma : :class:`int` or :class:`float`
            Threshold used to detect the raise of the signal.

            The trigger position is detected by obtaining the first point
            of the smoothed differences of the time trace whose value is
            above a threshold. This threshold is calculated as *n* times
            the standard deviation (sigma).

            Default: 4


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Suppose you have recorded a tr-EPR dataset with a setup that does not
    allow to set the trigger position to somewhere near the actual laser
    flash. In this case, you will end up with a time axis starting at
    zero. To perform steps such as pretrigger offset compensation (via
    :class:`PretriggerOffetCompensation`), you need to set the trigger
    position first. Automatically detecting the trigger position and
    afterwards performing the routine processing steps for tr-EPR data may
    look like this:

    .. code-block:: yaml

        - kind: processing
          type: TriggerAutodetection
        - kind: processing
          type: PretriggerOffsetCompensation
        - kind: processing
          type: BackgroundCorrection
        - kind: singleplot
          type: SinglePlotter2D
          properties:
            filename: overview_poc_bgc.pdf

    If you like to adjust parameters, simply provide them in the recipe:

    .. code-block:: yaml

        - kind: processing
          type: TriggerAutodetection
          properties:
            parameters:
              n_sigma: 3

    In this case, the threshold would be set to 3 times the standard
    deviation (sigma). Note that you are not limited to integer values,
    but can give floats as well here.


    .. versionadded:: 0.2

    """

    def __init__(self):
        super().__init__()
        self.description = "Autodetect trigger position"
        self.parameters["n_sigma"] = 4

    @staticmethod
    def applicable(dataset):
        """
        Check whether the processing step is applicable to the dataset.

        Trigger autodetection is only possible if the first axis (in case
        of 1D data) or the second axis (in case of 2D data) is a time axis.
        """
        if len(dataset.data.axes) == 2:
            answer = "time" in dataset.data.axes[0].quantity
        else:
            answer = "time" in dataset.data.axes[1].quantity
        return answer

    def _perform_task(self):
        if len(self.dataset.data.axes) > 2:
            time_trace = self.dataset.data.data[0, :]
        else:
            time_trace = self.dataset.data.data
        smoothed_differences = np.convolve(
            np.diff(time_trace), np.ones(int(len(time_trace) / 20))
        )
        try:
            threshold = (
                np.std(smoothed_differences[0:50])
                * self.parameters["n_sigma"]
            )
            trigger_pos = np.where(smoothed_differences > threshold)[0][0]
        except IndexError:
            trigger_pos = 0
        self.dataset.metadata.transient.trigger_position = trigger_pos
        for axis in self.dataset.data.axes:
            if "time" in axis.quantity:
                axis.values -= axis.values[trigger_pos]
