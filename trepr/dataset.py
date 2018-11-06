"""To produce replicable results it's important not to change the raw data.

This module creates a dataset structure, inheriting from the aspecd dataset class.
"""

import aspecd.dataset
import aspecd.metadata

class Dataset(aspecd.dataset.Dataset):

    def __init__(self):
        super().__init__()
        self.metadata = DatasetMetadata()


class DatasetMetadata(aspecd.metadata.DatasetMetadata):

    def __init__(self):
        super().__init__()
        self.recorder = Recorder()
        self.general = General()


class Measurement(aspecd.metadata.Measurement):

    def __init__(self, dict_=None):
        self.label = ''
        self.spectrometer = ''
        self.software = ''
        self.runs = None
        self.shot_repetition_rate = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):

    def __init__(self, dict_=None):
        self.description = ''
        self.solvent = ''
        self.preperation = ''
        self.tube = ''
        super().__init__(dict_=dict_)


class Transient(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.points = None
        self.length = aspecd.metadata.PhysicalQuantity()
        self.trigger_position = None
        super().__init__(dict_=dict_)


class Experiment(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.runs = None
        self.shot_repetition_rate = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Spectrometer(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.model = ''
        self.software = ''
        super().__init__(dict_=dict_)


class MagneticField(aspecd.metadata.Metadata):

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

    def __init__(self, dict_=None):
        self.field = aspecd.metadata.PhysicalQuantity()
        self.occurrence = None
        self.polarisation = ''
        self.intensity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):

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

    def __init__(self, dict_=None):
        self.bandwidth = aspecd.metadata.PhysicalQuantity()
        self.amplification = aspecd.metadata.PhysicalQuantity()


class Recorder(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.model = ''
        self.averages = None
        self.time_base = aspecd.metadata.PhysicalQuantity()
        self.bandwidth = aspecd.metadata.PhysicalQuantity()
        self.pretrigger = aspecd.metadata.PhysicalQuantity()
        self.coupling = ''
        self.impedance = aspecd.metadata.PhysicalQuantity()
        self.sensitivity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_ = dict_)


class Probehead(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.type = ''
        self.model = ''
        self.coupling = ''
        super().__init__(dict_=dict_)


class Pump(aspecd.metadata.Metadata):

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

    def __init__(self, dict_=None):
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)


class FieldCalibration(aspecd.metadata.Metadata):

    def __init__(self, dict_=None):
        self.standard = ''
        super().__init__(dict_=dict_)

if __name__ == '__main__':
    metadata_dict = {'recorder':{'Averages': 500, 'Impedance': '50 Ohm', 'Time base': '2 ns'}}
    dataset = Dataset()
    dataset.metadata.from_dict(metadata_dict)
    print(dataset.metadata.recorder.time_base)

