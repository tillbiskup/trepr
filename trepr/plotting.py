"""
Plotting: Graphical representations of data extracted from datasets.

Graphical representations of tr-EPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.
Additionally, savers (and stylers) are implemented.

Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting inside the
actual plotter classes. Note that the user of the trepr package usually will
not be exposed directly to the matplotlib interface.

Generally, two types of plotters can be distinguished:

* Plotters for handling single datasets

  Shall be derived from :class:`aspecd.plotting.SinglePlotter`.

* Plotters for handling multiple datasets

  Shall be derived from :class:`aspecd.plotting.MultiPlotter`.

In the first case, the plot is usually handled using the :meth:`plot` method
of the respective :obj:`trepr.dataset.Dataset` object. Additionally,
those plotters always only operate on the data of a single dataset, and the
plot can easily be attached as a representation to the respective dataset.
Plotters handling single datasets should always inherit from the
:class:`aspecd.plotting.SinglePlotter` class.

In the second case, the plot is handled using the :meth:`plot` method of the
:obj:`aspecd.plotting.Plotter` object, and the datasets are stored as a list
within the plotter. As these plots span several datasets, there is no easy
connection between a single dataset and such a plot in sense of
representations stored in datasets. Plotters handling multiple datasets should
always inherit from the :class:`aspecd.plotting.MultiPlotter` class.


A note on array dimensions and axes
===================================

Something often quite confusing is the apparent inconsistency between the
order of array dimensions and the order of axes. While we are used to assign
axes in the order *x*, *y*, *z*, and assuming *x* to be horizontal,
*y* vertical (and *z* sticking out of the paper plane), arrays are usually
indexed row-first, column-second (at least in the widely followed C
convention; with FORTRAN things are different). That means, however, that if
you simply plot a 2D array in axes, your *first* dimension is along the *y*
axis, the *second* dimension along the *x* axis.

Therefore, as the axes of your datasets will always correspond to the array
dimensions of your data, in case of 2D plots you will need to *either* use
the information contained in the second axis object for your *x* axis label,
and the information from the first axis object for your *y* axis label,
*or* to transpose the data array.

Another aspect to have in mind is the position of the origin. Usually,
in a Cartesian coordinate system, convention is to have the origin (0,
0) in the *lower left* of the axes (for the positive quadrant). However,
for images, convention is to have the corresponding (0, 0) pixel located in
the *upper left* edge of your image. Therefore, those plotting methods
dealing with images will usually *revert* the direction of your *y* axis.
Most probably, eventually you will have to check with real data and ensure
the plotters to plot data and axes in a consistent fashion.


Types of concrete plotters
==========================

The trepr package comes with a series of concrete plotters included ready
to be used, thanks to inheriting from the underlying ASpecD framework. As
stated above, plotters can generally be divided into two types: plotters
operating on single datasets and plotters combining the data of multiple
datasets into a single figure.

Additionally, plotters can be categorised with regard to creating figures
consisting of a single or multiple axes. The latter are plotters inheriting
from the :class:`aspecd.plotting.CompositePlotter` class. The latter can be
thought of as templates for the other plotters to operate on, *i.e.* they
provide the axes for other plotters to display their results.


Concrete plotters for single datasets
-------------------------------------

* :class:`trepr.plotting.SinglePlotter1D`

  Basic line plots for single datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`trepr.plotting.SinglePlotter2D`

  Basic 2D plots for single datasets, allowing to plot a series of 2D plots,
  including contour plots and image-type display

* :class:`trepr.plotting.SingleCompositePlotter`

  Composite plotter for single datasets, allowing to plot different views of
  one and the same datasets by using existing plotters for single datasets.


Concrete plotters for multiple datasets
---------------------------------------

* :class:`trepr.plotting.MultiPlotter1D`

  Basic line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`trepr.plotting.MultiPlotter1DStacked`

  Stacked line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots


A note for developers
=====================

As each kind of spectroscopy comes with own needs for extensions, there is a
class :class:`PlotterExtensions` that can be used as a mixin class for other
plotters to provide additional functionality for all plotters.

Make sure when implementing functionality here that it really works with all
types of plotters, *i.e.* both SinglePlotters and MultiPlotters. This is
particularly relevant if you need to get information from dataset(s),
as a SinglePlotter will have an attribute ``dataset``, while a MultiPlotter
will have an attribute ``datasets``.


Module documentation
====================

"""

import matplotlib as mpl
from matplotlib.colors import ListedColormap
import numpy as np

import aspecd.plotting
import trepr.dataset
from trepr import utils


