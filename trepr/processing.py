"""
Data processing functionality.

.. sidebar:: Processing vs. analysis steps

    The key difference between processing and analysis steps: While a
    processing step *modifies* the data of the dataset it operates on,
    an analysis step returns a result based on data of a dataset, but leaves
    the original dataset unchanged.


Key to reproducible science is automatic documentation of each processing
step applied to the data of a dataset. Such a processing step each is
self-contained, meaning it contains every necessary information to perform
the processing task on a given dataset.

Processing steps, in contrast to analysis steps (see :mod:`trepr.analysis`
for details), not only operate on data of a :class:`trepr.dataset.Dataset`,
but change its data. The information necessary to reproduce each processing
step gets added to the :attr:`trepr.dataset.Dataset.history` attribute of a
dataset.

Due to the inheritance from the :mod:`aspecd.processing` module, all processing
steps provided are fully self-documenting, i.e. they add all necessary
information to reproduce each processing step to the
:attr:`trepr.dataset.Dataset.history` attribute of the dataset.


Concrete processing steps
=========================

This module provides a series of processing steps that can be divided into
those specific for TREPR data and those generally applicable to
spectroscopic data and directly inherited from the ASpecD framwork.

What follows is a list as a first overview. For details, see the detailed
documentation of each of the classes, readily accessible by the link.


Processing steps specific for TREPR data
----------------------------------------

A number of processing steps are rather specific for TREPR data namely
correcting DC offsets, background, and microwave frequency:

* :class:`PretriggerOffsetCompensation`

  Correct for DC offsets of TREPR data

* :class:`BackgroundCorrection`

  Subtract background, mainly laser-induced field-independent background

* :class:`FrequencyCorrection`

  Correct for same microwave frequency, necessary to compare measurements


General processing steps inherited from the ASpecD framework
------------------------------------------------------------

Besides the processing steps specific for TREPR data, a number of further
processing steps that are generally applicable to spectroscopic data have
been inherited from the underlying ASpecD framework:

* :class:`Normalisation`

  Normalise data.

  There are different kinds of normalising data: maximum, minimum,
  amplitude, area

* :class:`ScalarAlgebra`

  Perform scalar algebraic operation on one dataset.

  Operations available: add, subtract, multiply, divide (by given scalar)

* :class:`ScalarAxisAlgebra`

  Perform scalar algebraic operation on axis values of a dataset.

  Operations available: add, subtract, multiply, divide, power (by given scalar)

* :class:`DatasetAlgebra`

  Perform scalar algebraic operation on two datasets.

  Operations available: add, subtract

* :class:`Projection`

  Project data, *i.e.* reduce dimensions along one axis.

* :class:`SliceExtraction`

  Extract slice along one ore more dimensions from dataset.

* :class:`BaselineCorrection`

  Correct baseline of dataset.

* :class:`Averaging`

  Average data over given range along given axis.

* :class:`Filtering`

  Filter data


Further processing steps implemented in the ASpecD framework can be used as
well, by importing the respective modules. In case of recipe-driven data
analysis, simply prefix the kind with ``aspecd``:

.. code-block:: yaml

    - kind: aspecd.processing
      type: <ClassNameOfProcessingStep>


Implementing own processing steps is rather straight-forward. For details,
see the documentation of the :mod:`aspecd.processing` module.

Module documentation
====================

"""
import numpy as np
import scipy.signal

import aspecd.processing
import aspecd.exceptions

import trepr.exceptions


