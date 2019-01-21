"""
Interface between SpecProFi and the trep package.

One main aspect of connecting the trepr package to SpecProFi is a functional
interface.
"""

import collections
import numpy as np

import SpecProFi.specprofi_oop as spf


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class DimensionError(Error):
    """Exception raised when the dimension of the dataset isn't 1."""
    def __init__(self, message=''):
        self.message = message


class SpecProFiInterface:
    """Call SpecProFi with given fitting parameters and a given dataset.

    In order to interpret a spectrum, it is essential to know the parameters
    that make up the shape of the spectrum. To achieve this, the spectrum can
    be fitted and the best possible parameters determined using a least-square.

    Parameters
    ----------
    fitting_parameters : dict
        Dictionary containing all necessary fitting parameters.

    dataset : :obj:`trepr.dataset.Dataset`
        Dataset containing raw data and metadata.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset to work with.

    Raises
    ------
    DimensionError
        Raised if the dimension of the dataset isn't 2.

    """

    def __init__(self, fitting_parameters, dataset):
        # public properties
        self.dataset = dataset
        # protected properties
        self._exp = spf.Exp()
        self._opt = spf.Opt()
        self._fit_opt = spf.FitOpt()
        self._sys = list()
        self._vary = list()
        self._exp_list = list()
        self._x_data = None
        self._y_data = None
        self._yaml_obj = None
        self._fitting_parameters = fitting_parameters
        self._path = None

    def fit(self):
        """Execute all necessary methods."""
        self._convert_angle_to_radian()
        self._preallocate_matrices_for_dataset()
        self._set_x_and_y_data()
        self._set_sys_exp_opt_fitopt()
        self._set_vary()
        self._perform_fitting()

    def _convert_angle_to_radian(self):
        """Convert all given angles to radians."""
        self._fitting_parameters['fitting']['FitOpt']['thetaoff'] = \
            [angle / 180 * np.pi
             for angle in
             self._fitting_parameters['fitting']['FitOpt']['thetaoff']]

    def _preallocate_matrices_for_dataset(self):
        """Prepare arrays for x and y data."""
        self._x_data = np.zeros(
            [len(self._fitting_parameters['datasets']),
             self._fitting_parameters['fitting']['Opt']['nPoints']])
        self._y_data = np.zeros(
            [len(self._fitting_parameters['datasets']),
             self._fitting_parameters['fitting']['Opt']['nPoints']])

    def _set_x_and_y_data(self):
        """Set x and y data to the prepared arrays."""
        for i in range(len(self._fitting_parameters['datasets'])):
            self._check_dimension(self.dataset)
            if len(self._fitting_parameters['datasets']) == 1:
                self._x_data = self.dataset.data.axes[0].values
                self._y_data = self.dataset.data.data
            else:
                self._x_data[i, :] = self.dataset.data.axes[0].values
                self._y_data[i, :] = self.dataset.data.data
                self._y_data[i, :] = self._y_data[i, :] / sum(
                    abs(self._y_data[i, :]))

    @staticmethod
    def _check_dimension(dataset):
        """Check weather the dimension of the dataset is 2."""
        if len(dataset.data.axes) != 2:
            raise DimensionError('Dimension of the dataset needs to be 1.')

    def _set_sys_exp_opt_fitopt(self):
        """Set the sys, exp and opt attributes."""
        for i in range(len(self._fitting_parameters['fitting']['Sys'])):
            self._sys.append(spf.Sys())
            for key in self._fitting_parameters['fitting']['Sys'][i]:
                setattr(self._sys[i], key.lower(),
                        self._fitting_parameters['fitting']['Sys'][i][key])
        for key in self._fitting_parameters['fitting']['Exp']:
            setattr(self._exp, key.lower(),
                    self._fitting_parameters['fitting']['Exp'][key])
        for i in range(len(self._fitting_parameters['datasets'])):
            self._exp_list.append(self._exp)
        for key in self._fitting_parameters['fitting']['Opt']:
            setattr(self._opt, key.lower(),
                    self._fitting_parameters['fitting']['Opt'][key])
        for key in self._fitting_parameters['fitting']['FitOpt']:
            setattr(self._fit_opt, key.lower(),
                    self._fitting_parameters['fitting']['FitOpt'][key])

    def _set_vary(self):
        """Prepare the vary list."""
        for i in range(len(self._fitting_parameters['fitting']['Vary'])):
            vary_dict = collections.OrderedDict()
            for key in self._fitting_parameters['fitting']['Vary'][i]:
                vary_dict[key.lower()] = \
                    self._fitting_parameters['fitting']['Vary'][i][key]
            self._vary.append(vary_dict)

    def _perform_fitting(self):
        """Call specprofi_oop.SpecProFi to fit the dataset."""
        number_of_datasets = len(self._fitting_parameters['datasets'])
        if number_of_datasets == 1:
            spf.SpecProFi(self._y_data,
                          self._sys,
                          self._vary,
                          self._exp,
                          self._opt,
                          self._fit_opt,
                          self._fitting_parameters).fit()
        else:
            spf.SpecProFi(tuple(self._y_data),
                          self._sys,
                          self._vary,
                          tuple(self._exp_list),
                          self._opt,
                          self._fit_opt,
                          self._fitting_parameters).fit()


if __name__ == '__main__':
    import trepr.io
    import trepr.dataset
    import trepr.processing
    import aspecd.utils
    imp = trepr.io.SpeksimImporter(
        '/home/popp/nas/DatenBA/PCDTBT-PET-RNK-asCast/X-Band/080K/messung06/')
    data_set = trepr.dataset.Dataset()
    data_set.import_from(imp)
    pretrigger = trepr.processing.PretriggerOffsetCompensation()
    data_set.process(pretrigger)
    averaging = trepr.processing.Averaging(0, [4.e-7, 6.e-7], 'axis')
    data_set.process(averaging)
    yaml = aspecd.utils.Yaml()
    yaml.read_from('specprofi-input.yaml')
    parameter_dict = yaml.dict
    obj = SpecProFiInterface(parameter_dict, data_set)
    obj.fit()
