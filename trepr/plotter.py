"""
Plotter.

To analyze a trepr spectrum it's helpful to plot the dataset either in a
2D or a 1D plot.

This module creates either a 2D or 1D plot of a given dataset.
"""

import matplotlib.pyplot as plt

import aspecd
from trepr import coloring
from trepr import io
from trepr import processing
from trepr import saver


class Plotter2D(aspecd.plotting.Plotter):
    """Create a 2D plot of a given dataset.

    Parameters
    ----------
    dataset_ : :obj:`trepr.dataset.Dataset`
        Object of the class Dataset.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    dataset : :obj:`trepr.dataset.Dataset`
        Object of the class Dataset.

    description : str
        Describes the aim of the class.

    """

    def __init__(self, dataset_=None):
        super().__init__()
        # public properties
        self.style = ''
        self.dataset = dataset_
        self.description = '2D plot as scaled image.'
        # protected properties
        self._extent = list()

    @staticmethod
    def _create_axis_label(axis):
        """Create the axes labels out of the axis quantity and unit."""
        axis_label = '$' + axis.quantity + '$' + ' / ' + axis.unit
        return axis_label

    def _create_plot(self):
        """Plot the given dataset with axes labels and a normed colormap."""
        self._get_extent()
        if self.style == 'xkcd':
            plt.xkcd()
        axes = plt.subplot()
        data = self.dataset.data.data
        norm = coloring.Coloring(dataset_=self.dataset).norm
        axes.imshow(data, norm=norm, interpolation='bilinear', cmap='seismic',
                    origin='lower', extent=self._extent, aspect='auto')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0),
                             useMathText=True)
        plt.xlabel(self._create_axis_label(self.dataset.data.axes[0]))
        plt.ylabel(self._create_axis_label(self.dataset.data.axes[1]))

    def _get_extent(self):
        """Define the start and end values of the axes."""
        x_axis_start = self.dataset.data.axes[0].values[0]
        x_axis_end = self.dataset.data.axes[0].values[-1]
        y_axis_start = self.dataset.data.axes[1].values[0]
        y_axis_end = self.dataset.data.axes[1].values[-1]
        self._extent = [x_axis_start, x_axis_end, y_axis_start, y_axis_end]


class Plotter1D(aspecd.plotting.Plotter):
    """Create a 1D plot of a given dataset.

    Parameters
    ----------
    dataset_ : object
        Object of the class Dataset.

    Attributes
    ----------
    style : str
        Defines whether the plot is done in xkcd style or not.

    dataset : object
        Object of the class Dataset.

    description : str
        Describes the aim of the class.

    """

    def __init__(self, dataset_=None):
        super().__init__()
        # public properties
        self.dataset = dataset_
        self.style = ''
        self.description = '1D line plot.'

    @staticmethod
    def _create_axis_label(axis):
        """Create the axes labels out of the axis quantity and unit."""
        axis_label = '$' + axis.quantity + '$' + ' / ' + axis.unit
        return axis_label

    def _create_plot(self):
        """Plot the given dataset with axes labels and a zero line."""
        if self.style == 'xkcd':
            plt.xkcd()
        data = self.dataset.data.data
        plt.subplots()
        plt.xlabel(self._create_axis_label(self.dataset.data.axes[0]))
        plt.ylabel(self._create_axis_label(self.dataset.data.axes[1]))
        plt.axhline(y=0, color='#999999')
        plt.plot(self.dataset.data.axes[0].values, data)
        axes = plt.gca()
        axes.set_xlim([self.dataset.data.axes[0].values[0],
                       self.dataset.data.axes[0].values[-1]])


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = io.Importer(source=PATH)
    dataset = aspecd.dataset.Dataset()
    dataset.import_from(importer)

    obj = processing.PretriggerOffsetCompensation()
    process1 = dataset.process(obj)
    saver_obj1 = saver.Saver(PATH + 'fig1.pdf')
    plotter_obj1 = Plotter2D()
    plot1 = dataset.plot(plotter_obj1)
    plot1.save(saver_obj1)

    averaging_obj = processing.Averaging(dimension=0,
                                        avg_range=[4.8e-07, 5.2e-07],
                                        unit='axis')
    process = dataset.process(averaging_obj)
    saver_obj = saver.Saver(PATH + 'fig2.pdf')
    plotter_obj = Plotter1D()
    dataset.plot(plotter_obj).save(saver_obj)
