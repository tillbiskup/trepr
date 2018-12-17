"""
General facilities to call the trepr package with a YAML file.

In terms of usability, this module serves as an interface between the
user and the trepr package.

The operation is designed in such a way that a YAML file is transferred to the
module as a recipe and the module ensures that all necessary steps are carried
out.
"""

import os

import aspecd.plotting
from aspecd import utils
from trepr import dataset
from trepr import io
from trepr import plotting
from trepr import processing
from trepr import report


class Caller:
    """Read a given YAML file and execute all demanded methods.

    Parameters
    ----------
    yaml_filename : str
        Name of the YAML file containing the recipe for generating the report.

    Attributes
    ----------
    yaml_filename : str
        Name of the YAML file containing the recipe for generating the report.

    """

    def __init__(self, yaml_filename=''):
        # public properties
        self.yaml_filename = yaml_filename
        # protected properties
        self._dataset = dataset.Dataset()
        self._path = ''
        self._yaml_dict = None
        self._figures = list()
        # calls to methods
        self._load_yaml()
        self._import_dataset()
        self._create_figures()
        self._create_report()

    def _load_yaml(self):
        yamlfile = io.YamlLoader(filename=self.yaml_filename)
        self._yaml_dict = yamlfile.yaml_dict

    def _import_dataset(self):
        self._path = self._yaml_dict['dataset']['path']
        if self._path is None:
            raise FileNotFoundError('No path given.')
        elif not os.path.isdir(self._path):
            raise FileNotFoundError('Path not found.')
        else:
            imp = io.SpeksimImporter(source=self._path)
            self._dataset.import_from(imp)

    def _create_figures(self):
        for figure in self._yaml_dict['figures']:
            for key in figure:
                if figure[key]['pretrigger compensation']:
                    pretrigger_offset = \
                        processing.PretriggerOffsetCompensation()
                    self._dataset.process(pretrigger_offset)
                if figure[key]['averaging']:
                    average_range = figure[key]['average range']
                    average_dimension = figure[key]['average dimension']
                    average_unit = figure[key]['average unit']
                    average = processing.Averaging(dimension=average_dimension,
                                                   avg_range=average_range,
                                                   unit=average_unit)
                    self._dataset.process(average)
                else:
                    pass
                plotter_obj = utils.object_from_class_name('plotting.' + key)
                if figure[key]['filename']:
                    plotter_obj.filename = figure[key]['filename']
                    self._figures.append(os.path.join(
                        self._path, plotter_obj.filename))
                else:
                    plotter_obj.filename = key + '.pdf'
                    self._figures.append(os.path.join(
                        self._path, plotter_obj.filename))
                plot = self._dataset.plot(plotter_obj)
                saver_obj = \
                    aspecd.plotting.Saver()
                saver_obj.filename = os.path.join(self._path, plotter_obj.filename)
                if figure[key]['save options']:
                    saver_obj.parameters = figure[key]['save options']
                else:
                    pass
                plot.save(saver_obj)

    def _create_report(self):
        template = self._yaml_dict['report']['template']
        filename = self._yaml_dict['report']['filename']
        if self._yaml_dict['report']:
            report_ = \
                report.Reporter(dataset_=self._dataset, source=self._path,
                                template=template, filename=filename)
            report_.includes = self._figures
            report_.create()
            report_.compile()
        else:
            pass


if __name__ == '__main__':
    obj = Caller('report.yaml')
