.. trepr documentation master file, created by
   sphinx-quickstart on Thu Sep 20 08:59:47 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

trepr documentation
===================

Welcome! This is the documentation for trepr, a Python package for processing and analysis of time-resolved electron paramagnetic resonance (tr-EPR) spectra based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.trepr.de/>`_. Due to the inheritance from the ASpecD superclass, all data generated with the trepr package are completely reproducible and have a complete history.

.. warning::
  The trepr package is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Features
--------

- fully reproducible processing of TREPR data
- customisable plots
- automatically generated reports
- recipe-driven usage

Installation
------------

Install the package by running::

    pip install trepr

Contribute
----------

- Source Code: https://github.com/tillbiskup/trepr

Support
-------

If you are having issues, please contact us under j.popp@gmx.ch

License
-------

The project licensed under the BSD license.


A note on the logo
------------------

The snake (a python) resembles the lines of a tr-EPR spectrum, most probably a light-induced spin-polarised triplet state. The copyright of the logo belongs to J. Popp.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   audience
   concepts
   usecases

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

