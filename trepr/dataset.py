"""
To produce replicable results it's important not to change the raw data.

This module creates a dataset structure, inheriting from the ASpecD dataset
class. The dataset structure contains metadata, consisting of different
classes, which contain the individual information about the experiment.
"""

import aspecd.dataset
import aspecd.metadata
from trepr import io


class Dataset(aspecd.dataset.Dataset):
    """Define the structure for a given dataset, inheriting from ASpecD.

    The "raison d'être" for this class is mainly to extend the metadata
    contained in the metadata property.

    Attributes
    ----------
    metadata : :class:`trepr.dataset.DatasetMetadata`
        Metadata of dataset.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.metadata = DatasetMetadata()
        self.time_stamp = aspecd.dataset.Data()
        self.microwave_frequency = aspecd.dataset.Data()


class DatasetMetadata(aspecd.metadata.DatasetMetadata):
    """Metadata for a TREPR dataset.

    Attributes
    ----------
    measurement : :obj:`trepr.dataset.Measurement`
        Metadata corresponding to the measurement.

    sample : :obj:`trepr.dataset.Sample`
        Metadata corresponding to the sample.

    transient : :obj:`trepr.dataset.Transient`
        Metadata corresponding to the transient.

    experiment : :obj:`trepr.dataset.Experiment`
        Metadata corresponding to the experiment.

    spectrometer : :obj:`trepr.dataset.Spectrometer`
        Metadata corresponding to the spectrometer.

    magnetic_field : :obj:`trepr.dataset.MagneticField`
        Metadata corresponding to the magnetic field.

    background : :obj:`trepr.dataset.Background`
        Metadata corresponding to the background.

    bridge : :obj:`trepr.dataset.Bridge`
        Metadata corresponding to the bridge.

    viedo_amplifier : :obj:`trepr.dataset.VideoAmplifier`
        Metadata corresponding to the video amplifier.

    recorder : :obj:`trepr.dataset.Recorder`
        Metadata corresponding to the recorder.

    probehead : :obj:`trepr.dataset.Probehead`
        Metadata corresponding to the probehead.

    pump : :obj:`trepr.dataset.Pump`
        Metadata corresponding to the pump.

    temperature_control : :obj:`trepr.dataset.TemperatureControl`
        Metadata corresponding to the temperature control.

    """

    def __init__(self):
        super().__init__()
        # public properties
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

    """

    def __init__(self, dict_=None):
        # public properties
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

    preparation : str
        Type of sample preparation.

    tube : str
        Dimension of the tube used.

    """

    def __init__(self, dict_=None):
        # public properties
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
        # public properties
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

    shot_repetition_rate : :obj:`aspecd.metadata.PhysicalQuantity`
        Shot repetition rate of the experiment.

    """

    def __init__(self, dict_=None):
        # public properties
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
        # public properties
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

    start : :obj:`aspecd.metadata.PhysicalQuantity`
        Start of the magnetic field sweep.

    stop: :obj:`aspecd.metadata.PhysicalQuantity`
        End of the magnetic field sweep.

    step : :obj:`aspecd.metadata.PhysicalQuantity`
        Step size of the magnetic field sweep.

    sequence : str
        Sequence of field steps.

    controller : str
        Model of the controller used.

    power_supply : str
        Model of the power supply used.

    """

    def __init__(self, dict_=None):
        # public properties
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
    field : :obj:`aspecd.metadata.PhysicalQuantity`
        Magnetic field position of background trace.

    occurence : int
        Number of time traces after which a background trace is recorded.

    polarisation: str
        Type of background polarisation.

    intensity : :obj:`aspecd.metadata.PhysicalQuantity`
        Amplitude of background signal.

    """

    def __init__(self, dict_=None):
        # public properties
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
        Model of the microwave bridge used.

    controller : str
        Model of the bridge controller used.

    attenuation : :obj:`aspecd.metadata.PhysicalQuantity`
        Attenuation of the microwave in dB.

    power : :obj:`aspecd.metadata.PhysicalQuantity`
        Output power of the microwave.

    detection : str
        Type of the detection used.

    frequency_counter : str
        Model of the frequency counter used.

    mw_frequency : :obj:`aspecd.metadata.PhysicalQuantity`
        Microwave frequency.

    """

    def __init__(self, dict_=None):
        # public properties
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
    bandwidth : :obj:`aspecd.metadata.PhysicalQuantity`
        Bandwidth of the video amplifier.

    amplification : :obj:`aspecd.metadata.PhysicalQuantity`
        Amplification in dB.

    """

    def __init__(self, dict_=None):
        # public properties
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

    time_base : :obj:`aspecd.metadata.PhysicalQuantity`
        Time base of the recorder.

    bandwidth : :obj:`aspecd.metadata.PhysicalQuantity`
        Bandwidth of the recorder.

    pretrigger : :obj:`aspecd.metadata.PhysicalQuantity`
        Length of time trace before trigger.

    coupling : str
        Type of coupling.

    impedance : :obj:`aspecd.metadata.PhysicalQuantity`
        Impedance of the recorder input channel.

    sensitivity : :obj:`aspecd.metadata.PhysicalQuantity`
        Sensitivity of the recorder.

    """

    def __init__(self, dict_=None):
        # public properties
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
        # public properties
        self.type = ''
        self.model = ''
        self.coupling = ''
        super().__init__(dict_=dict_)


class Pump(aspecd.metadata.Metadata):
    """Metadata corresponding to the optical excitation..

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

    wavelength : :obj:`aspecd.metadata.PhysicalQuantity`
        Wavelength of the optical excitation.

    power : :obj:`aspecd.metadata.PhysicalQuantity`
        Power of the optical excitation.

    repetition_rate : :obj:`aspecd.metadata.PhysicalQuantity`
        Repetition rate of the optical excitation.

    tunable_type : str
        Type of the tunable used.

    tunable_model : str
        Model of the tunable used.

    tunable_dye : str
        Name of Laser dye.

    tunable_position : int
        Position of the tunable used.

    filter : str
        Type of the filter(s) used.

    """

    def __init__(self, dict_=None):
        # public properties
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
        # public properties
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)


class MetadataMapper(aspecd.metadata.MetadataMapper):
    """Bring the metadata into a unified layout using mappings.

    Given the version number and metadata read from an infofile, the metadata
    are converted into a structure compatible to the dataset.

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

    """

    def __init__(self, version='', metadata=None):
        super().__init__()
        # public properties
        self.version = version
        self.metadata = metadata
        # protected properties
        self._map_recipe = dict()
        self._yaml_dict = dict()
        # calls to methods
        self._load_yaml()
        self._get_mapping_recipe()
        self._create_mappings()
        self.map()

    def _load_yaml(self):
        """Load the YAML file containing the map recipes."""
        yaml_file = io.YamlLoader('metadata_mapper.yaml')
        self._yaml_dict = yaml_file.yaml_dict

    def _get_mapping_recipe(self):
        """Get the right map recipe out of the YAML file."""
        for key in self._yaml_dict.keys():
            if key != 'format':
                if self.version in self._yaml_dict[key]['infofile versions']:
                    self._map_recipe = self._yaml_dict[key]

    def _create_mappings(self):
        """Create mappings out of the map recipe."""
        if 'copy key' in self._map_recipe.keys():
            for i in range(len(self._map_recipe['copy key'])):
                mapping = \
                    [self._map_recipe['copy key'][i]['in dict'],
                     'copy_key',
                     [self._map_recipe['copy key'][i]['old key'],
                      self._map_recipe['copy key'][i]['new key']]]
                self.mappings.append(mapping)
        if 'combine items' in self._map_recipe.keys():
            for i in range(len(self._map_recipe['combine items'])):
                mapping = \
                    [self._map_recipe['combine items'][i]['in dict'],
                     'combine_items',
                     [self._map_recipe['combine items'][i]['old keys'],
                      self._map_recipe['combine items'][i]['new key'],
                      self._map_recipe['combine items'][i]['pattern']]]
                self.mappings.append(mapping)
        if 'rename key' in self._map_recipe.keys():
            for i in range(len(self._map_recipe['rename key'])):
                mapping = \
                    [self._map_recipe['rename key'][i]['in dict'],
                     'rename_key',
                     [self._map_recipe['rename key'][i]['old key'],
                      self._map_recipe['rename key'][i]['new key']]]
                self.mappings.append(mapping)
        if 'move item' in self._map_recipe.keys():
            for i in range(len(self._map_recipe['move item'])):
                mapping = \
                    ['', 'move_item',
                     [self._map_recipe['move item'][i]['key'],
                      self._map_recipe['move item'][i]['source dict'],
                      self._map_recipe['move item'][i]['target dict'], True]]
                self.mappings.append(mapping)
        else:
            pass


if __name__ == '__main__':
    map_ = MetadataMapper()
