"""To make a 2D plot meaningful, it needs significant colors.

This module makes sure that the zero point of the colormap is equal to the
zero point of the dataset.
"""

import matplotlib as mpl
import numpy as np

from trepr import dataset


class Coloring:
    """Set the colormap zero point equal to the dataset zero point.

    Parameters
    ----------
    dataset : object
        object of the dataset class.
    """

    def __init__(self, dataset=dataset.Dataset()):
        self.dataset = dataset
        self._get_min_and_max()

    def _get_min_and_max(self):
        """Calculate the minimum an maximum of the dataset to set the
        colormap.
        """
        self._abs_min = abs(np.amin(self.dataset.data.data))
        self._max = np.amax(self.dataset.data.data)
        self._values = [self._abs_min, self._max]
        self._bound = max(self._values)
        self.norm = mpl.colors.Normalize(vmin=self._bound * -1,
                                         vmax=self._bound)
