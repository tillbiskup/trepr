import yaml


class YamlLoader:

    def __init__(self, filename=''):
        self.filename = filename
        self._read_yaml_file()

    def _read_yaml_file(self):
        with open(self.filename, 'r') as stream:
            self.yaml_dict = yaml.load(stream)


if __name__ == '__main__':
    obj = YamlLoader('importer.yaml')
    print(obj.yaml_dict)
