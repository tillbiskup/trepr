"""
To produce replicable results it's important not to change the raw data.

This module creates a dataset structure, inheriting from the aspecd dataset
class. The dataset structure contains metadata, consisting of different
classes, which contain the individual information about the experiment.
"""

import aspecd.dataset
import aspecd.metadata
from trepr import yaml_loader


class Dataset(aspecd.dataset.Dataset):
    """Define the structure for a given dataset, inheriting from ASpecD.

    Attributes
    ----------
    metadata : :class:`trepr.dataset.DatasetMetadata`
        Object of the DatasetMetadata class.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.metadata = DatasetMetadata()


class DatasetMetadata(aspecd.metadata.DatasetMetadata):
    """Metadata for a given dataset.

    Attributes
    ----------
    measurement : :obj:`trepr.dataset.Measurement`
        Object of the Measurement class.

    sample : :obj:`trepr.dataset.Sample`
        Object of the Sample class.

    transient : :obj:`trepr.dataset.Transient`
        Object of the Transient class.

    experiment : :obj:`trepr.dataset.Experiment`
        Object of the Experiment class.

    spectrometer : :obj:`trepr.dataset.Spectrometer`
        Object of the Spectrometer class.

    magnetic_field : :obj:`trepr.dataset.MagneticField`
        Object of the MagneicField class.

    background : :obj:`trepr.dataset.Background`
        Object of the Background class.

    bridge : :obj:`trepr.dataset.Bridge`
        Object of the Bridge class.

    viedo_amplifier : :obj:`trepr.dataset.VideoAmplifier`
        Object of the VideoAmplifier class.

    recorder : :obj:`trepr.dataset.Recorder`
        Object of the Recorder class.

    probehead : :obj:`trepr.dataset.Probehead`
        Object of the Probehead class.

    pump : :obj:`trepr.dataset.Pump`
        Object of the Pump class.

    temperature_control : :obj:`trepr.dataset.TemperatureControl`
        Object of the TemperatureControl class.

    """

    def __init__(self):
        super().__init__()
        # public properies
        self.measurement = Measurement()
        self.sample = Sample()
        self.transient = Transient()
        self.experiment = Experiment()
        self.spectrometer = Spectrometer()
        self.magnetic_field = MagneticField()
        self.background = Background()
        self.bridge = Bridge()
        self.video_amplifier = VideoAmplifier()
        self.recorder = Recorder()
        self.probehead = Probehead()
        self.pump = Pump()
        self.temperature_control = TemperatureControl()


class Measurement(aspecd.metadata.Measurement):
    """Metadata corresponding to the measurement.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    label : str
        Label of the sample, including the sample-number.

    spectrometer : str
        Model of the spectrometer used.

    software : str
        Name and version of the software used.

    runs : int
        Number of recorded runs.

    shot_repetition_rate : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.label = ''
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):
    """Metadata corresponding to the sample.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    description : str
        Description of the measured sample.

    solvent : str
        Name of the solvent used.

    preperation : str
        Type of sample preparation.

    tube : str
        Dimension of the tube used.

    """

    def __init__(self, dict_=None):
        # public properies
        self.description = ''
        self.solvent = ''
        self.preparation = ''
        self.tube = ''
        super().__init__(dict_=dict_)


class Transient(aspecd.metadata.Metadata):
    """Metadata corresponding to the transient.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    points : int
        Number of measuring points.

    length : object
        Object of the PhysicalQuantity class from ASpecD.

    trigger_position : int
        Position of the trigger.

    """

    def __init__(self, dict_=None):
        # public properies
        self.points = None
        self.length = aspecd.metadata.PhysicalQuantity()
        self.trigger_position = None
        super().__init__(dict_=dict_)


