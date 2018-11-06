"""One of the first processing steps after measuring trepr is to set the
average of the pretrigger timetrace to zero. The so called pretrigger
offset compensation.

This module makes a pretrigger offset compensation on a given dataset.
"""

import numpy as np

import aspecd.processing
from trepr import importer


class PretriggerOffsetCompensation(aspecd.processing.ProcessingStep):
    """Pretrigger offset compensation on a given dataset.

    Attributes
    ----------
    description : str
        Describes the aim of the class.

    undoable : bool
        Information weather the processing step is undoable or not.
    """

    def __init__(self):
        super().__init__()
        # public properties:
        # Note: self.parameters inherited
        self.description = 'Pretrigger offset compensation'
        self.undoable = True

    def _get_zeropoint_index(self):
        """Get the index of the last negative value on the timeaxis."""
        zeropoint_index = \
            np.argmin(np.cumsum(self.dataset.data.axes[0].values))
        self.parameters['zeropoint_index'] = int(zeropoint_index)

    @staticmethod
    def _get_pretrigger_average(timetrace, range_end=1):
        """Calculate the average of the timetrace before triggering."""
        array = timetrace[0:range_end]
        return np.average(array)

    def _perform_task(self):
        """Perform the processing step and return the processed data to the
        dataset.
        """
        self._get_zeropoint_index()
        range_end = self.parameters['zeropoint_index']
        for fieldpoint, timetrace in enumerate(self.dataset.data.data):
            pretrig_avg = self._get_pretrigger_average(timetrace, range_end)
            self.dataset.data.data[fieldpoint] = timetrace - pretrig_avg


if __name__ == '__main__':
    PATH = '../../Daten/messung17/'
    importer = importer.Importer(path=PATH)
    importer.dataset.import_from(importer)
    obj = PretriggerOffsetCompensation()
    process = importer.dataset.process(obj)
