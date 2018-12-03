"""
Caller.

In terms of user friendliness, this module serves as an interface between the
user and the trepr package.

The operation is designed in such a way that a YAML file is transferred to the
module as a recipe and the module ensures that all necessary steps are carried
out.
"""

import os

from aspecd import utils
#from jinja_report import jinja_report
from trepr import dataset
from trepr import io
from trepr import plotter
from trepr import processing
from trepr import report
from trepr import saver
from trepr import yaml_loader


class Caller:
    """Read a given yaml-file and execute all demanded methods.

    Parameters
    ----------
    yamlfilename : str
        Name of the yaml-file containing the recipe for generating the report.

    Attributes
    ----------
    yamlfilename : str
        Name of the yaml-file containing the recipe for generating the report.

    """

    def __init__(self, yamlfilename=''):
        # public properties:
        self.yamlfilename = yamlfilename
        # protected properties:
        self._dataset = None
        self._path = ''
        self._yaml_dict = None
        # calls to methods:
        self._load_yaml()
        self._import_dataset()
        self._create_figures()
        self._create_report()

    def _load_yaml(self):
        yamlfile = yaml_loader.YamlLoader(filename=self.yamlfilename)
        self._yaml_dict = yamlfile.yaml_dict

    def _import_dataset(self):
        self._path = self._yaml_dict['dataset']['path']
        if self._path is None:
            raise FileNotFoundError('No path given.')
        elif not os.path.isdir(self._path):
            raise FileNotFoundError('Path not found.')
        else:
            imp = io.Importer(source=self._path)
            self._dataset = dataset.Dataset()
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
                plotter_obj = utils.object_from_class_name('plotter.' + key)
                plotter_obj.dataset = self._dataset
                # TODO: Dateinamen woanders her suchen (YAML-Datei?)
                name = key + '.pdf'
                saver_obj = saver.Saver(os.path.join(self._path, name))
                plot = self._dataset.plot(plotter_obj)
                plot.save(saver_obj)

    def _create_report(self):
        if self._yaml_dict['report']:
            self.report = report.Report(
                dataset=self._dataset, source=self._path)
        else:
            pass


if __name__ == '__main__':
    obj = Caller('report.yaml')
