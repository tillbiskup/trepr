"""
General facilities to generate a report.

To do scientific research in terms of reproducibility and traceability it's
highly necessary to report all the steps done on a given dataset and never
separate the dataset from its metadata.

This module provides functionality to create a report containing a 1D and 2D
plot of the dataset, its metadata and all processing steps including
parameters.
"""

import collections
import os
import shutil
import subprocess
import tempfile
import time

import jinja2
import numpy as np

import aspecd.report


class Reporter(aspecd.report.LaTeXReporter):
    """
    Generate a report based on a LaTeX template provided.

    Parameters
    ----------
    dataset_ : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw data as well as metadata.

    source : str
        Path to the dataset.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw dat as well as metadata.

    path : str
        Path to the dataset.

    """

    def __init__(self, dataset_=None, source='', template='', filename=''):
        """
        Create a report rendering a template and store all files in the
        dataset repository.
        """
        # public properties
        super().__init__()
        self.dataset = dataset_
        self.path = source
        self.template = template
        self.filename = filename
        self.context = None
        # protected properties
        self._latex_jinja_env = jinja2.Environment()
        self._temp_dir = tempfile.mkdtemp()
        self._metadata = None
        self._date = None
        self._processing_steps = collections.OrderedDict()
        self._avg_parameter = dict()
        self.context = collections.OrderedDict()
        # calls to methods
        self._prepare_metadata()
        self._get_processing_steps()
        self._get_current_date()
        self._create_context()

    def _prepare_metadata(self):
        """Prepare the metadata the way it can be rendered."""
        self._metadata = self.dataset.metadata.to_dict()
        self._metadata = self._change_keys_in_dict_recursively(self._metadata)
        self._metadata['Parameter'] = collections.OrderedDict()
        for key in self._metadata.keys():
            if key not in ['Sample', 'Measurement', 'Parameter']:
                self._metadata['Parameter'][key] = \
                    self._metadata[key]

    def _get_processing_steps(self):
        for history_record in self.dataset.history:
            self._processing_steps[history_record.processing.description] = \
                history_record.processing.parameters
            if history_record.processing.description == 'Averaging':
                self._avg_parameter['Schnitt bei'] = \
                    np.average(history_record.processing.parameters['range'])
                self._avg_parameter['gemittelt ueber'] = \
                    history_record.processing.parameters['range'][1] - \
                    history_record.processing.parameters['range'][0]
        self._processing_steps = \
            self._change_keys_in_dict_recursively(self._processing_steps)

    @staticmethod
    def _change_keys_in_dict_recursively(dict_=None):
        tmp_dict = collections.OrderedDict()
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = Reporter._change_keys_in_dict_recursively(value)
            tmp_dict[key.replace('_', ' ').capitalize()] = dict_[key]
        return tmp_dict

    def _get_current_date(self):
        """Get the current date."""
        self._date = time.strftime('%d.%m.%Y')

    def _create_context(self):
        """Create a dictionary containing all data to write the report."""
        self.context['PROCESSINGSTEPS'] = self._processing_steps
        self.context['METADATA'] = self._metadata
        self.context['DATE'] = self._date
        self.context['PROCESSINGPARAMETERS'] = self._avg_parameter


if __name__ == '__main__':
    template = 'report.tex'
    filename = 'test.tex'
    report_ = LaTeXReporter(template, filename)
    report_.create()
    report_.compile()

