trepr
=====

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4897112.svg
   :target: https://doi.org/10.5281/zenodo.4897112
   :align: right

trepr is a package for handling data obtained using time-resolved electron paramagnetic resonance (TREPR) spectroscopy. It is based on the `ASpecD framework <https://www.aspecd.de/>`_. Due to inheriting from the ASpecD superclasses, all data generated with the trepr package are completely reproducible and have a complete history.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at the following example::

    format:
      type: ASpecD recipe
      version: '0.2'

    settings:
      default_package: trepr

    datasets:
      - /path/to/first/dataset
      - /path/to/second/dataset

    tasks:
      - kind: processing
        type: PretriggerOffsetCompensation
      - kind: processing
        type: BackgroundCorrection
        properties:
          parameters:
            num_profiles: [10, 10]
      - kind: singleplot
        type: SinglePlotter2D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf

For more general information on the trepr package and for how to use it, see its `documentation <https://doc.trepr.de/>`_.


Features
--------

A list of features:

- Fully reproducible processing of tr-EPR data
- Import and export of data from and to different formats
- Customisable plots
- Automatically generated reports
- Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background and without programming skills

And to make it even more convenient for users and future-proof:

- Open source project written in Python (>= 3.5)
- Extensive user and API documentation


.. warning::
  The trepr package is currently under active development and still considered in Beta development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Target audience
---------------

The trepr package addresses scientists working with TREPR data (both, measured and calculated) on a daily base and concerned with `reproducibility <https://www.reproducible-research.de/>`_. Due to being based on the `ASpecD framework <https://www.aspecd.de/>`_, the trepr package ensures reproducibility and---as much as possible---replicability of data processing, starting from recording data and ending with their final (graphical) representation, e.g., in a peer-reviewed publication. This is achieved by automatically creating a gap-less record of each operation performed on your data. If you do care about reproducibility and are looking for a system that helps you to achieve this goal, the trepr package may well be interesting for you.


Related projects
----------------

There is a number of related packages users of the trepr package may well be interested in, as they have a similar scope, focussing on spectroscopy and reproducible research.

* `ASpecD <https://docs.aspecd.de/>`_

  A Python framework for the analysis of spectroscopic data focussing on reproducibility and good scientific practice. The framework the trepr package is based on, developed by T. Biskup.

* `cwepr <https://docs.cwepr.de/>`_

  Package for processing and analysing continuous-wave electron paramagnetic resonance (cw-EPR) data, originally implemented by P. Kirchner, currently developed and maintained by M. Schröder and T. Biskup.

* `FitPy <https://docs.fitpy.de/>`_

  Framework for the advanced fitting of models to spectroscopic data focussing on reproducibility, developed by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


Installation
------------

Install the package by running::

    pip install trepr


License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.