class PretriggerOffsetCompensation(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """
    Correct for DC offsets of TREPR data.

    Usually the first processing step after recording TREPR data is to
    compensate for DC offsets due to experimental instabilities. This is
    done by setting the average of the pretrigger part of the time trace to
    zero (pretrigger offset compensation). At the same time, this will
    remove any background signals of stable paramangetic species, as they
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
    step when processing and analysing TREPR data.

    """

    def __init__(self):
        super().__init__()
        # public properties:
        # Note: self.parameters inherited
        self.description = 'Pretrigger offset compensation'
        self.undoable = True
        self.parameters['zeropoint_index'] = 0

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
    and therefore, it is crucial to record the TREPR data with sufficient
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
        self.description = 'Background correction of 2D spectrum'
        self.undoable = True
        self.parameters['num_profiles'] = [5, 5]

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
        if not isinstance(self.parameters['num_profiles'], list):
            self.parameters['num_profiles'] = \
                list(self.parameters['num_profiles'])
        if len(self.parameters['num_profiles']) == 1:
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
        print("### From both sides")
        low = self.parameters['num_profiles'][0]
        high = abs(self.parameters['num_profiles'][1])
        lower_mean = np.mean(self.dataset.data.data[:low, :], axis=0)
        higher_mean = np.mean(self.dataset.data.data[-high:, :], axis=0)
        slope = (higher_mean - lower_mean) / self.dataset.data.data.shape[0]
        for idx, transient in enumerate(self.dataset.data.data):
            transient -= lower_mean + slope * idx

    def _bg_corr_one_side(self):
        assert isinstance(self.parameters['num_profiles'], int)

        if self.parameters['num_profiles'] < 0:
            self._subtract_from_end()
        else:
            self._subtract_from_begin()

    def _subtract_from_end(self):
        print("### From end")
        bg = np.mean(
            self.dataset.data.data[self.parameters['num_profiles']:, :],
            axis=0
        )
        self.dataset.data.data -= bg

    def _subtract_from_begin(self):
        print("### From begin")
        bg = np.mean(
            self.dataset.data.data[:self.parameters['num_profiles'], :],
            axis=0
        )
        self.dataset.data.data -= bg


class FrequencyCorrection(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
    """Convert data to a given microwave frequency.

    To compare EPR spectra, it is necessary to first correct them for the
    same microwave frequency, *i.e.* to adjust the magnetic field axis
    accordingly. Note that each individual measurement will have its own
    microwave frequency. Particularly for TREPR data with their usually
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
        nu_target = self.parameters['frequency']
        for axis in self.dataset.data.axes:
            # TODO: Question: Better check for quantity rather than unit? (
            #   Difficult if not filled)
            # if axis.quantity == 'magnetic field'
            if axis.unit in ('mT', 'G'):
                axis.values = self._correct_field_for_frequency(nu_target,
                                                                axis.values)
                self._write_new_frequency()

    def _correct_field_for_frequency(self, nu_target=None,
                                     b_initial=None):
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
        self.dataset.metadata.bridge.mw_frequency.value = \
            self.parameters['frequency']


class Normalisation(aspecd.processing.Normalisation):
    """Normalise data.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.Normalisation`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the normalisation with default values:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation

    This will normalise your data to their maximum.

    Sometimes, normalising to maximum is not what you need, hence you can
    control in more detail the criterion using the appropriate parameter:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             kind: amplitude

    In this case, you would normalise to the amplitude, meaning setting the
    difference between minimum and maximum to one. For other kinds, see above.

    If you want to normalise not over the entire range of the dataset,
    but only over a dedicated range, simply provide the necessary parameters:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range: [50, 150]

    In this case, we assume a 1D dataset and use indices, requiring the data
    to span at least over 150 points. Of course, it is often more convenient
    to provide axis units. Here you go:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range: [340, 350]
             range_unit: axis

    And in case of ND datasets with N>1, make sure to provide as many ranges
    as dimensions of your dataset, in case of a 2D dataset:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             range:
               - [50, 150]
               - [30, 40]

    Here as well, the range can be given in indices or axis units,
    but defaults to indices if no unit is explicitly given.

    """


class ScalarAlgebra(aspecd.processing.ScalarAlgebra):
    """Perform scalar algebraic operation on one dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.ScalarAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAlgebra
         properties:
           parameters:
             kind: add
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", or "divide" as kind - resulting in the given algebraic
    operation.

    """


class ScalarAxisAlgebra(aspecd.processing.ScalarAxisAlgebra):
    """Perform scalar algebraic operation on the axis of a dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.ScalarAxisAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to the first axis
    (index 0) your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAxisAlgebra
         properties:
           parameters:
             kind: plus
             axis: 0
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", "divide", and "power" as kind - resulting in the given
    algebraic operation.

    """


class DatasetAlgebra(aspecd.processing.DatasetAlgebra):
    """Perform scalar algebraic operation on two datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.DatasetAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add the data of the dataset referred to by its
    label ``label_to_other_dataset`` to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset

    Similarly, you could use "minus", "add", "subtract" as kind - resulting
    in the given algebraic operation.

    As mentioned already, the data of both datasets need to have identical
    shape, and comparison is only meaningful if the axes are compatible as
    well. Hence, you will usually want to perform a CommonRangeExtraction
    processing step before doing algebra with two datasets:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction
         results:
           - label_to_dataset
           - label_to_other_dataset

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset
         apply_to:
           - label_to_dataset

    """


class Projection(aspecd.processing.Projection):
    """Project data, *i.e.* reduce dimensions along one axis.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.Projection`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the projection with default values:

    .. code-block:: yaml

       - kind: processing
         type: Projection

    This will project the data along the first axis (index 0), yielding a 1D
    dataset.

    If you would like to project along the second axis (index 1), simply set
    the appropriate parameter:

    .. code-block:: yaml

       - kind: processing
         type: Projection
         properties:
           parameters:
             axis: 1

    This will project the data along the second axis (index 1), yielding a 1D
    dataset.

    """


class SliceExtraction(aspecd.processing.SliceExtraction):
    """Extract slice along one ore more dimensions from dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.SliceExtraction`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the slice extraction with an index only:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5

    This will extract the sixth slice (index five) along the first axis (index
    zero).

    If you would like to extract a slice along the second axis (with index
    one), simply provide both parameters, index and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5
             axis: 1

    This will extract the sixth slice along the second axis.

    And as it is sometimes more convenient to give ranges in axis values
    rather than indices, even this is possible. Suppose the axis you would
    like to extract a slice from runs from 340 to 350 and you would like to
    extract the slice corresponding to 343:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 343
             unit: axis

    In case of you providing the range in axis units rather than indices,
    the value closest to the actual axis value will be chosen automatically.

    For ND datasets with N>2, you can either extract a 1D or ND slice,
    with N always at least one dimension less than the original data. To
    extract a 2D slice from a 3D dataset, simply proceed as above, providing
    one value each for position and axis. If, however, you want to extract a
    1D slice from a 3D dataset, you need to provide two values each for
    position and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: [21, 42]
             axis: [0, 2]

    This particular case would be equivalent to ``data[21, :, 42]`` assuming
    ``data`` to contain the numeric data, besides, of course, that the
    processing step takes care of removing the axes as well.

    """


class BaselineCorrection(aspecd.processing.BaselineCorrection):
    """Subtract baseline from dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.BaselineCorrection`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the baseline correction with default
    values:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection

    In this case, a zeroth-order polynomial baseline will be subtracted from
    your dataset using ten percent to the left and right, and in case of a
    2D dataset, the baseline correction will be performed along the first
    axis (index zero) for all indices of the second axis (index 1).

    Of course, often you want to control a little bit more how the baseline
    will be corrected. This can be done by explicitly setting some parameters.

    Suppose you want to perform a baseline correction with a polynomial of
    first order:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             order: 1

    If you want to change the (percental) area used for fitting the
    baseline, and even specify different ranges left and right:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             fit_area: [5, 20]

    Here, five percent from the left and 20 percent from the right are used.

    Finally, suppose you have a 2D dataset and want to average along the
    second axis (index one):

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             axis: 1

    Of course, you can combine the different options.

    """


class Filtering(aspecd.processing.Filtering):
    """Filter data.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.Filtering`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally, filtering requires to provide both, a type of filter and a
    window length. Therefore, for uniform and Gaussian filters, this would be:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: uniform
             window_length: 10

    Of course, at least uniform filtering (also known as boxcar or moving
    average) is strongly discouraged due to the artifacts introduced.
    Probably the best bet for applying a filter to smooth your data is the
    Savitzky-Golay filter:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: savitzky-golay
             window_length: 10
             order: 3

    Note that for this filter, you need to provide the polynomial order as
    well. To get best results, you will need to experiment with the
    parameters a bit.

    """


class Averaging(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
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
    trepr.exceptions.DimensionError
        Raised if dimension is not in [0, 1].

    trepr.exceptions.UnitError
        Raised if unit is not in ['axis', 'index'].

    trepr.exceptions.RangeError
        Raised if range is not within axis.


    .. deprecated:: 0.1
        Use :class:`aspecd.processing.Averaging` instead.

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
            raise trepr.exceptions.DimensionError(
                'Wrong dimension. Choose 0 or 1.')
        if self.parameters['unit'] not in ['index', 'axis']:
            raise trepr.exceptions.UnitError(
                'Wrong unit. Choose "axis" or "index".')
        if self.parameters['unit'] == 'index':
            if self.parameters['range'][0] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
                raise trepr.exceptions.RangeError('Lower index out of range.')
            if self.parameters['range'][1] not in \
                    range(len(self.dataset.data.axes[self._dim].values)):
                raise trepr.exceptions.RangeError('Upper index out of range.')
        if self.parameters['unit'] == 'axis':
            if not self._value_within_vector_range(
                    self.parameters['range'][0],
                    self.dataset.data.axes[self._dim].values):
                raise trepr.exceptions.RangeError('Lower value out of range.')
            if not self._value_within_vector_range(
                    self.parameters['range'][1],
                    self.dataset.data.axes[self._dim].values):
                raise trepr.exceptions.RangeError('Upper value out of range.')
        if self.parameters['range'][1] < self.parameters['range'][0]:
            raise trepr.exceptions.RangeError('Values need to be ascending.')

    @staticmethod
    def _value_within_vector_range(value, vector):
        return np.amin(vector) <= value <= np.amax(vector)


class Filter(aspecd.processing.SingleProcessingStep):
    # noinspection PyUnresolvedReferences
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


    .. deprecated:: 0.1
        Use :class:`Filtering` instead.

    """

    def __init__(self):
        super().__init__()
        self.description = 'Filter 1D dataset.'
        self.parameters['type'] = 'savitzky-golay'
        self.parameters['window_width'] = None
        self.parameters['order'] = 2

    @staticmethod
    def applicable(dataset):
        """
        Check whether processing step is applicable to the given dataset.

        Filtering is only applicable to 1D datasets.

        Parameters
        ----------
        dataset : :class:`aspecd.dataset.Dataset`
            dataset to check

        Returns
        -------
        applicable : :class:`bool`
            `True` if successful, `False` otherwise.

        """
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
            self.parameters['window_width'] = int(np.ceil((1 / 10 * len(
                self.dataset.data.axes[0].values))) * 2 + 1)

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
        """Add padding to get same length of data at the end."""
        width = self.parameters['window_width']
        self.dataset.data.data = np.concatenate((
            np.ones(int(np.floor(width / 2))) * self.dataset.data.data[0],
            self.dataset.data.data,
            np.ones(int(np.floor(width / 2)) + 1) * self.dataset.data.data[-1]
        ))

    def _perform_binomial_filtering(self):
        filter_coefficients = (np.poly1d([0.5, 0.5]) ** self.parameters[
            'window_width']).coeffs
        filtered_data = np.array(np.convolve(self.dataset.data.data,
                                             filter_coefficients, mode='valid'))
        self.dataset.data.data = filtered_data

    def _perform_boxcar_filtering(self):
        filter_ = np.ones(self.parameters['window_width']) / self.parameters[
            'window_width']
        filtered_data = np.array(np.convolve(self.dataset.data.data,
                                             filter_, mode='valid'))
        self.dataset.data.data = filtered_data[:-1]