class Experiment(aspecd.metadata.Metadata):
    """Metadata corresponding to the experiment.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
     runs : int
        Number of recorded runs.

    shot_repetition_rate : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.runs = None
        self.shot_repetition_rate = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Spectrometer(aspecd.metadata.Metadata):
    """Metadata corresponding to the spectrometer.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    model : str
        Model of the spectrometer used.

    software : str
        Name and version of the software used.

    """

    def __init__(self, dict_=None):
        # public properies
        self.model = ''
        self.software = ''
        super().__init__(dict_=dict_)


class MagneticField(aspecd.metadata.Metadata):
    """Metadata corresponding to the magnetic field.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    fiels_probe_type : str
        Type of field probe used.

    field_probe_model : str
        Model of field probe used.

    start : object
        Object of the PhysicalQuantity class from ASpecD.

    stop: object
        Object of the PhysicalQuantity class from ASpecD.

    step : object
        Object of the PhysicalQuantity class from ASpecD.

    sequence : str
        Sequence of measurement performed.

    controller : str
        Model of the controller used.

    power_supply : str
        Model of the power supply used.

    """

    def __init__(self, dict_=None):
        # public properies
        self.field_probe_type = ''
        self.field_probe_model = ''
        self.start = aspecd.metadata.PhysicalQuantity()
        self.stop = aspecd.metadata.PhysicalQuantity()
        self.step = aspecd.metadata.PhysicalQuantity()
        self.sequence = ''
        self.controller = ''
        self.power_supply = ''
        super().__init__(dict_=dict_)


class Background(aspecd.metadata.Metadata):
    """Metadata corresponding to the background.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    field : object
        Object of the PhysicalQuantity class from ASpecD.

    occurence : int
        Number of time traces after which a background trace is recorded.

    polarisation: str
        Type of background polarisation.

    intensity : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.field = aspecd.metadata.PhysicalQuantity()
        self.occurrence = None
        self.polarisation = ''
        self.intensity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):
    """Metadata corresponding to the bridge.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    model : str
        Model of the bridge used.

    controller : str
        Model of the controller used.

    attenuation : object
        Object of the PhysicalQuantity class from ASpecD.

    power : object
        Object of the PhysicalQuantity class from ASpecD.

    detection : str
        Type of the detection used.

    frequency_counter : str
        Model of the frequency counter used.

    mw_frequency : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.model = ''
        self.controller = ''
        self.attenuation = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.detection = ''
        self.frequency_counter = ''
        self.mw_frequency = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class VideoAmplifier(aspecd.metadata.Metadata):
    """Metadata corresponding to the video amplifier.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    bandwith : object
        Object of the PhysicalQuantity class from ASpecD.

    amplification : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.bandwidth = aspecd.metadata.PhysicalQuantity()
        self.amplification = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Recorder(aspecd.metadata.Metadata):
    """Metadata corresponding to the recorder.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    model : str
        Model of the recorder used.

    averages : int
        Number of accumulations measured.

    time_base : object
        Object of the PhysicalQuantity class from ASpecD.

    bandwith : object
        Object of the PhysicalQuantity class from ASpecD.

    pretrigger : object
        Object of the PhysicalQuantity class from ASpecD.

    coupling : str
        Type of coupling.

    impedance : object
        Object of the PhysicalQuantity class from ASpecD.

    sensitivity : object
        Object of the PhysicalQuantity class from ASpecD.

    """

    def __init__(self, dict_=None):
        # public properies
        self.model = ''
        self.averages = None
        self.time_base = aspecd.metadata.PhysicalQuantity()
        self.bandwidth = aspecd.metadata.PhysicalQuantity()
        self.pretrigger = aspecd.metadata.PhysicalQuantity()
        self.coupling = ''
        self.impedance = aspecd.metadata.PhysicalQuantity()
        self.sensitivity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Probehead(aspecd.metadata.Metadata):
    """Metadata corresponding to the probehead.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    type : str
        Type of the probehead used.

    model : str
        Model of the probehead used.

    coupling : str
        Type of coupling.

    """

    def __init__(self, dict_=None):
        # public properies
        self.type = ''
        self.model = ''
        self.coupling = ''
        super().__init__(dict_=dict_)


