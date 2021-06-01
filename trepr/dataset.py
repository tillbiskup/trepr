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
subclasses exist:

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
are the result of more than fifteen years of practical experience. Reproducible
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

Particularly in case of recipe-driven data analysis (c.f. :mod:`aspecd.tasks`),
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

    Particularly in case of recipe-driven data analysis, there is a need to
    automatically retrieve datasets using nothing more than a source string
    that can be, e.g., a path or LOI.

    The DatasetFactory operates in conjunction with a
    :class:`trepr.io.DatasetImporterFactory` to import the actual dataset.
    See the respective class documentation for more details.

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

    The metadata and their structure implemented in this class are one key
    aspect of the trepr package. They provide a unified interface for all
    functionality operating on datasets. Additionally, the metadata and
    their structure are the result of more than fifteen years of practical
    experience. Defining what kind of metadata is important and needs to be
    recorded, together with metadata formats easily writable by the
    experimenters *during* recording the data requires a thorough
    understanding of both, the method and the setup(s) used.

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
    """Metadata for a calculated dataset.

    This class contains the minimal set of metadata for a dataset consisting
    of calculated data, i.e., :class:`trepr.dataset.CalculatedDataset`.

    Metadata of actual datasets should extend this class by adding
    properties that are themselves classes inheriting from
    :class:`aspecd.metadata.Metadata`.

    Metadata can be converted to dict via
    :meth:`aspecd.utils.ToDictMixin.to_dict()`, e.g., for generating
    reports using templates and template engines.
    """


class Measurement(aspecd.metadata.Measurement):
    """Metadata corresponding to the measurement.

    As this class inherits from :class:`aspecd.metadata.Measurement`,
    see the documentation of the parent class for details and the full list
    of inherited attributes.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    label : :class:`str`
        Short description of the measurement.

    """

    def __init__(self, dict_=None):
        # public properties
        self.label = ''
        super().__init__(dict_=dict_)


class Sample(aspecd.metadata.Sample):
    """Metadata corresponding to the sample.

    As this class inherits from :class:`aspecd.metadata.Sample`,
    see the documentation of the parent class for details and the full list
    of inherited attributes.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    description : :class:`str`
        Description of the measured sample.

    solvent : :class:`str`
        Name of the solvent used.

    preparation : :class:`str`
        Short details of the sample preparation.

    tube : :class:`str`
        Type and dimension of the sample tube used.

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

    A transient or time trace is the EPR signal intensity over time for a given
    magnetic field point. A full 2D TREPR dataset usually consists of a
    series of transients for different magnetic field points that are
    sequentially recorded.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    points : :class:`int`
        Number of measuring points.

    length : :obj:`aspecd.metadata.PhysicalQuantity`
        Object of the PhysicalQuantity class from ASpecD.

    trigger_position : :class:`int`
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

    Two parameters are relevant for a TREPR experiment that are not
    contained in other parts of the metadata: Number of runs and the shot
    repetition rate. The latter is determined by the laser system used as
    pump source.

    Note that a TREPR experiment can be understood as a special variant of a
    pump-probe experiment with the laser excitation acting as pump and the
    EPR signal intensity recording as function of time as probe.

    Typical shot repetition rates range from 20 Hz to less than 1 Hz and are
    mostly determined not only by the laser system used but as well by the
    kinetics of the sample investigated. To prevent degradation, the sample
    should be fully returned to its ground state between two excitations.
    The TREPR signal decay can *not* be used as a valid measure of the
    kinetics and the return of the sample to its ground state, as the spin
    polarisation usually decays much faster than the sample returns to its
    ground state.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    runs : :class:`int`
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

    TREPR spectrometers almost always consist of several exchangeable
    components, even if commercially available modular systems (*e.g.*
    Bruker EMX or ELEXSYS) are used. Therefore, the spectrometer model and
    the software (including its version information) need to be recorded.

    All the other components of the (TR)EPR spectrometer, such as magnet
    system, microwave bridge and amplifier, recorder, probehead and laser
    system, as well as the temperature controller have their own respective
    classes containing the necessary information.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    model : :class:`str`
        Model of the spectrometer used.

    software : :class:`str`
        Name and version of the software used.

    """

    def __init__(self, dict_=None):
        # public properties
        self.model = ''
        self.software = ''
        super().__init__(dict_=dict_)