class ColormapAdjuster:
    """General facilities to adjust the colormap.

    This class makes sure that the zero point of the colormap is equal to the
    zero point of the dataset.

    Parameters
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    normalised_colormap : :class:`matplotlib.colormap`
        Colormap normalised to data of dataset.


    .. deprecated:: 0.1
        Will be included in :class:`aspecd.plotting.SinglePlotter2D`.

    """

    def __init__(self, dataset=trepr.dataset.ExperimentalDataset()):
        # public properties
        self.dataset = dataset
        self.normalised_colormap = None
        # protected properties
        self._bound = None

    def adjust(self):
        """Perform all methods to adjust the colormap."""
        self._get_min_and_max()
        self._set_norm()

    def _get_min_and_max(self):
        """Calculate the minimum an maximum of the intensity."""
        min_ = np.amin(self.dataset.data.data)
        max_ = np.amax(self.dataset.data.data)
        self._bound = np.amax([abs(min_), max_])

    def _set_norm(self):
        """Normalize the colormap."""
        self.normalised_colormap = \
            mpl.colors.Normalize(vmin=self._bound * -1, vmax=self._bound)


class PlotterExtensions:
    """Extensions for plots of tr-EPR data.

    This class is meant as a mixin class for plotters of the cwepr package
    and provides functionality specific for tr-EPR-spectroscopic data.

    Hence it can only be used as mixin in addition to a plotter class.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those defined by the actual
        plotter:

        g-axis: :class:`bool`
            Whether to show an additional *g* axis opposite of the magnetic
            field axis

            This assumes the magnetic field axis to be the *x* axis and the
            magnetic field values to be in millitesla (mT), as it calls
            :func:`cwepr.utils.convert_mT2g`.


    .. versionadded:: 0.2

    """

    def __init__(self):
        self.parameters['g-axis'] = False  # noqa

    def _create_g_axis(self, mw_freq=None):
        """
        Add a *g* axis as second axis opposite the magnetic field axis.

        Currently, this function assumes the magnetic field axis to be the
        *x* axis. Additionally, the magnetic field values are assumed to be
        in millitesla (mT), and the microwave frequency to be in gigahertz (
        GHz).

        Parameters
        ----------
        mw_freq : :class:`float`
            microwave frequency (**in GHz**) used to convert from mT to g

        """
        def forward(values):
            return utils.convert_mT2g(values, mw_freq=mw_freq)

        def backward(values):
            return utils.convert_g2mT(values, mw_freq=mw_freq)

        gaxis = self.ax.secondary_xaxis('top', functions=(backward, forward))
        gaxis.set_xlabel(r'$g\ value$')