class Pump(aspecd.metadata.Metadata):
    """Metadata corresponding to the pump.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    type : str
        Type of the pump used.

    model : str
        Model of the pump used.

    wavelength : object
        Object of the PhysicalQuantity class from ASpecD.

    power : object
        Object of the PhysicalQuantity class from ASpecD.

    repetition_rate : object
        Object of the PhysicalQuantity class from ASpecD.

    tunable_type : str
        Type of the tunable used.

    tunable_model : str
        Model of the tunable used.

    tunable_dye : str
        Name of Laser dye.

    tunable_position : int
        Position of the tunable used.

    filter : str
        Type of the filter used.

    """

    def __init__(self, dict_=None):
        # public properies
        self.type = ''
        self.model = ''
        self.wavelength = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.repetition_rate = aspecd.metadata.PhysicalQuantity()
        self.tunable_type = ''
        self.tunable_model = ''
        self.tunable_dye = ''
        self.tunable_position = None
        self.filter = ''
        super().__init__(dict_=dict_)


class TemperatureControl(aspecd.metadata.TemperatureControl):
    """Metadata corresponding to the temperature control.

    Parameters
    ----------
    dict_ : dict
        Dictionary containing properties to set.

    Attributes
    ----------
    cryostat : str
        Model of the cryostat used.

    cryogen : str
        Cryogen used.

    """

    def __init__(self, dict_=None):
        # public properies
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)

class MetadataMapper(aspecd.metadata.MetadataMapper):
    """Bring the metadata into a unified layout using mappings.

    Parameters
    ----------
    version : str
        Version of the imported infofile.

    metadata : dict
        Dictionary containing all metadata from the infofile.

    Attributes
    ----------
    version : str
        Version of the imported infofile.

    metadata : dict
        Dictionary containing all metadata from the infofile.

    mappings : list
        List containing all tasks to perform to map the metadata.

    """

    def __init__(self, version='', metadata=None):
        # public proterties
        self.version = version
        self.metadata = metadata
        self.mappings = list()
        # protected properties
        self._yaml_dict = dict()
        # calls to methods
        self._load_yaml()
        self._get_map_recipe()
        self._create_mappings()
        self._map_metadata()

    def _load_yaml(self):
        """Load the yaml-file containing the map recipes."""
        yamlfile = yaml_loader.YamlLoader('metadata_mapper.yaml')
        self._yaml_dict = yamlfile.yaml_dict

    def _get_map_recipe(self):
        """Get the right map recipe out of the yaml-file."""
        for key in self._yaml_dict.keys():
            if key == 'format':
                pass
            else:
                if self.version in self._yaml_dict[key]['infofile versions']:
                    self.map_recipe = self._yaml_dict[key]

    def _create_mappings(self):
        """Create mappings out of the map recipe."""
        if 'copy key' in self.map_recipe.keys():
            for i in range(len(self.map_recipe['copy key'])):
                mapping = \
                    [self.map_recipe['copy key'][i]['in dict'],
                     'copy_key', [self.map_recipe['copy key'][i]['old key'],
                                  self.map_recipe['copy key'][i]['new key']]]
                self.mappings.append(mapping)
        if 'combine items' in self.map_recipe.keys():
            for i in range(len(self.map_recipe['combine items'])):
                mapping = \
                    [self.map_recipe['combine items'][i]['in dict'],
                     'combine_items', [self.map_recipe['combine items'][i]['old keys'],
                                       self.map_recipe['combine items'][i]['new key'],
                     self.map_recipe['combine items'][i]['pattern']]]
                self.mappings.append(mapping)
        if 'rename key' in self.map_recipe.keys():
            for i in range(len(self.map_recipe['rename key'])):
                mapping = \
                    [self.map_recipe['rename key'][i]['in dict'],
                     'rename_key', [self.map_recipe['rename key'][i]['old key'],
                                    self.map_recipe['rename key'][i]['new key']]]
                self.mappings.append(mapping)
        if 'move item' in self.map_recipe.keys():
            for i in range(len(self.map_recipe['move item'])):
                mapping = \
                    ['', 'move_item', [self.map_recipe['move item'][i]['key'],
                                       self.map_recipe['move item'][i][
                                           'source dict'],
                                       self.map_recipe['move item'][i][
                                           'target dict'], True]]
                self.mappings.append(mapping)
        else:
            pass

    def _map_metadata(self):
        """Map the metadata with the created mappings."""
        aspecd.metadata.MetadataMapper.map(self)


if __name__ == '__main__':
    map = MetadataMapper()
