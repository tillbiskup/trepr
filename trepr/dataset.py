"""
To produce replicable results it's important not to change the raw data.

This module creates a dataset structure, inheriting from the aspecd dataset
class.
"""

import aspecd.dataset
import aspecd.metadata


class Dataset(aspecd.dataset.Dataset):
    """Define the structure for a given dataset, inheriting from ASpecD."""

    def __init__(self):
        super().__init__()
        self.metadata = DatasetMetadata()


class DatasetMetadata(aspecd.metadata.DatasetMetadata):
    """Metadata for a given dataset."""

    def __init__(self):
        super().__init__()
        self.recorder = Recorder()
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
    """Metadata corresponding to the measurement."""

    def __init__(self, dict_=None):
        self.label = ''
        self.spectrometer = ''
        self.software = ''
        self.runs = None
        self.shot_repetition_rate = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):
    """Metadata corresponding to the sample."""

    def __init__(self, dict_=None):
        self.description = ''
        self.solvent = ''
        self.preperation = ''
        self.tube = ''
        super().__init__(dict_=dict_)


class Transient(aspecd.metadata.Metadata):
    """Metadata corresponding to the transient."""

    def __init__(self, dict_=None):
        self.points = None
        self.length = aspecd.metadata.PhysicalQuantity()
        self.trigger_position = None
        super().__init__(dict_=dict_)


class Experiment(aspecd.metadata.Metadata):
    """Metadata corresponding to the experiment."""

    def __init__(self, dict_=None):
        self.runs = None
        self.shot_repetition_rate = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Spectrometer(aspecd.metadata.Metadata):
    """Metadata corresponding to the spectrometer."""

    def __init__(self, dict_=None):
        self.model = ''
        self.software = ''
        super().__init__(dict_=dict_)


class MagneticField(aspecd.metadata.Metadata):
    """Metadata corresponding to the magnetic field."""

    def __init__(self, dict_=None):
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
    """Metadata corresponding to the background."""

    def __init__(self, dict_=None):
        self.field = aspecd.metadata.PhysicalQuantity()
        self.occurrence = None
        self.polarisation = ''
        self.intensity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):
    """Metadata corresponding to the bridge."""

    def __init__(self, dict_=None):
        self.model = ''
        self.controller = ''
        self.attenuation = aspecd.metadata.PhysicalQuantity()
        self.power = aspecd.metadata.PhysicalQuantity()
        self.detection = ''
        self.frequency_counter = ''
        self.mw_frequency = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class VideoAmplifier(aspecd.metadata.Metadata):
    """Metadata corresponding to the video amplifier."""

    def __init__(self, dict_=None):
        self.bandwidth = aspecd.metadata.PhysicalQuantity()
        self.amplification = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Recorder(aspecd.metadata.Metadata):
    """Metadata corresponding to the recorder."""

    def __init__(self, dict_=None):
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
    """Metadata corresponding to the probehead."""

    def __init__(self, dict_=None):
        self.type = ''
        self.model = ''
        self.coupling = ''
        super().__init__(dict_=dict_)


class Pump(aspecd.metadata.Metadata):
    """Metadata corresponding to the pump."""

    def __init__(self, dict_=None):
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
    """Metadata corresponding to the temperature control."""

    def __init__(self, dict_=None):
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)


class MetadataMapper():

    def __init__(self):
        self.metadata = dict()

    def rename_key(self, old_key='', new_key=''):
        self.metadata[new_key] = self.metadata.pop(old_key)

    def combine_items(self, old_keys=None, new_key=''):
        value_tmp = list()
        for key in old_keys:
            value_tmp.append(self.metadata.pop(key))
        self.metadata[new_key] = ' '.join(value_tmp)



if __name__ == '__main__':
    metadata_dict = {'recorder': {'Averages': 500, 'Impedance': '50 Ohm', 'Time base': '2 ns'}}
    dataset = Dataset()
    dataset.metadata.from_dict(metadata_dict)
    print(dataset.metadata.recorder.time_base)