class MagneticField(aspecd.metadata.Metadata):
    """Metadata corresponding to the magnetic field.

    The external magnetic field is a crucial component of EPR spectroscopy,
    and the corresponding metadata contain both, information about the
    settings relevant for the experiment conducted as well as the devices (
    field probe, controller, power supply) used. The latter is crucial,
    as most EPR spectrometers (with the exception of highly integrated
    benchtop devices) are modular and consist of exchangeable components.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    field_probe_type : :class:`str`
        Type of field probe used.

        Usually, a Hall probe will be used, with a somewhat limited
        accuracy. The other option is to use a Teslameter, *i.e.* a small
        NMR device, providing much higher accuracy.

    field_probe_model : :class:`str`
        Model of field probe used.

    start : :obj:`aspecd.metadata.PhysicalQuantity`
        Start of the magnetic field sweep.

    stop: :obj:`aspecd.metadata.PhysicalQuantity`
        End of the magnetic field sweep.

    step : :obj:`aspecd.metadata.PhysicalQuantity`
        Step size of the magnetic field sweep.

    sequence : :class:`str`
        Sequence of field steps, such as "up", "down", "out", or "in".

    controller : :class:`str`
        Model of the controller used.

    power_supply : :class:`str`
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

    When recording TREPR data, the laser excitation typically creates a
    field-independent background signal that needs to be subtracted from the
    data.

    There are different ways of how to measure the background signal. The
    simplest (and most often used) approach is to record sufficient baseline
    at the lower and upper magnetic field range. Other approaches are to
    record the background every Nth time trace and directly subtract this
    background signal in the transient recorder. Both methods have their
    advantages and disadvantages. For details, see the literature.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    field : :obj:`aspecd.metadata.PhysicalQuantity`
        Magnetic field position of background trace.

    occurrence : :class:`int`
        Number of time traces after which a background trace is recorded.

    polarisation: :class:`str`
        Type of background polarisation *i.e.* absorptive or emissive.

        An emissive polarisation is a clear hint that the phase is set 180° off.

    intensity : :obj:`aspecd.metadata.PhysicalQuantity`
        Amplitude of background signal.

        Sometimes, the background signal intensity can be much larger than
        the actual signal intensity, and in this case, the signal shape
        strongly depends on the stability of the setup, as a large
        background intensity gets subtracted. Therefore, knowing the
        background signal intensity is particulary important in case it is
        directly subtracted during data recording.

    """

    def __init__(self, dict_=None):
        # public properties
        self.field = aspecd.metadata.PhysicalQuantity()
        self.occurrence = None
        self.polarisation = ''
        self.intensity = aspecd.metadata.PhysicalQuantity()
        super().__init__(dict_=dict_)