class SinglePlotter1D(aspecd.plotting.SinglePlotter1D, PlotterExtensions):
    """1D plots of single datasets.

    Convenience class taking care of 1D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter1D`
    class for details.

    Furthermore, the class inhertis all functionality from
    :class:`PlotterExtensions`. See there for additional details.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           filename: output.pdf


    In case you would like to have a *g* axis plotted as a second *x* axis on
    top (note that this only makes sense in case of a calibrated magnetic
    field axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def _create_plot(self):
        super()._create_plot()
        if self.parameters['g-axis'] and self.dataset.data.axes[0].unit == 'mT':
            self._create_g_axis(self.dataset.metadata.bridge.mw_frequency.value)


class SinglePlotter2D(aspecd.plotting.SinglePlotter2D, PlotterExtensions):
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter2D`
    class for details.

    Furthermore, the class inhertis all functionality from
    :class:`PlotterExtensions`. See there for additional details.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf

    To change the axes (flip *x* and *y* axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           parameters:
             switch_axes: True

    To use another type (here: contour):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour

    To set the number of levels of a contour plot to 10:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour
           parameters:
             levels: 10

    To change the colormap (cmap) used:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           properties:
             drawing:
               cmap: RdGy

    Make sure to check the documentation of the ASpecD
    :mod:`aspecd.plotting` module for further parameters that can be set.

    In case you would like to have a *g* axis plotted as a second *x* axis on
    top (note that this only makes sense in case of a calibrated magnetic
    field axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def _create_plot(self):
        super()._create_plot()
        if self.parameters['g-axis'] and self.dataset.data.axes[0].unit == 'mT':
            self._create_g_axis(self.dataset.metadata.bridge.mw_frequency.value)


class SinglePlotter2DStacked(aspecd.plotting.SinglePlotter2DStacked,
                             PlotterExtensions):
    """Stacked plots of 2D data.

    A stackplot creates a series of lines stacked on top of each other from
    a 2D dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter2DStacked`
    class for details.

    Furthermore, the class inhertis all functionality from
    :class:`PlotterExtensions`. See there for additional details.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf

    If you need to more precisely control the formatting of the y tick
    labels, particularly the number of decimals shown, you can set the
    formatting accordingly:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             yticklabelformat: '%.2f'

    In this particular case, the y tick labels will appear with only two
    decimals. Note that currently, the "old style" formatting specifications
    are used due to their widespread use in other programming languages and
    hence the familiarity of many users with this particular notation.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True

    In case you would like to have a *g* axis plotted as a second *x* axis on
    top (note that this only makes sense in case of a calibrated magnetic
    field axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2DStacked
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def _create_plot(self):
        super()._create_plot()
        if self.parameters['g-axis'] and self.dataset.data.axes[0].unit == 'mT':
            self._create_g_axis(self.dataset.metadata.bridge.mw_frequency.value)


class MultiPlotter1D(aspecd.plotting.MultiPlotter1D, PlotterExtensions):
    # noinspection PyUnresolvedReferences
    """1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets.

    As the class is inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.MultiPlotter1D`
    class for its general use.

    Due to the need for displaying tr-EPR spectra, this class implements two
    additional keys in the :attr:`parameters` attribute documented below.
    This may be moved up to the parent class in ASpecD at some point.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        Additionally to those from :class:`aspecd.plotting.MultiPlotter1D`,
        the following parameters are allowed:

        switch_axes : :class:`bool`
            Whether to switch *x* and *y* axes

            Normally, the first axis is used as *x* axis, and the second
            as *y* axis. Sometimes, switching this assignment is
            necessary or convenient.

            Default: False

        tight: :class:`str`
            Whether to set the axes limits tight to the data

            Possible values: 'x', 'y', 'both'

            Default: ''


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    In case you would like to have a *g* axis plotted as a second *x* axis on
    top (note that this only makes sense in case of a calibrated magnetic
    field axis):

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def __init__(self):
        super().__init__()
        self.parameters['switch_axes'] = False
        self.parameters['tight'] = ''

    def _create_plot(self):
        """Actual drawing of datasets."""
        plot_function = getattr(self.axes, self.type)
        self.drawings = []
        for idx, dataset in enumerate(self.datasets):
            if not self.properties.drawings[idx].label:
                self.properties.drawings[idx].label = dataset.label
            if self.parameters['switch_axes']:
                drawing, = plot_function(
                    dataset.data.data,
                    dataset.data.axes[0].values,
                    label=self.properties.drawings[idx].label)
            else:
                drawing, = plot_function(
                    dataset.data.axes[0].values,
                    dataset.data.data,
                    label=self.properties.drawings[idx].label)
            self.drawings.append(drawing)
        if self.parameters['g-axis'] \
                and self.datasets[0].data.axes[0].unit == 'mT':
            self._create_g_axis(
                self.datasets[0].metadata.bridge.mw_frequency.value)
        if self.parameters['tight']:
            if self.parameters['tight'] in ('x', 'both'):
                if self.parameters['switch_axes']:
                    self.axes.set_xlim([
                        min([dataset.data.data.min() for dataset in
                             self.datasets]),
                        max([dataset.data.data.max() for dataset in
                             self.datasets])
                    ])
                else:
                    self.axes.set_xlim([
                        min([dataset.data.axes[0].values.min() for dataset in
                             self.datasets]),
                        max([dataset.data.axes[0].values.max() for dataset in
                             self.datasets])
                    ])
            if self.parameters['tight'] in ('y', 'both'):
                if self.parameters['switch_axes']:
                    self.axes.set_ylim([
                        min([dataset.data.axes[0].values.min() for dataset in
                             self.datasets]),
                        max([dataset.data.axes[0].values.max() for dataset in
                             self.datasets])
                    ])
                else:
                    self.axes.set_ylim([
                        min([dataset.data.data.min() for dataset in
                             self.datasets]),
                        max([dataset.data.data.max() for dataset in
                             self.datasets])
                    ])

    def _set_axes_labels(self):
        super(MultiPlotter1D, self)._set_axes_labels()
        if self.parameters['switch_axes']:
            old_xlabel = self.axes.get_xlabel()
            old_ylabel = self.axes.get_ylabel()
            self.axes.set_xlabel(old_ylabel)
            self.axes.set_ylabel(old_xlabel)


class MultiPlotter1DStacked(aspecd.plotting.MultiPlotter1DStacked,
                            PlotterExtensions):
    """Stacked 1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.MultiPlotter1DStacked`
    class for details.

    Furthermore, the class inhertis all functionality from
    :class:`PlotterExtensions`. See there for additional details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True

    In case you would like to have a *g* axis plotted as a second *x* axis on
    top (note that this only makes sense in case of a calibrated magnetic
    field axis):

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def _create_plot(self):
        super()._create_plot()
        if self.parameters['g-axis'] \
                and self.datasets[0].data.axes[0].unit == 'mT':
            self._create_g_axis(
                self.datasets[0].metadata.bridge.mw_frequency.value)
