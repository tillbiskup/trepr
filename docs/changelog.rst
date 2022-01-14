=========
Changelog
=========

This page contains a summary of changes between the official trEPR releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/trepr/commits/master>`_.


Version 0.2.0
=============

Not yet released

**Note:** Starting with this version, cwepr requires **Python >=3.7**


New features
------------

* Importer for Berlin fsc2 format: :class:`trepr.io.Fsc2Importer`
* Importer for Bruker BES3T format: :class:`trepr.io.BES3TImporter`
* :class:`trepr.analysis.MWFrequencyValues` to extract microwave frequency values from a dataset as a new, calculated dataset (e.g., for graphical display)
* :class:`trepr.analysis.MWFrequencyDrift` can return (calculated) datasets
* :class:`trepr.analysis.TimeStampAnalysis` can return (calculated) datasets
* :class:`trepr.processing.TriggerAutodetection` for automatically detecting the trigger position
* :class:`trepr.analysis.TransientNutationFFT` for analysing transient nutations using FFT


Changes
-------

* :class:`trepr.analysis.MWFrequencyDrift` renamed from ``MwFreqAnalysis``


Fixes
-----

* :class:`trepr.processing.BackgroundCorrection` subtracts background
* :class:`trepr.io.TezImporter` gets mapper from package data
* :class:`trepr.io.DatasetImporterFactory` falls back to ASpecD-supported formats if no matching format is found.
* :class:`trepr.analysis.MWFrequencyDrift` returns correct value for ratio of drift to magnetic field axis step width


Version 0.1.0
=============

Released 2021-06-03

* First public release
* Based on ASpecD v.0.2.1
* List of processing steps specific for TREPR data
* List of analysis steps specific for TREPR data
* Importers for different file formats
* Recipe-driven data analysis


Version 0.1.0.dev57
===================

Released 2019-06-15

* First public pre-release on PyPI