class Bridge(aspecd.metadata.Metadata):
    """Metadata corresponding to the microwave bridge.

    The microwave bridge contains the microwave source and parts of the
    detection system. Therefore, the crucial experimental parameters such as
    attenuation and power, microwave frequency and detection system used are
    contained as well as the description of the devices, *i.e.* the bridge
    itself, its controller, and the frequency counter, as these can be
    different interchangeable components.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    model : :class:`str`
        Model of the microwave bridge used.

    controller : :class:`str`
        Model of the bridge controller used.

    attenuation : :obj:`aspecd.metadata.PhysicalQuantity`
        Attenuation of the microwave power in dB.

        Without knowing the unattenuated source power, the attenuation is a
        rather useless value, although it gets often used, particularly in
        lab jargon. Typical microwave bridges have source powers of 200 mW
        in X-Band, but newer devices sometimes deliver only 150 mW.

    power : :obj:`aspecd.metadata.PhysicalQuantity`
        Output power of the microwave.

        The actual output power of the microwave used for the experiment,
        *i.e.* the source power reduced by the attenuation. Typical values
        are in the range of 20 mW to 20 µW.

    detection : :class:`str`
        Type of the detection used.

        There are two types of detection: diode and mixer. The latter
        usually allows for quadrature detection, *i.e.* detecting both, the
        absorptive and dispersive signal components.

        For the best time resolution, mixer detection in conjunction with a
        video amplifier get used, whereas conventional cw-EPR bridges only
        have diode detection combined with a rather low-bandwidth preamplifier.

    frequency_counter : :class:`str`
        Model of the frequency counter used.

        Depending on the setup used, this can be included in the bridge.
        Otherwise, it will often be a HP device.

    mw_frequency : :obj:`aspecd.metadata.PhysicalQuantity`
        Microwave frequency.

        The actual microwave frequency used for the experiment. Usually,
        this is a scalar number. Depending on the experiment control
        software used, the microwave frequency for each transient will be
        recorded, thus allowing for analysing frequency drifts. This is
        particularly helpful in case of long-running experiments (12+ h).
        By comparing the amplitude of the frequency drift with the field
        step width, the potential impact in the signal shape can be directly
        calculated.

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

    Depending on the detection (diode or mixer), either a low-bandwidth
    preamplifier will be used or a high-bandwidth video amplifier. The
    latter is only true for dedicated transient or pulsed bridges.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    bandwidth : :obj:`aspecd.metadata.PhysicalQuantity`
        Bandwidth of the video amplifier.

        Depending on the specific model, values such as 20, 50, 100, and 200
        dB are typically found. Newer devices have only reduced settings.

        The bandwidth of the amplifier is one of the parameters determining
        the overall time resolution of the system, but higher bandwidth
        usually comes with higher noise levels.

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

    The recorder works as an A/D converter, recording the time-dependent EPR
    signal intensity with high time resolution.

    Typically, digital oscilloscopes are used as transient recorders for
    TREPR spectroscopy. In case of commercially available pulsed EPR setups
    (Bruker ELEXSYS), the SpecJet can be used, basically a digital
    oscilloscope as well.

    Two characteristics of a transient recorder are particularly important:
    the time resolution (determined by the bandwidth and time base), and the
    vertical resolution. While the former is rarely limiting for TREPR
    spectra, the vertical resolution is often rather an issue. While
    stand-alone digital oscilloscopes provided a vertical resolution of 11
    bit already in the 1990s, only with the advent of the Bruker SpecJet III
    the vertical resolution for commercial Bruker spectrometers has
    increased beyond 8 bit. The latter is rather useless for recording TREPR
    data, as it translates to only 256 discrete steps. Having in mind that
    typically, TREPR spectra consist of both, absorptive and emissive signal
    components, this amounts to at most only 128 discrete steps per
    direction in the signal maximum. Therefore, weaker parts of the overall
    signal are usually not well resolved in this case.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    model : :class:`str`
        Model of the recorder used.

    averages : :class:`int`
        Number of accumulations recorded.

        Typically, at least 20, but often several hundreds of accumulations
        are recorded for each individual field point to increase the
        signal-to-noise ratio.

    time_base : :obj:`aspecd.metadata.PhysicalQuantity`
        Time base of the recorder.

        The time base is the time between two data points recorded. The time
        base should be much shorter (by a factor of 5--10) than the inverse
        bandwidth of the slowest component of the signal to faithfully
        digitise the actual signal shape (Nyquist sampling theorem).

        Note: While the time base is part of the time resolution of the
        overall system, usually, the time base of the recorder is not the
        limiting characteristic, but rather either the bandwidth of the
        microwave amplifier or the probehead.

    bandwidth : :obj:`aspecd.metadata.PhysicalQuantity`
        Bandwidth of the recorder.

        Typically, bandwidth and time base are connected. For the bandwidth,
        the same applies that has been said for the time base.

    pretrigger : :obj:`aspecd.metadata.PhysicalQuantity`
        Length of time trace before the actual trigger.

        Transients should never start with the actual laser excitation,
        but rather some time before, in order to allow for compensating for
        DC offsets.

        Note that the trigger point does not necessarily allow for
        determining the true signal rise time, due to the time the
        electrical signal takes to travel through the cables. After all,
        the speed of light translates "only" to 30 cm per nanosecond,
        and with typical cable lengths of several metres, this translates
        well into tens of nanoseconds.

    coupling : :class:`str`
        Type of coupling.

        Usually, this is either DC or AC coupling.

    impedance : :obj:`aspecd.metadata.PhysicalQuantity`
        Impedance of the recorder input channel.

        The impedance setting of the recorder input should match that of the
        output of the detector. Take care of any additional filters or alike
        in the signal pathway that typically change the impedance. While
        microwave bridges usually have 50 Ohm impedance, high-pass filters
        will typically translate this to several kOhm, making it necessary
        to change the impedance of the recorder input channel to 1 MOhm.

    sensitivity : :obj:`aspecd.metadata.PhysicalQuantity`
        Sensitivity of the recorder.

        The sensitivity setting determines the vertical resolution of the
        signal. Therefore, the optimum should be sought after between
        maximum vertical resolution and not clipping the signal.

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

    Often, resonating structures get used in EPR spectroscopy, but as this
    is not always the case, the term "probehead" is more generic.

    In all except of fully integrated benchtop spectrometers, the probehead
    can readily be exchanged. As each probehead has its own characteristics,
    it is crucially important to note at least type and model. The coupling
    (critically or overcoupled) determines the bandwidth of the resonator,
    and in all but pulsed experiments, usually, critical coupling is used.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    type : :class:`str`
        Type of the probehead used.

        There are several different types of probeheads regularly used. For
        resonators, there are, *e.g.*, dielectic and split-ring resonators,
        cylindrical and rectangular cavities. More special would be
        Fabry-Perot and stripline resonators. Sometimes, even resonator-free
        designs are used as probeheads.

    model : str
        Model of the probehead used.

        Commercial probeheads come with a distinct model that goes in here.
        In all other cases, use a short, memorisable, and unique name.

    coupling : :class:`str`
        Type of coupling.

        Usually either critically (default) or overcoupled

    """

    def __init__(self, dict_=None):
        # public properties
        self.type = ''
        self.model = ''
        self.coupling = ''
        super().__init__(dict_=dict_)


