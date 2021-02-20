trepr documentation
===================

Welcome! This is the documentation for trepr, a Python package for processing and analysis of time-resolved electron paramagnetic resonance (tr-EPR) spectra based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.trepr.de/>`_. Due to the inheritance from the ASpecD framework, all data generated with the trepr package are completely reproducible and have a complete history.


Features
--------

- fully reproducible processing of TREPR data
- customisable plots
- automatically generated reports
- recipe-driven usage

And to make it even more convenient for users and future-proof:

- Open source project written in Python (>= 3.5)
- Extensive user and API documentation


.. warning::
  The trepr package is currently under active development and still considered in Beta development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Where to start
--------------

Users new to the trepr package should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining frequent :doc:`use cases <usecases>`.

The :doc:`API documentation <api/index>` is the definite source of information for developers, besides having a look at the source code.


Installation
------------

Install the package by running::

    pip install trepr

Contribute
----------

- Source Code: https://github.com/tillbiskup/trepr

License
-------

The project licensed under the BSD license.


A note on the logo
------------------

The snake (a python) resembles the lines of a tr-EPR spectrum, most probably a light-induced spin-polarised triplet state. The copyright of the logo belongs to J. Popp.


.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   concepts
   usecases


.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   developers
   roadmap
   api/index


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`

