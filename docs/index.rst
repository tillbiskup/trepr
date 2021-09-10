.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4897112.svg
   :target: https://doi.org/10.5281/zenodo.4897112
   :align: right

trEPR documentation
===================

Welcome! This is the documentation for trEPR, a Python package for **processing and analysis of time-resolved electron paramagnetic resonance (tr-EPR) spectra** based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.trepr.de/>`_. Due to the inheritance from the ASpecD framework, all data generated with the trepr package are completely reproducible and have a complete history.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at the following example:


.. code-block:: yaml
    :linenos:

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


Interested in more real-live examples? Check out the :doc:`use cases section <usecases>`.


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


.. _sec-how_to_cite:

How to cite
-----------

trepr is free software. However, if you use trepr for your own research, please cite it appropriately:

Jara Popp, Mirjam Schröder, Till Biskup. trepr (2021). `doi:10.5281/zenodo.4897112 <https://doi.org/10.5281/zenodo.4897112>`_

To make things easier, trepr has a `DOI <https://doi.org/10.5281/zenodo.4897112>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4897112.svg
   :target: https://doi.org/10.5281/zenodo.4897112


Where to start
--------------

Users new to the trepr package should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining frequent :doc:`use cases <usecases>`.

The :doc:`API documentation <api/index>` is the definite source of information for developers, besides having a look at the source code.


Installation
------------

To install the trepr package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install trepr

Have a look at the more detailed :doc:`installation instructions <installing>` as well.


Related projects
----------------

There is a number of related packages users of the trepr package may well be interested in, as they have a similar scope, focussing on spectroscopy and reproducible research.

* `ASpecD <https://docs.aspecd.de/>`_

  A Python framework for the analysis of spectroscopic data focussing on reproducibility and good scientific practice. The framework the trepr package is based on, developed by T. Biskup.

* `cwepr <https://docs.cwepr.de/>`_

  Package for processing and analysing continuous-wave electron paramagnetic resonance (cw-EPR) data, originally implemented by P. Kirchner, developed and maintained by M. Schröder and T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


..
  Contribute
  ----------

  - Source Code: https://github.com/tillbiskup/trepr

License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**. However, if you use the cwepr package for your own research, please cite it appropriately. See :ref:`How to cite <sec-how_to_cite>` for details.


A note on the logo
------------------

The snake (a python) resembles the lines of a tr-EPR spectrum, most probably a light-induced spin-polarised triplet state. The copyright of the logo belongs to J. Popp.


.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   introduction
   concepts
   usecases
   installing


.. toctree::
   :maxdepth: 2
   :caption: tr-EPR Primer:
   :hidden:

   trepr/index
   trepr/setup
   trepr/recording
   trepr/processing
   trepr/analysis


.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   developers
   changelog
   roadmap
   dataset-structure
   api/index

