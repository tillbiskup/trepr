"""To do scientific research in terms of reproducibility and traceability it's
 highly necessary to report all the steps done on a given dataset and never
 seperate the dataset from its metadata.

 This module creates a pdf report containing a 1D and 2D plot of the dataset,
 its metadata and all processing steps including parameters.
 """
import collections
import numpy as np
import os
import shutil
import subprocess
import tempfile
import time

import jinja2


class Report:

    def __init__(self, dataset=None, source=''):
        """Create a report rendering a template and store all files in the
        dataset repository.
        """
        # public properties
        self.dataset = dataset
        self.path = source
        # protected properties
        self._define_jinja_env()
        self._copy_figures_to_temp_dir()
        self._make_keys_in_dict_latex_compatible()
        self._prepare_metadata()
        self._get_current_date()
        self._get_processing_steps()
        self._create_render_dict()
        self._render_template()
        self._write_report()
        self._copy_files_to_path()

    def _define_jinja_env(self):
        """Define the commands for Jinja2."""
        self.latex_jinja_env = jinja2.Environment(
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
        self.temp_dir = tempfile.mkdtemp()
        shutil.copy2(os.path.join(self.path, 'Plotter1D.pdf'),
                     os.path.join(self.temp_dir, 'Plotter1D.pdf'))
        shutil.copy2(os.path.join(self.path, 'Plotter2D.pdf'),
                     os.path.join(self.temp_dir, 'Plotter2D.pdf'))

    def _make_keys_in_dict_latex_compatible(self):
        self.metadata = self.dataset.metadata.to_dict()
        self.metadata = self._change_keys_in_dict_recursively(self.metadata)

    @staticmethod
    def _change_keys_in_dict_recursively(dict_=None):
        tmp_dict = collections.OrderedDict()
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = Report._change_keys_in_dict_recursively(value)
            tmp_dict[key.replace('_', ' ').capitalize()] = dict_[key]
        return tmp_dict

    def _prepare_metadata(self):
        """Prepare the metadata the way it can be rendered."""
        self.metadata['Parameter'] = collections.OrderedDict()

        for key in self.metadata.keys():
            if key not in ['Sample', 'Measurement', 'Parameter']:
                self.metadata['Parameter'][key] = \
                    self.metadata[key]

    def _get_current_date(self):
        """Get the current date."""
        self.date = time.strftime('%d.%m.%Y')

    def _get_processing_steps(self):
        self.processing_steps = dict()
        self.avg_parameter = dict()
        for history_record in self.dataset.history:
            self.processing_steps[history_record.processing.description] = \
                history_record.processing.parameters
            if history_record.processing.description is 'Averaging':
                self.avg_parameter['Schnitt bei'] = \
                    np.average(history_record.processing.parameters['range'])
                self.avg_parameter['gemittelt über'] = \
                    history_record.processing.parameters['range'][1]-\
                    history_record.processing.parameters['range'][0]
        self.processing_steps = \
            self._change_keys_in_dict_recursively(self.processing_steps)

    def _create_render_dict(self):
        """Create a dictionary containing all data to write the report."""
        self._render_dict = collections.OrderedDict()
        self._render_dict['PROCESSINGSTEPS'] = self.processing_steps
        self._render_dict['METADATA'] = self.metadata
        self._render_dict['DATE'] = self.date
        self._render_dict['PROCESSINGPARAMETERS'] = self.avg_parameter

    def _render_template(self):
        """Render the template and generate a latex report."""
        self.template = self.latex_jinja_env.get_template('jinja_test.tex')
        self.report = self.template.render(self._render_dict)
        with open(os.path.join(self.path, 'report.tex'), mode='w+') as f:
            f.write(self.report)
        shutil.copy2(os.path.join(self.path, 'report.tex'),
                     os.path.join(self.temp_dir, 'report.tex'))

    def _write_report(self):
        """Compile the latex report to a pdf."""
        dir_path = os.getcwd()
        os.chdir(self.temp_dir)
        self.input_path = os.path.join(self.temp_dir, 'report.tex')
        self.output_path = self.temp_dir
        subprocess.run(["pdflatex", '-output-directory', self.output_path,
                        self.input_path])
        os.chdir(dir_path)

    def _copy_files_to_path(self):
        """Copy all files to the repository containing the dataset and delet
        the temporary repository."""
        shutil.copy2(os.path.join(self.temp_dir, 'report.pdf'),
                     os.path.join(self.path, 'report.pdf'))
        shutil.rmtree(self.temp_dir)


if __name__ == '__main__':
    obj = Report()
