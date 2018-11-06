"""This module saves a plot."""

import matplotlib.pyplot as plt

import aspecd


class Saver(aspecd.plotting.Saver):
    """Save a given plot.

    Parameters:
    filename : str
        Path, including the filename, where to save the plot.
    """

    def __init__(self, filename=None):
        super().__init__(filename)

    def _save_plot(self):
        plt.savefig(self.filename)


if __name__ == '__main__':
    obj = Saver()
