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


class Reporter:
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

    def __init__(self, dataset_=None, source=''):
        """
        Create a report rendering a template and store all files in the
        dataset repository.
        """
        # public properties
        self.dataset = dataset_
        self.path = source
        # protected properties
        self._latex_jinja_env = jinja2.Environment()
        self._temp_dir = tempfile.mkdtemp()
        self._metadata = None
        self._date = None
        self._processing_steps = collections.OrderedDict()
        self._avg_parameter = dict()
        self._render_dict = collections.OrderedDict()
        # calls to methods
        self._define_jinja_env()
        self._copy_figures_to_temp_dir()
        self._prepare_metadata()
        self._get_processing_steps()
        self._get_current_date()
        self._create_render_dict()
        self._create_report()
        self._copy_files_to_path()

    def _define_jinja_env(self):
        """Define the commands for Jinja2."""
        self._latex_jinja_env = jinja2.Environment(
            block_start_string='%{',
            block_end_string='}%',
            variable_start_string='{@',
            variable_end_string='}',
            comment_start_string='%#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader(os.path.abspath('.'))
        )

    def _copy_figures_to_temp_dir(self):
        shutil.copy2(os.path.join(self.path, 'Plotter1D.pdf'),
                     os.path.join(self._temp_dir, 'Plotter1D.pdf'))
        shutil.copy2(os.path.join(self.path, 'Plotter2D.pdf'),
                     os.path.join(self._temp_dir, 'Plotter2D.pdf'))

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
                self._avg_parameter['gemittelt über'] = \
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

    def _create_render_dict(self):
        """Create a dictionary containing all data to write the report."""
        self._render_dict['PROCESSINGSTEPS'] = self._processing_steps
        self._render_dict['METADATA'] = self._metadata
        self._render_dict['DATE'] = self._date
        self._render_dict['PROCESSINGPARAMETERS'] = self._avg_parameter

    def _create_report(self):
        self._render_template()
        self._compile_report(self._temp_dir)

    def _render_template(self):
        """Render the template and generate a latex report."""
        template = self._latex_jinja_env.get_template('report.tex')
        report = template.render(self._render_dict)
        with open(os.path.join(self.path, 'report.tex'), mode='w+') as f:
            f.write(report)
        shutil.copy2(os.path.join(self.path, 'report.tex'),
                     os.path.join(self._temp_dir, 'report.tex'))

    @staticmethod
    def _compile_report(temp_dir=None):
        """Compile the latex report to a pdf."""
        dir_path = os.getcwd()
        os.chdir(temp_dir)
        input_path = os.path.join(temp_dir, 'report.tex')
        output_path = temp_dir
        subprocess.run(["pdflatex", '-output-directory', output_path,
                        input_path])
        os.chdir(dir_path)

    def _copy_files_to_path(self):
        """
        Copy all files to the repository containing the dataset and delete
        the temporary repository.
        """
        shutil.copy2(os.path.join(self._temp_dir, 'report.pdf'),
                     os.path.join(self.path, 'report.pdf'))
        shutil.rmtree(self._temp_dir)


if __name__ == '__main__':
    obj = Reporter()
