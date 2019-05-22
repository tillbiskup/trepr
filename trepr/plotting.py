"""
General plotting facilities.

Graphical representations of TREPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.
Additionally, savers (and stylers) are implemented.

"""

import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

import aspecd.plotting
import trepr.dataset


class ScaledImagePlot(aspecd.plotting.SinglePlotter):
    """Create a scaled image of a given dataset.

    Parameters
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    description : str
        Describes the aim of the class.

    filename : str
        Name of the resulting plot file.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '2D plot as scaled image.'
        self.filename = ''
        # protected properties
        self._extent = list()
        self._style_dict = {'interpolation': 'bilinear',
                            'cmap': 'seismic',
                            'origin': 'lower',
                            'aspect': 'auto'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (0, 0),
                                  'useMathText': True}

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
        self.axes.imshow(self.dataset.data.data,
                         norm=colormap_adjuster.normalised_colormap,
                         extent=self._extent,
                         **self._style_dict)

    def _format_ticklabels(self):
        """Set the format for the ticklabels"""
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

    Parameters
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    description : str
        Describes the aim of the class.

    filename : str
        Name of the resulting plot file.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.style = ''
        self.description = '1D line plot.'
        self.filename = ''
        # protected properties
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        self._set_style()
        self._display_data()
        self._set_axes()
        self._display_zero_line()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _set_axes(self):
        """Set the limits of the x-axis as well as the ticklabel format."""
        self.axes.set_xlim([self.dataset.data.axes[0].values[0],
                            self.dataset.data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)

    def _display_data(self):
        """Plot the data."""
        self.axes.plot(self.dataset.data.axes[0].values,
                       self.dataset.data.data)

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()


class MultiLinePlot(aspecd.plotting.MultiPlotter):

    def __init__(self):
        super().__init__()
        self.description = '1D line plot for multiple lines.'
        self.parameters['colors'] = None
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        self._display_zero_line()
        self._display_data()
        self._set_axes()

    def _display_data(self):
        for i, dataset in enumerate(self.datasets):
            if self.parameters['colors']:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data, color=self.parameters['colors'][i])
            else:
                self.axes.plot(dataset.data.axes[0].values, dataset.data.data)

    def _set_axes(self):
        self.axes.set_xlim([self.datasets[0].data.axes[0].values[0],
                            self.datasets[0].data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)


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


class Saver(aspecd.plotting.Saver):

    pass


if __name__ == '__main__':
    import trepr.processing
    import trepr.io
    PATH = '/home/popp/nas/DatenBA/PCDTBT-ODCB/X-Band/080K/messung17/'
    importer = trepr.io.SpeksimImporter(source=PATH)
    dataset_ = trepr.dataset.ExperimentalDataset()
    dataset_.import_from(importer)

    obj = trepr.processing.PretriggerOffsetCompensation()
    process1 = dataset_.process(obj)
    saver_obj1 = aspecd.plotting.Saver(filename='plotter.pdf')
    plotter_obj1 = ScaledImagePlot()
    plot1 = dataset_.plot(plotter_obj1)
    plot1.save(saver_obj1)

    averaging_obj = \
        trepr.processing.Averaging(dimension=0,
                                   avg_range=[4.9e-07, 5.1e-07],
                                   unit='axis')
    process = dataset_.process(averaging_obj)
    saver_obj = aspecd.plotting.Saver(filename='plotterli.pdf')
    plotter_obj = LinePlot()
    plot2 = dataset_.plot(plotter_obj)
    plot2.save(saver_obj)