class Pump(aspecd.metadata.Metadata):
    """Metadata corresponding to the optical excitation..

    A TREPR experiment can be understood as a special variant of a
    pump-probe experiment with the laser excitation acting as pump and the
    EPR signal intensity recording as function of time as probe.

    This class contains all information necessary to describe the laser
    system used as a pump. This includes, besides wavelength, power,
    and repetition rate, the type of tunable (if any), and filters situated
    within the beam path.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    type : :class:`str`
        Type of the pump used.

        This typically translates to "laser", and it may be extended by the
        actual type of laser (*e.g.*, Nd:YAG).

    model : :class:`str`
        Model of the pump used.

    wavelength : :obj:`aspecd.metadata.PhysicalQuantity`
        Wavelength of the optical excitation.

        Depending on whether a tunable light source (OPO, dye laser) is
        used, this can be either rather discrete wavelengths (the harmonics
        of the fundamental wavelength of the laser used), or specific
        wavelengths (typically with an accuracy of 1 nm).

    power : :obj:`aspecd.metadata.PhysicalQuantity`
        Power of the optical excitation.

        Values are typically in the range of 0.5--5 mJ. Make sure to
        *always* record the laser power, as too high laser powers can damage
        your sample (or even your setup).

        Note that measuring the laser power is typically done outside the
        probehead. Therefore, the actual laser power incident at the sample
        is much less, depending on how well you've focussed/collimated the
        excitation beam as well as on the physical structure of the window
        in the probehead. Often, the window contains a metal grid used to
        prevent moo much micrwove leakage, but reducing the incident laser
        power on the sample further.

    repetition_rate : :obj:`aspecd.metadata.PhysicalQuantity`
        Repetition rate of the optical excitation.

        Typical values range from 20 Hz to <1 Hz. The repetition rate of the
        pump determines the shot repetition rate of the whole experiment.

        The kinetics of the sample investigated is crucial for determining
        the correct repetition rate. To prevent degradation, the sample
        should be fully returned to its ground state between two
        excitations. The TREPR signal decay can *not* be used as a valid
        measure of the kinetics and the return of the sample to its ground
        state, as the spin polarisation usually decays much faster than the
        sample returns to its ground state.

    tunable_type : :class:`str`
        Type of the tunable used.

        Usually, this is eiter "OPO" or "dye laser".

    tunable_model : :class:`str`
        Model of the tunable used.

    tunable_dye : :class:`str`
        Name of Laser dye.

        In case of a dye laser, details of the laser dye used.

    tunable_position : :class:`str`
        Position of the tunable used.

        In case of an OPO, you may provide the position of the stepper motor
        here. Please note that these values can only be used for comparision
        within one setup and one calibration.

    filter : :class:`str`
        Type of the filter(s) used.

        Often, additional filters are placed within the excitation beam.

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

    As this class inherits from :class:`aspecd.metadata.TemperatureControl`,
    see the documentation of the parent class for details and the full list
    of inherited attributes.

    Parameters
    ----------
    dict_ : :class:`dict`
        Dictionary containing fields corresponding to attributes of the class

    Attributes
    ----------
    cryostat : :class:`str`
        Model of the cryostat used.

    cryogen : :class:`str`
        Cryogen used.

        Typically, this is either LN2 (for temperatures down to 80K) or LHe
        (for temperatures down to 4 K)

    """

    def __init__(self, dict_=None):
        # public properties
        self.cryostat = ''
        self.cryogen = ''
        super().__init__(dict_=dict_)
