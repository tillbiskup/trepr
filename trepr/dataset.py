"""Datasets: units containing data and metadata.

The dataset is one key concept of the ASpecD framework and hence the trepr
package derived from it, consisting of the data as well as the corresponding
metadata. Storing metadata in a structured way is a prerequisite for a
semantic understanding within the routines. Furthermore, a history of every
processing, analysis and annotation step is recorded as well, aiming at a
maximum of reproducibility. This is part of how the ASpecD framework and
therefore the trepr package tries to support good scientific practice.

Therefore, each processing and analysis step of data should always be
performed using the respective methods of a dataset, at least as long as it
can be performed on a single dataset.


Datasets
========

Generally, there are two types of datasets: Those containing experimental
data and those containing calculated data. Therefore, two corresponding
subclasses exist, and packages building upon the ASpecD framework should
inherit from either of them:

  * :class:`trepr.dataset.ExperimentalDataset`
  * :class:`trepr.dataset.CalculatedDataset`


Metadata
========

Furthermore, in this module, the individual metadata classes are defined
which contain the individual information about the experiment:

  * :class:`trepr.dataset.ExperimentalDatasetMetadata`
  * :class:`trepr.dataset.CalculatedDatasetMetadata`

What may sound like a minor detail is one key aspect of the trepr package:
The metadata and their structure provide a unified interface for all
functionality operating on datasets. Furthermore, the metadata contained
particularly in the :class:`trepr.dataset.ExperimentalDatasetMetadata` class
are the result of more than fifteen yearsof practical experience. Reproducible
research is only possible if all information necessary is always recorded,
and this starts with all the metadata accompanying a measurement. Defining
what kind of metadata is important and needs to be recorded, together with
metadata formats easily writable by the experimenters *during* recording the
data requires a thorough understanding of both, the method and the setup(s)
used. For an overview of the structures of the dataset classes and their
corresponding metadata, see the :doc:`dataset structure </dataset-structure>`
section.


Dataset factory
===============

Particularly in case of recipe-driven data analysis (c.f. :mod:`tasks`),
there is a need to automatically retrieve datasets using nothing more than a
source string that can be, e.g., a path or LOI. This is where the
DatasetFactory comes in. This is a factory in the sense of the factory
pattern described by the "Gang of Four" in their seminal work, "Design
Patterns" (Gamma et al., 1995):

  * :class:`trepr.dataset.DatasetFactory`


Module documentation
====================

"""
import os

import aspecd.dataset
import aspecd.metadata
import aspecd.utils
import trepr.io


class Dataset(aspecd.dataset.Dataset):
    """Base class for all kinds of datasets.

    Generally, there are two types of datasets: Those containing
    experimental data and those containing calculated data. Therefore,
    two corresponding subclasses exist:

      * :class:`trepr.dataset.ExperimentalDataset`
      * :class:`trepr.dataset.CalculatedDataset`

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.dataset.Dataset` class for
    details.

    """


class ExperimentalDataset(aspecd.dataset.ExperimentalDataset):
    """Entity consisting of experimental data and metadata.

    On the one hand this class extends the metadata contained in the metadata
    property. On the other hand this class extends the dataset by further
    :class:`aspecd.dataset.Data` objects containing additional variable
    parameters with independent axes useful for further analysis.

    Attributes
    ----------
    metadata : :class:`trepr.dataset.ExperimentalDatasetMetadata`
        Metadata of dataset.

    time_stamp : :class:`aspecd.dataset.Data`
        Time stamp of each individual time trace.

        Note: actual time stamp data will not be available for each file format.

    microwave_frequency : :class:`aspecd.dataset.Data`
        Microwave frequency of each individual time trace.

        Note: actual frequency data will not be available for each file format.

    """

    def __init__(self):
        super().__init__()
        # public properties
        self.metadata = ExperimentalDatasetMetadata()
        self.time_stamp = aspecd.dataset.Data()
        self.microwave_frequency = aspecd.dataset.Data()


class CalculatedDataset(aspecd.dataset.CalculatedDataset):
    """Entity consisting of calculated data and metadata.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.dataset.CalculatedDataset`
    class for details.

    """


class DatasetFactory(aspecd.dataset.DatasetFactory):
    """
    Factory for creating dataset objects based on the source provided.

    Particularly in case of recipe-driven data analysis (c.f. :mod:`tasks`),
    there is a need to automatically retrieve datasets using nothing more
    than a source string that can be, e.g., a path or LOI.

    Attributes
    ----------
    importer_factory : :class:`trepr.io.DatasetImporterFactory`
        ImporterFactory instance used for importing datasets

    """

    def __init__(self):
        super().__init__()
        self.importer_factory = trepr.io.DatasetImporterFactory()

    @staticmethod
    def _create_dataset(source=''):
        return trepr.dataset.ExperimentalDataset()


class ExperimentalDatasetMetadata(aspecd.metadata.ExperimentalDatasetMetadata):
    """Metadata for an experimental TREPR dataset.

    Each attribute is an instance of the respective subclass. For details of
    the attributes of these classes, see their respective documentation.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.

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

    video_amplifier : :obj:`trepr.dataset.VideoAmplifier`
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


class CalculatedDatasetMetadata(aspecd.metadata.CalculatedDatasetMetadata):
    """Metadata for a calculated dataset."""


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
    field_probe_type : str
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

    occurrence : int
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
