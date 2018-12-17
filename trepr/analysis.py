import numpy as np
from scipy import constants
from datetime import datetime
import matplotlib.pyplot as plt



import aspecd.analysis
import trepr.io


class MwFreqAnalysis(aspecd.analysis.AnalysisStep):

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Microwave frequency analysis'
        # protected properties
        self._delta_mw_freq = float()
        self._B0 = float()
        self._step_size_in_T = float()

    def analyse(self, dataset=None):
        self._calculate_mw_freq_amplitude()
        self._convert_delta_mw_freq_to_magnetic_field()
        self._calculate_step_size()
        self._compare_B0_with_step_size()

    def _calculate_mw_freq_amplitude(self):
        self._delta_mw_freq = max(self.dataset.microwave_frequency.data) - \
                              min(self.dataset.microwave_frequency.data)

    def _convert_delta_mw_freq_to_magnetic_field(self):
        electron_g_factor = constants.value('electron g factor')
        bohr_magneton = constants.value('Bohr magneton')
        planck_constant = constants.value('Planck constant')
        self._B0 = self._delta_mw_freq * 1e9 * planck_constant / \
                   (-1 * electron_g_factor * bohr_magneton)

    def _calculate_step_size(self):
        step_size_in_gauss = \
            self.dataset.microwave_frequency.axes[0].values[1] - \
            self.dataset.microwave_frequency.axes[0].values[0]
        self._step_size_in_T = step_size_in_gauss * 1e-4

    def _compare_B0_with_step_size(self):
        ratio = self._B0 / self._step_size_in_T
        print('step size: ' + str(self._step_size_in_T * 1e3) +
              ' mT\nfrequency shift: ' + str(self._B0 * 1e3) +
              ' mT\nratio frequency shift/step size: ' +
              str(ratio))


class TimeStampAnalysis(aspecd.analysis.AnalysisStep):

    def __init__(self):
        super().__init__()
        # public properties
        self.description = 'Time stamp analysis.'
        # protected properties
        self._time_stamp_floats = None
        self._time_field_matrix = None
        self._time_stamp_deltas = list()

    def analyse(self, dataset=None):
        self._create_time_field_matrix()
        self._calculate_time_stamp_delta()

    def _create_time_field_matrix(self):
        self._time_stamp_floats = np.zeros((len(self.dataset.time_stamp.data)))
        for i in range(len(self.dataset.time_stamp.data)):
            time_stamp = self.dataset.time_stamp.data[i].timestamp()
            self._time_stamp_floats[i] = time_stamp
        self._time_field_matrix = np.zeros((len(self._time_stamp_floats), 2))
        self._time_field_matrix[:, 0] = self._time_stamp_floats
        self._time_field_matrix[:, 1] = self.dataset.time_stamp.axes[0].values
        self._time_field_matrix = self._time_field_matrix[self._time_field_matrix[:, 0].argsort()]
        for i in range(len(self._time_field_matrix)):
            time_stamp = datetime.fromtimestamp(self._time_field_matrix[i, 0])
            self._time_field_matrix[i, 0] = time_stamp
        print(self._time_field_matrix)

    def _calculate_time_stamp_delta(self):
        for i in range(len(self._time_field_matrix)-1):
            self._time_field_matrix[i, 0] = self._time_field_matrix[i+1, 0] - self._time_field_matrix[i, 0]
        self._time_field_matrix = np.delete(self._time_field_matrix, -1, axis=0)
        self._time_field_matrix = self._time_field_matrix[self._time_field_matrix[:, 1].argsort()]
        #plt.plot(self._time_field_matrix[:, 1], self._time_field_matrix[:, 0], linestyle = '', marker='.')
        #plt.show()


if __name__ == '__main__':
    imp = trepr.io.SpeksimImporter(source=
                                   '/home/popp/nas/Python/Daten/messung01/')
    dataset_ = trepr.dataset.Dataset()
    dataset_.import_from(imp)
    obj = TimeStampAnalysis()
    obj.dataset = dataset_
    dataset_.analyse(obj)