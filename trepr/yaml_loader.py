"""
Yaml loader.

Yaml-files are a good way to generate files that are both human and machine
readable.

This module imports yaml-files and writes the information to a dictionary.
"""

import yaml


class YamlLoader:
    """Load yaml-files and write the information to a dictionary."""

    def __init__(self, filename=''):
        self.filename = filename
        self._read_yaml_file()

    def _read_yaml_file(self):
        with open(self.filename, 'r') as stream:
            self.yaml_dict = yaml.load(stream)


if __name__ == '__main__':
    obj = YamlLoader('metadata_mapper.yaml')
    for key in obj.yaml_dict.keys():
        if key == 'format':
            pass
        else:
            print(obj.yaml_dict[key]['infofile versions'])
