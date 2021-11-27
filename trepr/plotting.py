"""
Plotting: Graphical representations of data extracted from datasets.

Graphical representations of TREPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.
Additionally, savers (and stylers) are implemented.

Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting.

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
indexed row-first, column-second. That means, however, that if you simply
plot a 2D array in axes, your *first* dimension is along the *y* axis,
the *second* dimension along the *x* axis.

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


Module documentation
====================

"""

from colour import Color
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np

import aspecd.plotting
import trepr.dataset

left = Color(rgb=(102 / 255, 0 / 255, 204 / 255))
middle = Color(rgb=(1, 1, 1))
right = Color(rgb=(255 / 255, 51 / 255, 51 / 255))

R_left = np.linspace(102 / 255, 1, 128)
G_left = np.linspace(0, 1, 128)
B_left = np.linspace(204 / 255, 1, 128)

A_left = np.linspace(1, 0, 128)
A_right = np.linspace(0, 1, 128)

R_right = np.linspace(1, 255 / 255, 128)
G_right = np.linspace(1, 51 / 255, 128)
B_right = np.linspace(1, 51 / 255, 128)

colors_left = list(left.range_to(middle, 128))
colors_right = list(middle.range_to(right, 128))
for i, _ in enumerate(colors_left):
    colors_left[i] = list(colors_left[i].rgb)
for i, _ in enumerate(colors_right):
    colors_right[i] = list(colors_right[i].rgb)

for i, _ in enumerate(colors_left):
    colors_left[i][0] = R_left[i]
    colors_left[i][1] = G_left[i]
    colors_left[i][2] = B_left[i]

for i, _ in enumerate(colors_right):
    colors_right[i][0] = R_right[i]
    colors_right[i][1] = G_right[i]
    colors_right[i][2] = B_right[i]

viridis = cm.get_cmap('viridis', 256)
jara_colors = viridis(np.linspace(0, 1, 256))

for i in range(0, 128):
    jara_colors[i][0:3] = [102 / 255, 0, 204 / 255]
    jara_colors[i][3] = A_left[i]
for i in range(128, 255):
    jara_colors[i][0:3] = [1, 51 / 255, 51 / 255]
    jara_colors[i][3] = A_right[i - 128]

jara_cmap = ListedColormap(jara_colors)


class ScaledImagePlot(aspecd.plotting.SinglePlotter):
    """Create a scaled image of a given dataset.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    description : str
        Describes the aim of the class.


    .. deprecated:: 0.1
        Use :class:`SinglePlotter2D` instead.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '2D plot as scaled image.'
        # protected properties
        self._extent = list()
        self._style_dict = {'interpolation': 'bilinear',
                            'cmap': viridis,
                            'origin': 'lower',
                            'aspect': 'auto'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (0, 0),
                                  'useMathText': True}
        self.parameters['show_zero_lines'] = False

    def _create_plot(self):
        """Plot the given dataset with axes labels and a normed colormap."""
        self._get_extent()
        self._set_style()
        self._display_data()
        self._format_ticklabels()

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _display_data(self):
        """Display the data with adjusted colormap."""
        colormap_adjuster = ColormapAdjuster(dataset=self.dataset)
        colormap_adjuster.adjust()
        self.axes.imshow(self.dataset.data.data.T,
                         norm=colormap_adjuster.normalised_colormap,
                         extent=self._extent,
                         **self._style_dict)

    def _format_ticklabels(self):
        """Set the format for the ticklabels."""
        plt.ticklabel_format(axis='x', **self._ticklabel_format)

    def _get_extent(self):
        """Define the start and end values of the axes."""
        x_axis_start = self.dataset.data.axes[0].values[0]
        x_axis_end = self.dataset.data.axes[0].values[-1]
        y_axis_start = self.dataset.data.axes[1].values[0]
        y_axis_end = self.dataset.data.axes[1].values[-1]
        self._extent = [x_axis_start, x_axis_end, y_axis_start, y_axis_end]


class LinePlot(aspecd.plotting.SinglePlotter):
    """Create a 1D line plot of a given dataset.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    description : str
        Describes the aim of the class.


    .. deprecated:: 0.1
        Use :class:`SinglePlotter1D` instead.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '1D line plot.'
        self.parameters['color'] = None
        # protected properties
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        self._set_style()
        self._display_zero_line()
        self._display_data()
        self._set_axes()

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _display_data(self):
        """Plot the data."""
        self.axes.plot(self.dataset.data.axes[0].values,
                       self.dataset.data.data, color=self.parameters['color'])

    def _set_axes(self):
        """Set the limits of the x-axis as well as the ticklabel format."""
        self.axes.set_xlim([self.dataset.data.axes[0].values[0],
                            self.dataset.data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)


class MultiLinePlot(aspecd.plotting.MultiPlotter):
    """Plot multiple datasets as lines.

    .. deprecated:: 0.1
        Use :class:`MultiPlotter1D` instead.
    """

    def __init__(self):
        super().__init__()
        self.description = '1D line plot for multiple lines.'
        self.parameters['color'] = None
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        self._display_zero_line()
        self._display_data()
        self._set_axes()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _display_data(self):
        for idx, dataset in enumerate(self.datasets):
            if self.parameters['color']:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data,
                               color=self.parameters['color'][idx])
            else:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data)

    def _set_axes(self):
        self.axes.set_xlim([self.datasets[0].data.axes[0].values[0],
                            self.datasets[0].data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)


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


class SinglePlotter1D(aspecd.plotting.SinglePlotter1D):
    """1D plots of single datasets.

    Convenience class taking care of 1D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter1D`
    class for details.

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

    """


class SinglePlotter2D(aspecd.plotting.SinglePlotter2D):
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter2D`
    class for details.

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

    """


class MultiPlotter1D(aspecd.plotting.MultiPlotter1D):
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


class MultiPlotter1DStacked(aspecd.plotting.MultiPlotter1DStacked):
    """Stacked 1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.MultiPlotter1DStacked`
    class for details.

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

    """


class CompositePlotter(aspecd.plotting.CompositePlotter):
    """Base class for plots consisting of multiple axes.

    The underlying idea of composite plotters is to use a dedicated
    existing plotter for each axis and assign this plotter to the list of
    plotters of the CompositePlotter object. Thus the actual plotting task
    is left to the individual plotter and the CompositePlotter only takes
    care of the specifics of plots consisting of more than one axis.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.CompositePlotter`
    class for details.

    """


class SingleCompositePlotter(aspecd.plotting.SingleCompositePlotter):
    """Composite plotter for single datasets.

    This composite plotter is used for different representations of one and the
    same dataset in multiple axes contained in one figure. In this respect,
    it works like all the other ordinary single plotters derived from
    :class:`SinglePlotter`, *i.e.* it usually gets called by using the dataset's
    :meth:`aspecd.dataset.Dataset.plot` method.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SingleCompositePlotter`
    class for details.

    """


class Saver(aspecd.plotting.Saver):
    """Base class for saving plots.

    For basic saving of plots, no subclassing is necessary, as the
    :meth:`save` method uses :meth:`matplotlib.figure.Figure.savefig` and
    can cope with all possible parameters via the :attr:`parameters` property.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.Saver` class for
    details.

    """
