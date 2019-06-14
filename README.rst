trepr
=====

trepr is a package for handling data obtained using time-resolved electron paramagnetic resonance (TREPR) spectroscopy. It is based on the `ASpecD framework <https://www.aspecd.de/>`_. Due to inheriting from the ASpecD superclasses, all data generated with the trepr package are completely reproducible and have a complete history.

.. warning::
    The trepr package is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.

The easiest way to use the trepr package is to hand over a yaml file to the trepr caller::

    import trepr
    trepr.Caller('your_yaml_file.yaml')

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

If you are having issues, please contact the package authors.

License
-------

The project licensed under the BSD license.
