"""
General plotting facilities.

Graphical representations of TREPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.
Additionally, stylers and savers are implemented.

"""

import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

import aspecd.plotting
from trepr import dataset
from trepr import io
from trepr import processing


class Plotter2D(aspecd.plotting.SinglePlotter):
    """Create a scaled image of a given dataset.

    Parameters
    ----------
    dataset_ : :obj:`trepr.dataset.Dataset`
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

    def __init__(self, dataset_=None):
        super().__init__()
        # public properties
        self.style = ''
        self.dataset = dataset_
        self.description = '2D plot as scaled image.'
        self.filename = ''
        # protected properties
        self._extent = list()

    def _create_plot(self):
        """Plot the given dataset with axes labels and a normed colormap."""
        self._get_extent()
        if self.style == 'xkcd':
            plt.xkcd()
        style_dict = {'interpolation': 'bilinear', 'cmap': 'seismic',
                      'origin': 'lower', 'aspect': 'auto'}
        self.axes.imshow(self.dataset.data.data,
                         norm=ColormapAdjuster(dataset_=self.dataset).norm,
                         extent=self._extent, **style_dict)
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                             useMathText=True)

    def _get_extent(self):
        """Define the start and end values of the axes."""
        x_axis_start = self.dataset.data.axes[0].values[0]
        x_axis_end = self.dataset.data.axes[0].values[-1]
        y_axis_start = self.dataset.data.axes[1].values[0]
        y_axis_end = self.dataset.data.axes[1].values[-1]
        self._extent = [x_axis_start, x_axis_end, y_axis_start, y_axis_end]


class Plotter1D(aspecd.plotting.SinglePlotter):
    """Create a 1D plot of a given dataset.

    Parameters
    ----------
    dataset_ : :obj:`trepr.dataset.Dataset`
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

    def __init__(self, dataset_=None):
        super().__init__()
        # public properties
        self.dataset = dataset_
        self.style = ''
        self.description = '1D line plot.'
        self.filename = ''

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        if self.style == 'xkcd':
            plt.xkcd()
        self.axes.plot(self.dataset.data.axes[0].values, self.dataset.data.data)
        self.axes.set_xlim([self.dataset.data.axes[0].values[0],
                            self.dataset.data.axes[0].values[-1]])
        plt.ticklabel_format(style='sci', scilimits=(-2, 4), useMathText=True)
        plt.axhline(y=0, color='#999999')


class ColormapAdjuster:
    """General facilities to adjust the colormap.

    This class makes sure that the zero point of the colormap is equal to the
    zero point of the dataset.

    Parameters
    ----------
    dataset_ : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    """

    def __init__(self, dataset_=dataset.Dataset()):
        # public properties
        self.dataset = dataset_
        self.norm = None
        # protected properties
        self._bound = None
        # calls to methods
        self._get_min_and_max()
        self._set_norm()

    def _get_min_and_max(self):
        """Calculate the minimum an maximum of the intensity."""
        min_ = np.amin(self.dataset.data.data)
        max_ = np.amax(self.dataset.data.data)
        self._bound = np.amax([abs(min_), max_])

    def _set_norm(self):
        """Normalize the colormap."""
        self.norm = \
            mpl.colors.Normalize(vmin=self._bound * -1, vmax=self._bound)


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = io.SpeksimImporter(source=PATH)
    dataset_ = dataset.Dataset()
    dataset_.import_from(importer)

    obj = processing.PretriggerOffsetCompensation()
    process1 = dataset_.process(obj)
    saver_obj1 = aspecd.plotting.Saver(filename='plotter.pdf')
    plotter_obj1 = Plotter2D()
    plot1 = dataset_.plot(plotter_obj1)
    plot1.save(saver_obj1)

    averaging_obj = processing.Averaging(dimension=0,
                                         avg_range=[4.8e-07, 5.2e-07],
                                         unit='axis')
    process = dataset_.process(averaging_obj)
    saver_obj = aspecd.plotting.Saver(filename='plotterli.pdf')
    plotter_obj = Plotter1D()
    plot2 = dataset_.plot(plotter_obj)
    plot2.save(saver_obj)
